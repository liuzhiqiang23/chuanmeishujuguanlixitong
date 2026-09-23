package com.alvis.media.service.impl;

import com.alvis.media.domain.movie.PredictionLog;
import com.alvis.media.domain.other.PageResult;
import com.alvis.media.repository.PredictionLogMapper;
import com.alvis.media.service.PredictService;
import com.alvis.media.util.PythonRunner;
import com.alvis.media.viewmodel.predict.*;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

/**
 * 票房预测：调用 algorithm/boxoffice_prediction/predict_api.py。
 *
 * 与旧实现的区别（见 docs/04_系统详细设计.md §4.2）：
 *   - 模型离线训练、在线只加载 best_model.joblib，秒级返回（旧实现首次调用会现训，10~30 秒）；
 *   - 未提供的字段由脚本按训练集中位数补齐，响应里回带 imputedFields 提示；
 *   - 新增批量预测（逐条落 t_prediction_log）、算法对比、预测留痕查询；
 *   - Python 调用统一走 PythonRunner，带超时保护。
 */
@Service
public class PredictServiceImpl implements PredictService {

    private static final long SINGLE_TIMEOUT_SECONDS = 20;
    private static final long BATCH_TIMEOUT_SECONDS = 180;
    private static final int BATCH_MAX = 5000;
    private static final int LOG_PAGE_MAX = 50;

    @Value("${system.python.predictScript:}")
    private String predictScript;

    private final StringRedisTemplate redisTemplate;
    private final PredictionLogMapper predictionLogMapper;
    private final PythonRunner pythonRunner;
    private final ObjectMapper om = new ObjectMapper();

    /** 显式构造器：@Value 字段不参与构造注入（用 @AllArgsConstructor 会把 String 也当成 bean 去找） */
    public PredictServiceImpl(StringRedisTemplate redisTemplate,
                              PredictionLogMapper predictionLogMapper,
                              PythonRunner pythonRunner) {
        this.redisTemplate = redisTemplate;
        this.predictionLogMapper = predictionLogMapper;
        this.pythonRunner = pythonRunner;
    }

    @Override
    public PredictResultVM predict(PredictRequestVM req) {
        validate(req);
        String cacheKey = "predict:v2:" + cacheKeyOf(req);
        try {
            String cached = redisTemplate.opsForValue().get(cacheKey);
            if (cached != null) {
                return om.readValue(cached, PredictResultVM.class);
            }
        } catch (Exception ignore) {
            // Redis 不可用时不影响主流程
        }
        try {
            JsonNode root = pythonRunner.runJson(buildArgs(req), SINGLE_TIMEOUT_SECONDS);
            PredictResultVM vm = parse(root);
            saveLog(toLog(req, vm));
            try {
                redisTemplate.opsForValue().set(cacheKey, om.writeValueAsString(vm), 1, TimeUnit.HOURS);
            } catch (Exception ignore) {
            }
            return vm;
        } catch (Exception e) {
            throw new RuntimeException("票房预测服务调用失败: " + e.getMessage(), e);
        }
    }

    @Override
    public BatchPredictResultVM batchPredict(int limit) {
        int count = Math.min(BATCH_MAX, Math.max(1, limit));
        File scriptDir = new File(resolveScript()).getParentFile();
        File csv = new File(new File(scriptDir.getParentFile().getParentFile(), "data/processed"), "test_clean.csv");
        if (!csv.exists()) {
            throw new IllegalStateException("缺少测试集文件 " + csv.getPath() + "，请先运行 preprocess.py");
        }
        File out;
        try {
            out = File.createTempFile("predict_batch_", ".jsonl");
        } catch (IOException e) {
            throw new IllegalStateException("创建批量预测临时文件失败: " + e.getMessage(), e);
        }
        try {
            List<String> args = Arrays.asList(resolveScript(), "--batch", csv.getAbsolutePath(),
                    "--limit", String.valueOf(count), "--out", out.getAbsolutePath());
            JsonNode root = pythonRunner.runJson(args, BATCH_TIMEOUT_SECONDS);

            BatchPredictResultVM vm = new BatchPredictResultVM();
            vm.setTotal(root.path("total").asInt());
            vm.setSeconds(root.hasNonNull("seconds") ? root.get("seconds").asDouble() : null);
            vm.setAvgRevenue(root.hasNonNull("avgRevenue") ? root.get("avgRevenue").asLong() : null);
            vm.setMinRevenue(root.hasNonNull("minRevenue") ? root.get("minRevenue").asLong() : null);
            vm.setMaxRevenue(root.hasNonNull("maxRevenue") ? root.get("maxRevenue").asLong() : null);
            vm.setLogRows(persistBatchResult(out, root.path("model").asText("best_model")));
            return vm;
        } catch (Exception e) {
            throw new RuntimeException("批量预测失败: " + e.getMessage(), e);
        } finally {
            if (out.exists() && !out.delete()) {
                out.deleteOnExit();
            }
        }
    }

