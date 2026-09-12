package com.alvis.media.service.impl;

import com.alvis.media.service.PredictService;
import com.alvis.media.viewmodel.predict.PredictRequestVM;
import com.alvis.media.viewmodel.predict.PredictResultVM;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

/**
 * 票房预测：调用 Movie-Analysis-master/predict_api.py（模型缓存于 model_cache/，
 * 首次调用自动训练，之后秒级返回）。
 */
@Service
public class PredictServiceImpl implements PredictService {

    @Value("${system.python.path:python}")
    private String pythonPath;
    @Value("${system.python.script:}")
    private String scriptPath;
    @Value("${system.python.predictScript:}")
    private String predictScript;

    private final StringRedisTemplate redisTemplate;
    private final ObjectMapper om = new ObjectMapper();

    public PredictServiceImpl(StringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    @Override
    public PredictResultVM predict(PredictRequestVM req) {
        validate(req);
        String cacheKey = "predict:" + req.getModel() + ":" + req.getBudget() + ":"
                + req.getPopularity() + ":" + req.getRuntime() + ":" + req.getLanguage();
        try {
            String cached = redisTemplate.opsForValue().get(cacheKey);
            if (cached != null) {
                return om.readValue(cached, PredictResultVM.class);
            }
        } catch (Exception ignore) {
        }
        try {
            String json = callPython(req);
            PredictResultVM vm = parse(json);
            try {
                redisTemplate.opsForValue().set(cacheKey, om.writeValueAsString(vm), 1, TimeUnit.HOURS);
            } catch (Exception ignore) {
            }
            return vm;
        } catch (Exception e) {
            throw new RuntimeException("票房预测服务调用失败: " + e.getMessage(), e);
        }
    }

    private void validate(PredictRequestVM req) {
        if (req.getModel() == null || req.getModel().isEmpty()) {
            req.setModel("lgbm");
        }
        List<String> models = Arrays.asList("lr", "knn", "svm", "dt", "rf", "lgbm");
        if (!models.contains(req.getModel())) {
            throw new IllegalArgumentException("model 取值仅支持 lr / knn / svm / dt / rf / lgbm");
        }
        if (req.getBudget() == null || req.getBudget() < 0) {
            throw new IllegalArgumentException("请填写有效的预算（非负数）");
        }
        if (req.getPopularity() == null || req.getPopularity() < 0) {
            req.setPopularity(0.0);
        }
        if (req.getRuntime() == null || req.getRuntime() <= 0) {
            throw new IllegalArgumentException("请填写有效的时长（分钟）");
        }
        if (req.getLanguage() == null || req.getLanguage().trim().isEmpty()) {
            req.setLanguage("en");
        }
        if (req.getStatus() == null || req.getStatus().trim().isEmpty()) {
            req.setStatus("Released");
        }
    }

    private String resolvePredictScript() {
        if (predictScript != null && !predictScript.trim().isEmpty()) {
            return predictScript.trim();
        }
        // 未单独配置时：与 recommend_api.py（system.python.script）同目录下的 predict_api.py
        if (scriptPath != null && !scriptPath.trim().isEmpty()) {
            File parent = new File(scriptPath.trim()).getParentFile();
            if (parent != null) {
                return new File(parent, "predict_api.py").getAbsolutePath();
            }
        }
        throw new IllegalStateException("未配置 Python 票房预测脚本路径（system.python.predictScript）");
    }

    private String callPython(PredictRequestVM req) throws Exception {
        List<String> cmd = new ArrayList<>();
        cmd.add(pythonPath);
        cmd.add(resolvePredictScript());
        cmd.add("--model"); cmd.add(req.getModel());
        cmd.add("--budget"); cmd.add(String.valueOf(req.getBudget()));
        cmd.add("--popularity"); cmd.add(String.valueOf(req.getPopularity()));
        cmd.add("--runtime"); cmd.add(String.valueOf(req.getRuntime()));
        cmd.add("--language"); cmd.add(req.getLanguage().trim());
        cmd.add("--status"); cmd.add(req.getStatus().trim());

        ProcessBuilder pb = new ProcessBuilder(cmd);
        pb.redirectErrorStream(true);
        Process p = pb.start();
        StringBuilder sb = new StringBuilder();
        try (BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream(), StandardCharsets.UTF_8))) {
            String line;
            while ((line = br.readLine()) != null) {
                sb.append(line).append('\n');
            }
        }
        int code = p.waitFor();
        if (code != 0) {
            throw new RuntimeException("python exit " + code + ": " + sb);
        }
        return sb.toString().trim();
    }

    private PredictResultVM parse(String json) throws Exception {
        // python 输出可能混入告警行，只取最后一行非空文本作为 JSON
        String lastLine = json;
        for (String line : json.split("\\r?\\n")) {
            if (!line.trim().isEmpty()) {
                lastLine = line.trim();
            }
        }
        JsonNode root = om.readTree(lastLine);
        if (root.hasNonNull("error")) {
            throw new RuntimeException(root.path("error").asText());
        }
        PredictResultVM vm = new PredictResultVM();
        vm.setModel(root.path("model").asText());
        vm.setPrediction(root.hasNonNull("prediction") ? root.get("prediction").asDouble() : null);
        vm.setCurrency(root.hasNonNull("currency") ? root.path("currency").asText() : "USD");
        vm.setTrainedNow(root.path("trained_now").asBoolean(false));
        Map<String, Double> metrics = new HashMap<>();
        JsonNode m = root.path("metrics");
        for (String k : new String[]{"rmse", "mae", "r2"}) {
            if (m.hasNonNull(k)) {
                metrics.put(k, m.get(k).asDouble());
            }
        }
        vm.setMetrics(metrics);
        return vm;
    }
}
