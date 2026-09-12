package com.alvis.media.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.util.Date;


@Data
@EqualsAndHashCode
@NoArgsConstructor
@TableName("t_user_event_log")
public class UserEventLog implements Serializable {

    private static final long serialVersionUID = -3951198127152024633L;

    public UserEventLog(Integer userId, String userName, String realName, Date createTime) {
        this.userId = userId;
        this.userName = userName;
        this.realName = realName;
        this.createTime = createTime;
    }
    @TableId(value = "id", type = IdType.AUTO)
    private Integer id;

    private Integer userId;

    private String userName;

    private String realName;

    private String content;

    private Date createTime;

}
