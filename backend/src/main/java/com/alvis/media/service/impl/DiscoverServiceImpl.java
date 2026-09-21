package com.alvis.media.service.impl;

import com.alvis.media.domain.VideoInfo;
import com.alvis.media.domain.other.PageResult;
import com.alvis.media.repository.VideoInfoMapper;
import com.alvis.media.repository.VideoTagMapper;
import com.alvis.media.service.DiscoverService;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Service
@AllArgsConstructor
public class DiscoverServiceImpl implements DiscoverService {

    private final VideoTagMapper videoTagMapper;
    private final VideoInfoMapper videoInfoMapper;

    /** TMDB 标准类型的中文名。用白名单方式过滤：woman director / duringcreditsstinger 那类关键词不是类型，不该出现在分类栏 */
    private static final Map<String, String> GENRE_CN = new LinkedHashMap<>();

    static {
        GENRE_CN.put("Action", "动作");
        GENRE_CN.put("Adventure", "冒险");
        GENRE_CN.put("Animation", "动画");
        GENRE_CN.put("Comedy", "喜剧");
        GENRE_CN.put("Crime", "犯罪");
        GENRE_CN.put("Documentary", "纪录片");
        GENRE_CN.put("Drama", "剧情");
        GENRE_CN.put("Family", "家庭");
        GENRE_CN.put("Fantasy", "奇幻");
        GENRE_CN.put("History", "历史");
        GENRE_CN.put("Horror", "恐怖");
        GENRE_CN.put("Music", "音乐");
        GENRE_CN.put("Mystery", "悬疑");
        GENRE_CN.put("Romance", "爱情");
        GENRE_CN.put("Science Fiction", "科幻");
        GENRE_CN.put("TV Movie", "电视电影");
        GENRE_CN.put("Thriller", "惊悚");
        GENRE_CN.put("War", "战争");
        GENRE_CN.put("Western", "西部");
    }

    @Override
    public List<Map<String, Object>> listCategories(int minCount, int limit) {
        // 多取一些：返回里混着非类型标签，过滤完再截到 limit 个。
        // selectTopTags 已按影片数倒序，过滤后顺序不变。
        List<Map<String, Object>> raw = videoTagMapper.selectTopTags(minCount, limit * 3);
        List<Map<String, Object>> out = new ArrayList<>();
        for (Map<String, Object> row : raw) {
            String en = row.get("tagName") == null ? "" : row.get("tagName").toString();
            String cn = GENRE_CN.get(en);
            if (cn == null) {
                continue;
            }
            row.put("tagNameEn", en);
            row.put("tagName", cn);
            out.add(row);
            if (out.size() >= limit) {
                break;
            }
        }
        return out;
    }

    @Override
    public PageResult<VideoInfo> listVideosByTag(Integer tagId, int pageIndex, int pageSize) {
        int total = videoTagMapper.countVideosByTag(tagId);
        List<VideoInfo> list = videoTagMapper.selectVideosByTag(tagId, (pageIndex - 1) * pageSize, pageSize);
        return new PageResult<>(total, pageIndex, pageSize, list);
    }

    @Override
    public PageResult<VideoInfo> search(String keyword, int pageIndex, int pageSize) {
        int total = videoInfoMapper.countByKeyword(keyword);
        List<VideoInfo> list = videoInfoMapper.searchByKeyword(keyword, (pageIndex - 1) * pageSize, pageSize);
        return new PageResult<>(total, pageIndex, pageSize, list);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void deleteVideo(Integer videoId) {
        videoTagMapper.deleteByVideoId(videoId);
        videoInfoMapper.deleteVideoById(videoId);
        // t_video_play / t_user_video_operation 里的历史行为流水保留：
        // 那是"用户看过什么"的日志，删片不影响；后续 join 不上自然会被忽略。
    }
}
