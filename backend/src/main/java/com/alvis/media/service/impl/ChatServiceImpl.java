package com.alvis.media.service.impl;

import com.alvis.media.domain.ChatFaq;
import com.alvis.media.domain.ChatLog;
import com.alvis.media.domain.VideoInfo;
import com.alvis.media.repository.ChatFaqMapper;
import com.alvis.media.repository.ChatLogMapper;
import com.alvis.media.repository.VideoInfoMapper;
import com.alvis.media.service.ChatService;
import com.alvis.media.viewmodel.chat.ChatReplyVM;
import com.alvis.media.viewmodel.chat.ChatRequestVM;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * AI 客服实现。三步：
 *   1) 检索：FAQ 关键词打分 + t_movie 片名匹配，取 top 资料若干条；
 *   2) 生成：资料拼进 system prompt，调 GLM chat/completions（glm-4-flash 免费）；
 *   3) 兜底：没配 key / 调用失败时，FAQ 直接命中就回 FAQ 答案，否则回固定话术。
 * 每轮问答落 t_chat_log，FAQ 命中数累加，方便后续补知识库。
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ChatServiceImpl implements ChatService {

    private final ChatFaqMapper chatFaqMapper;
    private final ChatLogMapper chatLogMapper;
    private final VideoInfoMapper videoInfoMapper;
    private final ObjectMapper objectMapper;

    /** GLM 开放平台。key 走环境变量 GLM_API_KEY（local_env.cmd 注入），不入库不入 git */
    @Value("${system.chat.api-key:}")
    private String apiKey;

    @Value("${system.chat.model:glm-4-flash}")
    private String model;

    @Value("${system.chat.base-url:https://open.bigmodel.cn/api/paas/v4/chat/completions}")
    private String baseUrl;

    @Value("${system.chat.timeout-ms:20000}")
    private int timeoutMs;

    /** 问题里的虚词/问法词/寒暄词，剔除后剩下的才当影片名检索词。
     *  寒暄词（你好/谢谢…）必须在这里拦掉：否则整词 LIKE 会撞上
     *  《你好呀！亲爱的伦敦》这类片名，垃圾资料混进 prompt。 */
    private static final List<String> NOISE_WORDS = Arrays.asList(
            "请问", "帮我", "我想看", "我想", "给我", "给我讲", "一下", "有没有", "有没有人",
            "怎么样", "怎么", "如何", "什么", "为啥", "为什么", "哪些", "哪个", "能不能",
            "可不可以", "可以吗", "吗", "呢", "啊", "呀", "吧", "了", "的",
            "你好", "您好", "哈喽", "嗨", "谢谢", "多谢", "再见", "你是谁",
            "推荐", "介绍一下", "介绍", "告诉我", "讲讲", "说说", "查询", "搜索", "查找",
            "相关", "系列", "有哪些",
            "评分", "票房", "电影", "影片", "片子", "好看", "值得看", "信息", "资料", "详情", "多长", "时长");

    private static final int MAX_FAQ_REF = 3;
    private static final int MAX_MOVIE_REF = 5;
    private static final int MAX_ANSWER_LEN = 800;

    private HttpClient httpClient;

    private synchronized HttpClient http() {
        if (httpClient == null) {
            httpClient = HttpClient.newBuilder()
                    .connectTimeout(Duration.ofSeconds(10))
                    .build();
        }
        return httpClient;
    }

    @Override
    public ChatReplyVM ask(ChatRequestVM req) {
        long start = System.currentTimeMillis();
        String question = req.getQuestion() == null ? "" : req.getQuestion().trim();
        if (question.isEmpty()) {
            throw new IllegalArgumentException("问题不能为空");
        }

        // ---- 1. 检索 ----
        List<ChatFaq> enabledFaqs = chatFaqMapper.selectList(
                new QueryWrapper<ChatFaq>().eq("enabled", 1));
        List<ChatFaq> hitFaqs = scoreFaq(question, enabledFaqs);
        List<VideoInfo> hitMovies = searchMovies(question);

        List<String> refs = new ArrayList<>();
        StringBuilder knowledge = new StringBuilder();
        for (ChatFaq faq : hitFaqs) {
            knowledge.append("【规则】").append(faq.getQuestion()).append('\n')
                    .append(faq.getAnswer()).append("\n\n");
            refs.add("FAQ#" + faq.getId() + " " + faq.getQuestion());
        }
        for (VideoInfo m : hitMovies) {
            knowledge.append("【影片】").append(movieLine(m)).append('\n');
            refs.add(m.getVideoName());
        }

        // ---- 2. 生成（或 3. 兜底） ----
        String answer;
        String source;
        if (!StringUtils.hasText(apiKey)) {
            answer = fallbackAnswer(hitFaqs);
            source = hitFaqs.isEmpty() ? "failed" : "faq";
        } else {
            try {
                answer = callGlm(question, knowledge.toString());
                source = "glm";
            } catch (Exception e) {
                log.warn("GLM 调用失败，走兜底: {}", e.getMessage());
                answer = fallbackAnswer(hitFaqs);
                source = hitFaqs.isEmpty() ? "failed" : "faq";
            }
        }

        // ---- 落库 ----
        int cost = (int) (System.currentTimeMillis() - start);
        ChatReplyVM vm = new ChatReplyVM();
        vm.setAnswer(answer);
        vm.setSource(source);
        vm.setRefs(refs);
        vm.setCostMs(cost);
        vm.setSuggestions(pickSuggestions(hitFaqs, enabledFaqs));
        saveLog(req.getUserId(), question, answer, source, refs, cost);
        bumpFaqHits(hitFaqs);
        return vm;
    }

    /** FAQ 关键词打分：按命中关键词的**字数**计分（越具体的关键词权重越高，
     *  避免"会员"这类泛词把"开通会员"这类精准条目挤出前排），并列取问法短的优先 */
    private List<ChatFaq> scoreFaq(String question, List<ChatFaq> faqs) {
        record Scored(ChatFaq faq, int score) {}
        return faqs.stream()
                .map(f -> {
                    int s = Arrays.stream(f.getKeywords().split("\\|"))
                            .filter(StringUtils::hasText)
                            .filter(question::contains)
                            .mapToInt(String::length)
                            .sum();
                    return new Scored(f, s);
                })
                .filter(s -> s.score() > 0)
                .sorted(Comparator.<Scored>comparingInt(s -> -s.score())
                        .thenComparing(s -> s.faq().getQuestion().length()))
                .limit(MAX_FAQ_REF)
                .map(Scored::faq)
                .collect(Collectors.toList());
    }

    /** 影片检索：把问题里的问法词剔掉，剩下的片段用现成的 searchByKeyword
     *  （t_video_info 中文名模糊匹配 + 热度倒序，与小程序搜索同源）；
     *  整段匹配不到时降级做 n-gram（长→短）滑动匹配，对付"帮我流浪地球"这种
     *  虚词黏在片名前的情况，某个长度命中就停，避免查询过多。 */
    private List<VideoInfo> searchMovies(String question) {
        Set<String> terms = extractTerms(question);
        LinkedHashSet<Integer> seen = new LinkedHashSet<>();
        List<VideoInfo> out = new ArrayList<>();
        for (String term : terms) {
            if (out.size() >= MAX_MOVIE_REF) break;
            for (String q : candidatesOf(term)) {
                List<VideoInfo> hits = videoInfoMapper.searchByKeyword(
                        q, 0, MAX_MOVIE_REF - out.size());
                for (VideoInfo m : hits) {
                    if (seen.add(m.getVideoId())) {
                        out.add(m);
                    }
                }
                if (!hits.isEmpty()) break; // 该词已命中就不再降级
                if (out.size() >= MAX_MOVIE_REF) break;
            }
        }
        return out;
    }

    /** 匹配候选：先整段，再从长到短的滑动子串。
     *  下限 3 字：2 字子串（宇宙/多少/你好/流浪…）太容易撞进片名里常用词，
     *  曾经把《我们到底知道多少》当成"会员多少钱"的资料、《宇宙追缉令》当成
     *  "漫威宇宙"的答案，模型被垃圾引用带偏，一本正经地胡说。 */
    private List<String> candidatesOf(String term) {
        List<String> out = new ArrayList<>();
        out.add(term);
        int n = term.length();
        if (n >= 4) {
            for (int len = Math.min(6, n - 1); len >= 3; len--) {
                for (int i = 0; i + len <= n; i++) {
                    String sub = term.substring(i, i + len);
                    if (!out.contains(sub)) {
                        out.add(sub);
                    }
                }
            }
        }
        return out;
    }

    /** 按标点切段、剔虚词，剩下的 >=2 字片段作为检索词（保序去重） */
    private Set<String> extractTerms(String question) {
        Set<String> terms = new LinkedHashSet<>();
        for (String seg : question.split("[，。？！,.?! ;；、\\s]+")) {
            String s = seg;
            for (String w : NOISE_WORDS) {
                s = s.replace(w, "");
            }
            if (s.length() >= 2) {
                terms.add(s);
            }
        }
        return terms;
    }

    private String movieLine(VideoInfo m) {
        StringBuilder sb = new StringBuilder(m.getVideoName());
        if (m.getReleaseDate() != null) {
            sb.append("（").append(m.getReleaseDate().getYear() + 1900).append("）");
        }
        if (m.getVoteAverage() != null) sb.append(" 评分:").append(m.getVoteAverage());
        if (m.getRuntime() != null) sb.append(" 片长:").append(m.getRuntime()).append("分钟");
        if (m.getRevenue() != null && m.getRevenue() > 0) {
            sb.append(" 票房:").append(String.format("%.1f亿美元", m.getRevenue() / 1e8));
        }
        if (StringUtils.hasText(m.getOverview())) {
            String ov = m.getOverview().length() > 80 ? m.getOverview().substring(0, 80) + "…" : m.getOverview();
            sb.append(" 简介:").append(ov);
        }
        return sb.toString();
    }

    private String buildSystemPrompt(String knowledge) {
        StringBuilder sb = new StringBuilder();
        sb.append("你是小程序「阿强观影」的客服助手小影，回答关于电影、观影券、会员、优惠券、订单的问题。\n");
        sb.append("规则：\n1.只依据下面的资料回答；资料里没有的信息就直说\"这个我暂时查不到\"，不要编造数字或剧情。\n");
        sb.append("2.回答用中文，口语化、友好，控制在3句话以内，资料里的具体数字（价格/评分/年份）必须原样给出。\n");
        sb.append("3.只服务电影平台相关话题；遇到天气、新闻等无关问题，直接说明\"我只懂电影平台的事\"并引导回影片/购票话题，不要展开反问。\n");
        sb.append("4.列举影片类问题（\"有哪些\"\"推荐\"\"相关电影\"）：只能罗列资料里命中的影片；资料没命中就直说\"平台库里没检索到\"。可以再用你自己的常识补充一两部，但必须明确说那是额外推荐、不一定在平台片库里，绝不许把资料外的片名说成平台在映影片。\n\n");
        sb.append("资料：\n");
        sb.append(knowledge.isEmpty() ? "（本轮没有命中任何资料）" : knowledge);
        return sb.toString();
    }

    /** 调 GLM chat/completions；失败抛异常由上层兜底 */
    private String callGlm(String question, String knowledge) throws Exception {
        ObjectNode body = objectMapper.createObjectNode();
        body.put("model", model);
        body.put("temperature", 0.3);
        body.put("max_tokens", 400);
        ArrayNode messages = body.putArray("messages");
        ObjectNode sys = messages.addObject();
        sys.put("role", "system");
        sys.put("content", buildSystemPrompt(knowledge));
        ObjectNode user = messages.addObject();
        user.put("role", "user");
        user.put("content", question);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl))
                .timeout(Duration.ofMillis(timeoutMs))
                .header("Authorization", "Bearer " + apiKey)
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(objectMapper.writeValueAsString(body), java.nio.charset.StandardCharsets.UTF_8))
                .build();
        HttpResponse<String> resp = http().send(request, HttpResponse.BodyHandlers.ofString());
        if (resp.statusCode() != 200) {
            throw new IllegalStateException("GLM HTTP " + resp.statusCode() + ": "
                    + abbreviate(resp.body(), 200));
        }
        JsonNode root = objectMapper.readTree(resp.body());
        JsonNode content = root.path("choices").path(0).path("message").path("content");
        if (!content.isTextual() || content.asText().isBlank()) {
            throw new IllegalStateException("GLM 返回空内容: " + abbreviate(resp.body(), 200));
        }
        String answer = content.asText().trim();
        return answer.length() > MAX_ANSWER_LEN ? answer.substring(0, MAX_ANSWER_LEN) + "…" : answer;
    }

    /** 兜底：FAQ 命中就回标准答案，否则固定话术 */
    private String fallbackAnswer(List<ChatFaq> hitFaqs) {
        if (!hitFaqs.isEmpty()) {
            return hitFaqs.get(0).getAnswer();
        }
        return "抱歉，小影这会儿联系不上大脑（AI 服务暂不可用），会员、观影券、优惠券的问题可以先看「我的」页面说明，或稍后再问我一次。";
    }

    /** 建议追问：同分类下未命中的其它问法 */
    private List<String> pickSuggestions(List<ChatFaq> hitFaqs, List<ChatFaq> all) {
        Set<String> hitIds = hitFaqs.stream().map(f -> String.valueOf(f.getId())).collect(Collectors.toSet());
        Set<String> cats = hitFaqs.stream().map(ChatFaq::getCategory).collect(Collectors.toSet());
        return all.stream()
                .filter(f -> !hitIds.contains(String.valueOf(f.getId())))
                .filter(f -> cats.isEmpty() || cats.contains(f.getCategory()))
                .map(ChatFaq::getQuestion)
                .limit(3)
                .collect(Collectors.toList());
    }

    private void saveLog(Integer userId, String q, String a, String source, List<String> refs, int cost) {
        try {
            ChatLog logRow = new ChatLog();
            logRow.setUserId(userId);
            logRow.setQuestion(q.length() > 900 ? q.substring(0, 900) : q);
            logRow.setAnswer(a);
            logRow.setSource(source);
            logRow.setRefs(refs.isEmpty() ? null : String.join(",", refs).length() > 480
                    ? String.join(",", refs).substring(0, 480) : String.join(",", refs));
            logRow.setCostMs(cost);
            chatLogMapper.insert(logRow);
        } catch (Exception e) {
            log.warn("chat log 落库失败（不影响回答）: {}", e.getMessage());
        }
    }

    private void bumpFaqHits(List<ChatFaq> hitFaqs) {
        for (ChatFaq faq : hitFaqs) {
            try {
                ChatFaq upd = new ChatFaq();
                upd.setId(faq.getId());
                upd.setHit((faq.getHit() == null ? 0 : faq.getHit()) + 1);
                chatFaqMapper.updateById(upd);
            } catch (Exception e) {
                log.warn("faq hit 累加失败 id={}: {}", faq.getId(), e.getMessage());
            }
        }
    }

    private static String abbreviate(String s, int n) {
        if (s == null) return "";
        return s.length() > n ? s.substring(0, n) + "…" : s;
    }
}
