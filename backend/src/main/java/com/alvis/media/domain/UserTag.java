package com.alvis.media.domain;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode
@TableName("t_user_tag")
public class UserTag {

    private Integer userId;

    private Integer tagId;

    private Integer userPropertyFlag;
    private String tagName;

    public String getTagName() {
        return tagName;
    }

    public void setTagName(String tagName) {
        this.tagName = tagName;
    }

    public Integer getUserId() {
        return userId;
    }

    public void setUserId(Integer userId) {
        this.userId = userId;
    }

    public Integer getTagId() {
        return tagId;
    }

    public void setTagId(Integer tagId) {
        this.tagId = tagId;
    }

    public Integer getUserPropertyFlag() {
        return userPropertyFlag;
    }

    public void setUserPropertyFlag(Integer userPropertyFlag) {
        this.userPropertyFlag = userPropertyFlag;
    }
}