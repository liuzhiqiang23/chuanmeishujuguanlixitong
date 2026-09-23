package com.alvis.media.service.impl;

import com.alvis.media.repository.MovieMapper;
import com.alvis.media.service.RecommendService;
import com.alvis.media.util.PythonRunner;
import com.alvis.media.viewmodel.recommend.RecommendItemVM;
import com.alvis.media.viewmodel.recommend.RecommendRequestVM;
import com.alvis.media.viewmodel.recommend.RecommendResultVM;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.io.File;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

/**
 * 智能推荐：调用 algorithm/movie_recommendation/recommend_api.py。
 *
 * 数据源是新数据集（不再是已按作业要求删除的 MovieLens），三种策略：
 *   similar    给参考影片 → 内容相似（类型/关键词/演职员/公司/国家加权余弦）
 *   genre_hot  给类型 → 该类型热门（热度与评分人数加权）
 *   站内评分加权：当前用户给过 7 分以上的影片，其类型会作为加权项传给脚本（策略 C）
 */
@Service
public class RecommendServiceImpl implements RecommendService {

    private static final long TIMEOUT_SECONDS = 30;
    private static final int TOP_MAX = 30;
    private static final int BOOST_LIMIT = 5;
    /** 站内评分加权的最低分（>=7 视为“喜欢”） */
    private static final double BOOST_MIN_SCORE = 7.0;

    @Value("${system.python.script:}")
    private String scriptPath;

    private final StringRedisTemplate redisTemplate;
    private final MovieMapper movieMapper;
    private final PythonRunner pythonRunner;
    private final ObjectMapper om = new ObjectMapper();

    /** 显式构造器：@Value 字段不参与构造注入（用 @AllArgsConstructor 会把 String 也当成 bean 去找） */
    public RecommendServiceImpl(StringRedisTemplate redisTemplate,
                                MovieMapper movieMapper,
                                PythonRunner pythonRunner) {
        this.redisTemplate = redisTemplate;
        this.movieMapper = movieMapper;
        this.pythonRunner = pythonRunner;
    }

    @Override
    public RecommendResultVM recommend(RecommendRequestVM req) {
        String strategy = resolveStrategy(req);
        int topN = Math.min(TOP_MAX, Math.max(1, req.getTopN() == null ? 10 : req.getTopN()));
        List<String> boostGenres = loadBoostGenres(req.getUserId());

        String cacheKey = "recommend:v2:" + strategy + ":"
                + ("genre_hot".equals(strategy) ? req.getGenre().trim() : req.getMovieId())
                + ":" + topN + ":" + String.join(",", boostGenres);
        try {
            String cached = redisTemplate.opsForValue().get(cacheKey);
            if (cached != null) {
                return om.readValue(cached, RecommendResultVM.class);
            }
        } catch (Exception ignore) {
            // Redis 不可用不影响主流程
        }
        try {
            JsonNode root = pythonRunner.runJson(buildArgs(strategy, req, topN, boostGenres), TIMEOUT_SECONDS);
            RecommendResultVM vm = parse(root);
            try {
                redisTemplate.opsForValue().set(cacheKey, om.writeValueAsString(vm), 1, TimeUnit.HOURS);
            } catch (Exception ignore) {
            }
            return vm;
        } catch (Exception e) {
            throw new RuntimeException("推荐服务调用失败: " + e.getMessage(), e);
        }
    }

    /** 缺省策略：有 movieId 走相似影片，有 genre 走类型热门 */
    private String resolveStrategy(RecommendRequestVM req) {
        String strategy = req.getStrategy();
        if (!StringUtils.hasText(strategy)) {
            if (req.getMovieId() != null) {
                strategy = "similar";
            } else if (StringUtils.hasText(req.getGenre())) {
                strategy = "genre_hot";
            } else {
                throw new IllegalArgumentException("请指定 strategy（similar / genre_hot），或提供 movieId / genre");
            }
        }
        if ("similar".equals(strategy) && req.getMovieId() == null) {
            throw new IllegalArgumentException("相似影片推荐需要提供 movieId");
        }
        if ("genre_hot".equals(strategy) && !StringUtils.hasText(req.getGenre())) {
            throw new IllegalArgumentException("类型热门推荐需要提供 genre");
        }
        return strategy;
    }

    /** 策略 C 的输入：当前用户评分 >=7 的影片里出现最多的类型（无评分数据时为空，脚本会自动跳过） */
    private List<String> loadBoostGenres(Integer userId) {
        if (userId == null) {
            return Collections.emptyList();
        }
        try {
            List<String> genres = movieMapper.selectTopGenresByUserRating(userId, BOOST_MIN_SCORE, BOOST_LIMIT);
            return genres == null ? Collections.emptyList() : genres;
        } catch (Exception e) {
            return Collections.emptyList();
        }
    }

    private List<String> buildArgs(String strategy, RecommendRequestVM req, int topN, List<String> boostGenres) {
        List<String> args = new ArrayList<>();
        args.add(resolveScript());
        if ("genre_hot".equals(strategy)) {
            args.add("--genre");
            args.add(req.getGenre().trim());
        } else {
            args.add("--movie");
            args.add(String.valueOf(req.getMovieId()));
        }
        args.add("--top");
        args.add(String.valueOf(topN));
        if (!boostGenres.isEmpty()) {
            args.add("--boost-genres");
            args.add(String.join(",", boostGenres));
        }
        return args;
    }

    private RecommendResultVM parse(JsonNode root) {
        RecommendResultVM vm = new RecommendResultVM();
        vm.setStrategy(root.path("strategy").asText("similar"));
        vm.setSeconds(root.hasNonNull("seconds") ? root.get("seconds").asDouble() : null);
        if (root.path("seed").isObject()) {
            vm.setSeed(om.convertValue(root.get("seed"), new TypeReference<Map<String, Object>>() {
            }));
        }
        List<RecommendItemVM> items = new ArrayList<>();
        for (JsonNode node : root.path("items")) {
            RecommendItemVM item = new RecommendItemVM();
            item.setMovieId(node.hasNonNull("movieId") ? node.get("movieId").asLong() : null);
            item.setTitle(node.path("title").asText(""));
            item.setYear(node.hasNonNull("year") ? node.get("year").asInt() : null);
            item.setPosterPath(node.hasNonNull("posterPath") ? node.get("posterPath").asText() : null);
            item.setScore(node.hasNonNull("score") ? node.get("score").asDouble() : null);
            List<String> reasons = new ArrayList<>();
            for (JsonNode reason : node.path("reasons")) {
                reasons.add(reason.asText());
            }
            item.setReasons(reasons);
            items.add(item);
        }
        vm.setItems(items);
        return vm;
    }

    private String resolveScript() {
        if (!StringUtils.hasText(scriptPath)) {
            throw new IllegalStateException("未配置 Python 推荐脚本路径（system.python.script）");
        }
        return new File(scriptPath.trim()).getAbsolutePath();
    }
}
