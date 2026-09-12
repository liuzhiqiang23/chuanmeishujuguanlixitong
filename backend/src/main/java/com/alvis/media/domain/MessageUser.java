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
@TableName("t_message_user")
public class MessageUser implements Serializable {

    private static final long serialVersionUID = -4042932811802896498L;

    @TableId(value = "id", type = IdType.AUTO)
    private Integer id;

    private Integer messageId;

    private Integer receiveUserId;

    private String receiveUserName;

    private String receiveRealName;

    private Boolean readed;

    private Date createTime;

    private Date readTime;

    private String title;

}
