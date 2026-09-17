package com.alvis.media.repository;

import com.alvis.media.domain.OrderItem;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;

/**
 * 订单明细。
 */
@Mapper
public interface OrderItemMapper extends BaseMapper<OrderItem> {
}
