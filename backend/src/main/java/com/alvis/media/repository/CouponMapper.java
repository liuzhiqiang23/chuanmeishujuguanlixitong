package com.alvis.media.repository;

import com.alvis.media.domain.Coupon;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;

/**
 * 优惠券模板。CRUD 直接用 MyBatis-Plus 的 BaseMapper，没有特殊 SQL 就不写 XML。
 */
@Mapper
public interface CouponMapper extends BaseMapper<Coupon> {
}
