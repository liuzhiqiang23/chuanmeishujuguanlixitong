package com.alvis.media.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.io.Serializable;
import java.util.Date;

@Data
@EqualsAndHashCode
@TableName("t_user_token")
public class UserToken implements Serializable {

    private static final long serialVersionUID = -2414443061696200360L;

    @TableId(value = "id", type = IdType.AUTO)
    private Integer id;

    private String token;

    private Integer userId;

    private String wxOpenId;

    private Date createTime;

    private Date endTime;

    private String userName;

}