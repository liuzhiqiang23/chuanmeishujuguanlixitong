package com.alvis.media.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.io.Serializable;
import java.util.Date;

/**
 * 分享领券记录。同一对（分享者, 被分享者）只发一次，
 * 表上的 uk_sharer_receiver 唯一索引兜底防刷。
 */
@Data
@TableName("t_coupon_share")
public class CouponShare implements Serializable {
    private static final long serialVersionUID = 1L;

    @TableId(value = "share_id", type = IdType.AUTO)
    private Integer shareId;
    private Integer sharerId;
    private Integer receiverId;
    private Integer couponId;
    private Date createTime;
}
