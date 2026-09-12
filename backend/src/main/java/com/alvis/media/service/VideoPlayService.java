package com.alvis.media.service;

import com.alvis.media.domain.VideoPlay;

import java.util.List;

/**
 *@author 奇趣
 */
public interface VideoPlayService extends BaseService<VideoPlay> {
    /**
     * 带条件查询视频数量
     * @param filter
     * @return
     */
    int selectVideoPlayCount(VideoPlay filter );
    /**
     * 带条件查询最佳影片
     * @param filter
     * @return
     */
    String selectBestVideo(VideoPlay filter );

    List<Integer> selectMothCount();
}
