package com.alvis.media.service;

import com.alvis.media.domain.Order;
import com.alvis.media.domain.OrderItem;
import com.alvis.media.domain.other.OrderPreview;
import com.alvis.media.domain.other.PageResult;

import java.util.List;

/**
 * 订单：预览算价、下单、我的订单、取消。
 */
public interface OrderService {

    /** 确认订单页要的价格明细 + 可用券 */
    OrderPreview previewVideo(Integer userId, Integer videoId);

    OrderPreview previewMember(Integer userId, Integer months);

    /** 下「影片观影券」单。userCouponId 可不传。 */
    Order createVideoOrder(Integer userId, Integer videoId, Integer userCouponId);

    /** 下「会员套餐」单。支付成功后直接开卡/续费。 */
    Order createMemberOrder(Integer userId, Integer months, Integer userCouponId);

    PageResult<Order> page(Integer userId, Integer pageIndex, Integer pageSize);

    /** 取订单，会校验是不是这个用户的单 */
    Order getOwned(Integer userId, String orderNo);

    List<OrderItem> itemsOf(String orderNo);

    /** 取消订单，已支付的按演示退款处理，并把券退回 */
    Order cancel(Integer userId, String orderNo);
}
