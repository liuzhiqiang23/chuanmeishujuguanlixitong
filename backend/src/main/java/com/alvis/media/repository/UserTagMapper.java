package com.alvis.media.repository;

import com.alvis.media.domain.UserTag;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;
@Mapper
public interface UserTagMapper {
    int insert(UserTag record);

    int insertSelective(UserTag record);

    List <UserTag> selectUserTagByUserId(Integer userId);
}