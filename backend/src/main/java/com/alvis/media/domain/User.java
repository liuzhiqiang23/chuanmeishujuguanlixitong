package com.alvis.media.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.io.Serializable;
import java.util.Date;
import java.util.List;

@Data
@EqualsAndHashCode
@TableName("t_user")
public class User implements Serializable {

    private static final long serialVersionUID = -7797183521247423117L;

    @TableId(value = "id", type = IdType.AUTO)
    private Integer id;

    private String userUuid;

    private String userName;

    private String password;

    private String realName;

    private Integer age;

    private Integer sex;

    private Date birthDay;

    private String job;
    private String city;

    private String phone;

    private Integer role;

    private Integer status;

    private String imagePath;

    private Date createTime;

    private Date modifyTime;

    private Date lastActiveTime;

    private Boolean deleted;

    private String wxOpenId;

    private List <UserTag> userTagList;

    private List <VideoPlay> userPlayList;

    private List <MessageUser> userRecommendList;

    private List <UserVideoOperation> userOperationList;

}
