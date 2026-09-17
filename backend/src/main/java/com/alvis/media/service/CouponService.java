package com.alvis.media.service;

import com.alvis.media.domain.Coupon;
import com.alvis.media.domain.UserCoupon;

import java.math.BigDecimal;
import java.util.List;

/**
 * 优惠券：可领列表、我的券、领券、下单核销、取消订单退券。
 */
public interface CouponService {

    /** 还能领的券（上架的 + 有库存的 + 当前用户没领过的） */
    List<Coupon> available(Integer userId);

    /** 我的券，status 传 null 表示全部 */
    List<UserCoupon> mine(Integer userId, Integer status);

    /**
     * 领券。同一个券模板每人限领 1 张，重复领会抛 IllegalArgumentException。
     */
    UserCoupon receive(Integer userId, Integer couponId);

    /** 这张单能用的券：未使用、未过期、订单金额已到门槛 */
    List<UserCoupon> usableFor(Integer userId, BigDecimal orderAmount);

    /**
     * 下单时核销一张券。校验归属/状态/有效期/门槛，通过后置为已使用并记到订单上。
     *
     * @return 实际抵扣的金额（不会超过订单金额）
     */
    BigDecimal useForOrder(Integer userId, Integer userCouponId, BigDecimal orderAmount, String orderNo);

    /** 取消订单时把券退回去 */
    void restoreByOrderNo(String orderNo);
}
