package com.alvis.media.repository;

import com.alvis.media.domain.VideoInfo;
import com.alvis.media.domain.other.KeyValue;
import com.alvis.media.viewmodel.video.VideoPageRequestVM;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

@Mapper
public interface VideoInfoMapper extends MediaBaseMapper <VideoInfo> {


    int deleteByPrimaryKey(Integer videoId);

    int insert(VideoInfo record);

    int insertSelective(VideoInfo record);

    VideoInfo selectByPrimaryKey(Integer videoId);

    int updateByPrimaryKeySelective(VideoInfo record);

    int updateByPrimaryKey(VideoInfo record);
    /**
     * 获取新增视频数量
     * @param filter
     * @return
     */
    int selectNewVideoCount(VideoInfo filter);

    /**
     *get videoId by video url from
     * @param
     * @return
     */
    Integer selectVideoIdByUrl(String videoUrl);


    /**
     * @param requestVM requestVM
     * @return List<VideoInfo>
     */
    List <VideoInfo> videoPage(VideoPageRequestVM requestVM);

    List <VideoInfo> selectHotVideoList();

    List<VideoInfo> selectHeatTop(@Param("limit") Integer limit);
    List<KeyValue> selectGenreDistribution();
    List<KeyValue> selectYearDistribution();
    List<VideoInfo> selectBudgetRevenue();
    List<KeyValue> selectRuntimeDistribution();
    List<KeyValue> selectLanguageDistribution();
    List<VideoInfo> selectTopRevenue(@Param("limit") Integer limit);
    List<Map<String, Object>> selectBudgetRevenuePoints();
    Map<String, Object> selectVideoStats();

    List<VideoInfo> selectAll();

    List<VideoInfo> selectByIds(@Param("ids") List<Integer> ids);
}