    @Override
    public AlgoCompareVM algoCompare() {
        File metricsFile = new File(new File(resolveScript()).getParentFile(), "metrics.json");
        if (!metricsFile.exists()) {
            throw new IllegalStateException("未找到算法指标文件 " + metricsFile.getPath() + "，请先运行 train_all.py");
        }
        try {
            JsonNode root = om.readTree(metricsFile);
            AlgoCompareVM vm = new AlgoCompareVM();
            vm.setBest(root.path("best").asText(""));
            vm.setFigure("/algo-figures/algo_comparison.png");
            vm.setNFeatures(root.path("n_features").asInt());
            vm.setNTrain(root.path("n_train").asInt());
            vm.setNVal(root.path("n_val").asInt());
            List<AlgoCompareVM.AlgoMetricVM> list = new ArrayList<>();
            for (JsonNode node : root.path("algorithms")) {
                AlgoCompareVM.AlgoMetricVM item = new AlgoCompareVM.AlgoMetricVM();
                item.setName(node.path("name").asText());
                item.setRmse(node.hasNonNull("rmse") ? node.get("rmse").asDouble() : null);
                item.setMae(node.hasNonNull("mae") ? node.get("mae").asDouble() : null);
                item.setR2(node.hasNonNull("r2") ? node.get("r2").asDouble() : null);
                item.setFitSeconds(node.hasNonNull("fit_seconds") ? node.get("fit_seconds").asDouble() : null);
                list.add(item);
            }
            vm.setAlgorithms(list);
            return vm;
        } catch (IOException e) {
            throw new IllegalStateException("读取算法指标失败: " + e.getMessage(), e);
        }
    }

    @Override
    public PageResult<PredictLogVM> logs(PredictLogRequestVM req) {
        int pageIndex = Math.max(1, req.getPageIndex());
        int pageSize = Math.min(LOG_PAGE_MAX, Math.max(1, req.getPageSize()));
        PageInfo<PredictLogVM> info = PageHelper.startPage(pageIndex, pageSize)
                .doSelectPageInfo(() -> predictionLogMapper.selectLogPage(req.getMovieId()));
        return new PageResult<>(info.getTotal(), pageIndex, pageSize, info.getList());
    }

    @Override
    public void saveLog(PredictionLog log) {
        predictionLogMapper.insert(log);
    }

    private void validate(PredictRequestVM req) {
        if (!StringUtils.hasText(req.getModel())) {
            req.setModel("best");
        }
        if (req.getBudget() == null || req.getBudget() < 0) {
            throw new IllegalArgumentException("请填写有效的预算（非负数）");
        }
        if (req.getRuntime() == null || req.getRuntime() <= 0) {
            throw new IllegalArgumentException("请填写有效的时长（分钟）");
        }
        if (!StringUtils.hasText(req.getLanguage())) {
            req.setLanguage("en");
        }
        if (!StringUtils.hasText(req.getStatus())) {
            req.setStatus("Released");
        }
    }

