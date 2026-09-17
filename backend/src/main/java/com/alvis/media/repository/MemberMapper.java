package com.alvis.media.repository;

import com.alvis.media.domain.Member;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;

/**
 * 会员。
 */
@Mapper
public interface MemberMapper extends BaseMapper<Member> {
}
