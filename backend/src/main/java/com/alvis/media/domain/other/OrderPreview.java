package com.alvis.media.domain.other;

import com.alvis.media.domain.UserCoupon;
import lombok.Data;

import java.io.Serializable;
import java.math.BigDecimal;
import java.util.List;

/**
 * 下单前的「确认订单」预览：前端拿它渲染价格明细和可用券列表。
 */
@Data
public class OrderPreview implements Serializable {

    private static final long serialVersionUID = 1L;

    /** 1 影片 2 会员套餐 */
    private Integer itemType;

    /** 影片 ID，或会员套餐的月数 */
    private Integer itemId;

    private String itemName;

    /** 商品原价 */
    private BigDecimal originalPrice;

    /** 当前用户是不是有效会员 */
    private boolean member;

    /** 会员折扣省下的钱 */
    private BigDecimal memberDiscount;

    /** 打完会员折扣后的价（还没算券） */
    private BigDecimal priceAfterMember;

    /** 这张单能用的券（未使用、没过期、门槛已满足） */
    private List<UserCoupon> usableCoupons;

    /** 最划算的一张券能省多少 */
    private BigDecimal bestCouponDiscount;
}
