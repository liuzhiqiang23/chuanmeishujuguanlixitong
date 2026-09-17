package com.alvis.media.repository;

import com.alvis.media.domain.Order;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;

/**
 * 订单。
 */
@Mapper
public interface OrderMapper extends BaseMapper<Order> {
}
