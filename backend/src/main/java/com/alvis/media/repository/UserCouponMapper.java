package com.alvis.media.repository;

import com.alvis.media.domain.UserCoupon;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;

/**
 * 用户持有的优惠券。
 */
@Mapper
public interface UserCouponMapper extends BaseMapper<UserCoupon> {
}
