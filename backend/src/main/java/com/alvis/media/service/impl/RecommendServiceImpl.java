package com.alvis.media.service.impl;

import com.alvis.media.domain.VideoInfo;
import com.alvis.media.repository.VideoInfoMapper;
import com.alvis.media.service.RecommendService;
import com.alvis.media.viewmodel.recommend.RecommendItemVM;
import com.alvis.media.viewmodel.recommend.RecommendRequestVM;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

@Service
public class RecommendServiceImpl implements RecommendService {

    @Value("${system.python.path:python}")
    private String pythonPath;
    @Value("${system.python.script:}")
    private String scriptPath;

    private final VideoInfoMapper videoInfoMapper;
    private final StringRedisTemplate redisTemplate;
    private final ObjectMapper om = new ObjectMapper();

    public RecommendServiceImpl(VideoInfoMapper videoInfoMapper, StringRedisTemplate redisTemplate) {
        this.videoInfoMapper = videoInfoMapper;
        this.redisTemplate = redisTemplate;
    }

    @Override
    public List<RecommendItemVM> recommend(RecommendRequestVM req) {
        validate(req);
        String cacheKey = "recommend:" + req.getAlgo() + ":"
                + (req.getUserId() == null ? req.getMovieTitle() : req.getUserId())
                + (req.getKeywords() == null || req.getKeywords().isEmpty() ? "" : ":" + req.getKeywords());
        try {
            String cached = redisTemplate.opsForValue().get(cacheKey);
            if (cached != null) {
                return om.readValue(cached, om.getTypeFactory().constructCollectionType(List.class, RecommendItemVM.class));
            }
        } catch (Exception ignore) {
        }
        try {
            String json = callPython(req);
            List<RecommendItemVM> result = parse(json);
            enrich(result);
            try {
                redisTemplate.opsForValue().set(cacheKey, om.writeValueAsString(result), 1, TimeUnit.HOURS);
            } catch (Exception ignore) {
            }
            return result;
        } catch (Exception e) {
            throw new RuntimeException("推荐服务调用失败: " + e.getMessage(), e);
        }
    }

    /**
     * 参数校验：部分算法强依赖 userId / movieTitle，缺参会直接导致 Python 进程报错退出。
     */
    private void validate(RecommendRequestVM req) {
        String algo = req.getAlgo();
        if (algo == null || algo.isEmpty()) {
            throw new IllegalArgumentException("缺少参数 algo");
        }
        switch (algo) {
            case "user_knn":
            case "svd":
                if (req.getUserId() == null) {
                    throw new IllegalArgumentException("算法 " + algo + " 需要填写用户ID（如 11 = MovieLens 用户1）");
                }
                break;
            case "content":
            case "keyword":
            case "movie_knn":
                if (req.getMovieTitle() == null || req.getMovieTitle().trim().isEmpty()) {
                    throw new IllegalArgumentException("算法 " + algo + " 需要填写电影名（如 The Dark Knight）");
                }
                break;
            case "usr_movie_knn":
                if (req.getUserId() == null) {
                    throw new IllegalArgumentException("算法 " + algo + " 需要填写用户ID（如 11 = MovieLens 用户1）");
                }
                if (req.getMovieTitle() == null || req.getMovieTitle().trim().isEmpty()) {
                    throw new IllegalArgumentException("算法 " + algo + " 需要填写电影名（如 The Dark Knight）");
                }
                break;
            case "knn_svd":
                if (req.getUserId() == null) {
                    throw new IllegalArgumentException("算法 " + algo + " 需要填写用户ID（如 11 = MovieLens 用户1）");
                }
                break;
            case "usr_keywords":
                if (req.getUserId() == null) {
                    throw new IllegalArgumentException("算法 " + algo + " 需要填写用户ID（如 11 = MovieLens 用户1）");
                }
                if (req.getKeywords() == null || req.getKeywords().trim().isEmpty()) {
                    throw new IllegalArgumentException("算法 " + algo + " 需要填写关键词（空格分隔，如 spy hero war army）");
                }
                break;
            default:
                break;
        }
    }

    private String callPython(RecommendRequestVM req) throws Exception {
        List<String> cmd = new ArrayList<>();
        cmd.add(pythonPath);
        cmd.add(scriptPath);
        cmd.add("--algo"); cmd.add(req.getAlgo());
        if (req.getUserId() != null) { cmd.add("--user"); cmd.add(String.valueOf(req.getUserId() - 10)); }
        if (req.getMovieTitle() != null && !req.getMovieTitle().isEmpty()) { cmd.add("--movie"); cmd.add(req.getMovieTitle()); }
        if (req.getKeywords() != null && !req.getKeywords().isEmpty()) { cmd.add("--keywords"); cmd.add(req.getKeywords()); }
        cmd.add("--top"); cmd.add(String.valueOf(req.getTop() == null ? 10 : req.getTop()));

        ProcessBuilder pb = new ProcessBuilder(cmd);
        pb.redirectErrorStream(true);
        Process p = pb.start();
        StringBuilder sb = new StringBuilder();
        try (BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream(), StandardCharsets.UTF_8))) {
            String line;
            // 保留换行符，便于解析时只取最后一行非空 JSON（stderr 合并进来的告警行会被丢弃）
            while ((line = br.readLine()) != null) { sb.append(line).append('\n'); }
        }
        int code = p.waitFor();
        if (code != 0) { throw new RuntimeException("python exit " + code + ": " + sb); }
        String json = sb.toString().trim();
        return json;
    }

    private List<RecommendItemVM> parse(String json) throws Exception {
        // python 输出可能混入 stderr 告警行（Java 端 redirectErrorStream=true），
        // 只取最后一行非空文本作为真正的 JSON 再解析；无内容时照旧走 readTree 抛错
        String lastLine = json;
        for (String line : json.split("\\r?\\n")) {
            if (!line.trim().isEmpty()) {
                lastLine = line.trim();
            }
        }
        JsonNode root = om.readTree(lastLine);
        List<RecommendItemVM> list = new ArrayList<>();
        for (JsonNode n : root.path("movies")) {
            RecommendItemVM item = new RecommendItemVM();
            item.setTitle(n.path("title").asText());
            item.setMovieId(n.hasNonNull("movieId") ? n.get("movieId").asInt() : null);
            item.setScore(n.hasNonNull("score") ? n.get("score").asDouble() : null);
            list.add(item);
        }
        return list;
    }

    private void enrich(List<RecommendItemVM> items) {
        List<Integer> ids = new ArrayList<>();
        for (RecommendItemVM it : items) {
            if (it.getMovieId() != null) ids.add(it.getMovieId());
        }
        if (ids.isEmpty()) return;
        Map<Integer, VideoInfo> map = new HashMap<>();
        for (VideoInfo v : videoInfoMapper.selectByIds(ids)) {
            map.put(v.getVideoId(), v);
        }
        for (RecommendItemVM it : items) {
            VideoInfo v = map.get(it.getMovieId());
            if (v != null) {
                it.setPopularity(v.getPopularity());
                it.setVoteAverage(v.getVoteAverage());
                it.setPosterPath(v.getPosterPath());
            }
        }
    }
}
