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
 * 优惠券模板（t_coupon）。满 threshold 减 amount，领取后 valid_days 天内有效。
 */
@Data
@EqualsAndHashCode
@TableName("t_coupon")
public class Coupon implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(value = "id", type = IdType.AUTO)
    private Integer id;

    private String title;

    /** 使用门槛，0 表示无门槛 */
    private BigDecimal threshold;

    /** 抵扣金额 */
    private BigDecimal amount;

    /** 领取后有效天数 */
    private Integer validDays;

    /** 发行总量，0 表示不限量 */
    private Integer totalCount;

    private Integer receivedCount;

    /** 1 上架 0 下架 */
    private Integer status;

    private Date createTime;
}
