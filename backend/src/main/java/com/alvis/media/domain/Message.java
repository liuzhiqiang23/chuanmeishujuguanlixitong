package com.alvis.media.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.io.Serializable;
import java.util.Date;
@Data
@EqualsAndHashCode
@TableName("t_message")
public class Message implements Serializable {

    private static final long serialVersionUID = -3510265139403747341L;

    @TableId(value = "id", type = IdType.AUTO)
    private Integer id;

    private String title;

    private String content;

    private Date createTime;

    private Integer sendUserId;

    private String sendUserName;

    private String sendRealName;

    private Integer receiveUserCount;

    private Integer readCount;

}