package com.alvis.media.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.io.Serializable;
import java.util.Date;

/**
 * 会员（t_member）。一个用户一行，续费就是把 expire_time 往后延。
 */
@Data
@EqualsAndHashCode
@TableName("t_member")
public class Member implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(value = "id", type = IdType.AUTO)
    private Integer id;

    private Integer userId;

    /** 会员等级，目前只有 1 */
    private Integer level;

    private Date expireTime;

    private Date createTime;

    private Date updateTime;
}