    private List<String> buildArgs(PredictRequestVM req) {
        List<String> args = new ArrayList<>();
        args.add(resolveScript());
        args.add("--model");
        args.add(req.getModel());
        args.add("--budget");
        args.add(String.valueOf(req.getBudget()));
        args.add("--runtime");
        args.add(String.valueOf(req.getRuntime()));
        args.add("--language");
        args.add(req.getLanguage().trim());
        args.add("--status");
        args.add(req.getStatus().trim());
        if (req.getPopularity() != null && req.getPopularity() > 0) {
            args.add("--popularity");
            args.add(String.valueOf(req.getPopularity()));
        }
        if (StringUtils.hasText(req.getGenres())) {
            args.add("--genres");
            args.add(req.getGenres().trim());
        }
        if (req.getReleaseMonth() != null) {
            args.add("--release-month");
            args.add(String.valueOf(req.getReleaseMonth()));
        }
        if (req.getYear() != null) {
            args.add("--year");
            args.add(String.valueOf(req.getYear()));
        }
        if (req.getVoteAverage() != null) {
            args.add("--vote-average");
            args.add(String.valueOf(req.getVoteAverage()));
        }
        if (req.getVoteCount() != null) {
            args.add("--vote-count");
            args.add(String.valueOf(req.getVoteCount()));
        }
        return args;
    }

    private PredictResultVM parse(JsonNode root) throws IOException {
        PredictResultVM vm = new PredictResultVM();
        vm.setModel(root.path("model").asText("best_model"));
        vm.setPrediction(root.hasNonNull("prediction") ? root.get("prediction").asLong() : null);
        vm.setCurrency(root.path("currency").asText("USD"));
        vm.setLogRevenue(root.hasNonNull("logRevenue") ? root.get("logRevenue").asDouble() : null);
        JsonNode range = root.path("range");
        if (range.isObject()) {
            PredictResultVM.RangeVM rangeVM = new PredictResultVM.RangeVM();
            rangeVM.setLow(range.hasNonNull("low") ? range.get("low").asLong() : null);
            rangeVM.setHigh(range.hasNonNull("high") ? range.get("high").asLong() : null);
            vm.setRange(rangeVM);
        }
        if (root.hasNonNull("metrics")) {
            vm.setMetrics(om.convertValue(root.get("metrics"), new TypeReference<Map<String, Double>>() {
            }));
        }
        vm.setTrainedNow(root.path("trainedNow").asBoolean(false));
        List<String> imputed = new ArrayList<>();
        for (JsonNode node : root.path("imputedFields")) {
            imputed.add(node.asText());
        }
        vm.setImputedFields(imputed);
        vm.setNote(root.path("note").asText(""));
        return vm;
    }

    /** 把批量结果文件逐条写入 t_prediction_log，返回落库条数 */
    private int persistBatchResult(File jsonl, String modelName) throws IOException {
        int rows = 0;
        try (BufferedReader reader = Files.newBufferedReader(jsonl.toPath(), StandardCharsets.UTF_8)) {
            String line;
            while ((line = reader.readLine()) != null) {
                if (line.trim().isEmpty()) {
                    continue;
                }
                JsonNode node = om.readTree(line);
                PredictionLog log = new PredictionLog();
                log.setMovieId(node.hasNonNull("movieId") ? node.get("movieId").asLong() : null);
                log.setModelName(modelName);
                log.setPredictedLogRevenue(node.hasNonNull("logRevenue") ? node.get("logRevenue").asDouble() : null);
                log.setPredictedRevenue(node.hasNonNull("prediction") ? node.get("prediction").asLong() : null);
                log.setCreatedAt(new Date());
                predictionLogMapper.insert(log);
                rows++;
            }
        }
        return rows;
    }

    private PredictionLog toLog(PredictRequestVM req, PredictResultVM vm) {
        PredictionLog log = new PredictionLog();
        log.setModelName(vm.getModel());
        log.setPredictedLogRevenue(vm.getLogRevenue());
        log.setPredictedRevenue(vm.getPrediction());
        log.setCreatedAt(new Date());
        try {
            log.setInputFeatures(om.writeValueAsString(req));
        } catch (Exception ignore) {
            log.setInputFeatures(null);
        }
        return log;
    }

    private String cacheKeyOf(PredictRequestVM req) {
        try {
            return om.writeValueAsString(req);
        } catch (Exception e) {
            return req.toString();
        }
    }

    private String resolveScript() {
        if (!StringUtils.hasText(predictScript)) {
            throw new IllegalStateException("未配置 Python 票房预测脚本路径（system.python.predictScript）");
        }
        return new File(predictScript.trim()).getAbsolutePath();
    }
}
