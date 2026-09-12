package com.alvis.media.repository;

import com.alvis.media.domain.VideoTag;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface VideoTagMapper {
    int insert(VideoTag record);

    int insertSelective(VideoTag record);
}