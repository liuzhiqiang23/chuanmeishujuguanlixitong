package com.alvis.media.service;

import com.alvis.media.domain.VideoInfo;
import com.alvis.media.viewmodel.video.VideoPageRequestVM;
import com.github.pagehelper.PageInfo;

import java.util.List;

/**
 *@author 奇趣
 */
public interface VideoInfoService extends BaseService<VideoInfo> {
    /**
     * 带条件查询视频数量
     *
     * @param filter
     * @return
     */
    int selectNewVideoCount(VideoInfo filter);

    /**
     * @param requestVM requestVM
     * @return PageInfo<VideoInfo>
     */
    PageInfo <VideoInfo> userPage(VideoPageRequestVM requestVM);

    List <VideoInfo> userAnalysis(Integer recommendUserId);

    int insertVideoPlay(String realUrl,Integer userId);

    List <com.alvis.media.domain.VideoPlay> selectVideoPlayByVideoId(Integer videoId);

    int recalculateHeat();

    List <VideoInfo> heatTop(Integer limit);

}