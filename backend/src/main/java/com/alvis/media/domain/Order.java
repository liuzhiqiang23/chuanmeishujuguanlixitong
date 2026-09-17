package com.alvis.media.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.io.Serializable;
import java.math.BigDecimal;
import java.util.Date;

/**
 * 订单（t_order）。演示版下单即置为「已支付」（模拟支付成功）；
 * 正式接微信支付时应先落「待支付」，在支付回调里再改成已支付。
 */
@Data
@EqualsAndHashCode
@TableName("t_order")
public class Order implements Serializable {

    private static final long serialVersionUID = 1L;

    /** 待支付 */
    public static final int STATUS_UNPAID = 0;
    /** 已支付 */
    public static final int STATUS_PAID = 1;
    /** 已取消 */
    public static final int STATUS_CANCELED = 2;

    /** 影片观影券 */
    public static final int TYPE_VIDEO = 1;
    /** 会员套餐 */
    public static final int TYPE_MEMBER = 2;

    @TableId(value = "id", type = IdType.AUTO)
    private Integer id;

    private String orderNo;

    private Integer userId;

    /** 1 影片观影券 2 会员套餐 */
    private Integer orderType;

    private String title;

    /** 原价 */
    private BigDecimal totalAmount;

    /** 优惠合计（会员折扣 + 券） */
    private BigDecimal discountAmount;

    /** 实付 */
    private BigDecimal payAmount;

    /** 用了哪张券（t_user_coupon.id） */
    private Integer userCouponId;

    /** 0 待支付 1 已支付 2 已取消 */
    private Integer status;

    private Date createTime;

    private Date payTime;
}
