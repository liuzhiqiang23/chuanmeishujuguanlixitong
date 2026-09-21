package com.alvis.media.service;

import com.alvis.media.domain.VideoInfo;
import com.alvis.media.domain.other.PageResult;

import java.util.List;
import java.util.Map;

/**
 * 发现页相关：分类导航、搜索、影片删除。
 * 分类直接用项目已有的标签体系（t_tag / t_video_tag），不额外建分类表。
 */
public interface DiscoverService {

    /** 分类导航：取关联影片数 >= minCount 的标签，按影片数倒序 */
    List<Map<String, Object>> listCategories(int minCount, int limit);

    PageResult<VideoInfo> listVideosByTag(Integer tagId, int pageIndex, int pageSize);

    PageResult<VideoInfo> search(String keyword, int pageIndex, int pageSize);

    /** 删除影片，连带清掉标签关联 */
    void deleteVideo(Integer videoId);
}
