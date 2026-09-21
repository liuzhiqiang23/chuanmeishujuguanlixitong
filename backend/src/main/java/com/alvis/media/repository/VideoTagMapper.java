package com.alvis.media.repository;

import com.alvis.media.domain.VideoInfo;
import com.alvis.media.domain.VideoTag;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

@Mapper
public interface VideoTagMapper {
    int insert(VideoTag record);

    int insertSelective(VideoTag record);

    /** 分类导航：按关联影片数倒序取标签，只保留影片数 >= minCount 的 */
    List<Map<String, Object>> selectTopTags(@Param("minCount") int minCount, @Param("limit") int limit);

    int countVideosByTag(@Param("tagId") Integer tagId);

    List<VideoInfo> selectVideosByTag(@Param("tagId") Integer tagId,
                                      @Param("offset") int offset,
                                      @Param("size") int size);

    int deleteByVideoId(@Param("videoId") Integer videoId);
}
