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
 * 用户持有的优惠券（t_user_coupon）。领券时把券名/门槛/面额抄一份快照，
 * 这样后台改券模板不会影响用户已经领到手的券。
 */
@Data
@EqualsAndHashCode
@TableName("t_user_coupon")
public class UserCoupon implements Serializable {

    private static final long serialVersionUID = 1L;

    /** 未使用 */
    public static final int STATUS_UNUSED = 0;
    /** 已使用 */
    public static final int STATUS_USED = 1;
    /** 已过期 */
    public static final int STATUS_EXPIRED = 2;

    @TableId(value = "id", type = IdType.AUTO)
    private Integer id;

    private Integer userId;

    private Integer couponId;

    private String title;

    private BigDecimal threshold;

    private BigDecimal amount;

    /** 0 未使用 1 已使用 2 已过期 */
    private Integer status;

    private Date receiveTime;

    private Date expireTime;

    private Date useTime;

    /** 用在哪个订单上 */
    private String orderNo;
}
