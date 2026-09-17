package com.alvis.media.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.io.Serializable;
import java.math.BigDecimal;

/**
 * 订单明细（t_order_item）。
 */
@Data
@EqualsAndHashCode
@TableName("t_order_item")
public class OrderItem implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(value = "id", type = IdType.AUTO)
    private Integer id;

    private Integer orderId;

    private String orderNo;

    /** 1 影片 2 会员套餐 */
    private Integer itemType;

    /** 影片 ID，或会员套餐的月数 */
    private Integer itemId;

    private String itemName;

    private BigDecimal unitPrice;

    private Integer quantity;
}
