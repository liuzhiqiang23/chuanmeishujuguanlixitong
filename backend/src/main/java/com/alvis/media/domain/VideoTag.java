package com.alvis.media.domain;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode
@TableName("t_video_tag")
public class VideoTag {
    private Integer videoId;

    private Integer tagId;

    private Boolean videoPropertyFlag;

    public Integer getVideoId() {
        return videoId;
    }

    public void setVideoId(Integer videoId) {
        this.videoId = videoId;
    }

    public Integer getTagId() {
        return tagId;
    }

    public void setTagId(Integer tagId) {
        this.tagId = tagId;
    }

    public Boolean getVideoPropertyFlag() {
        return videoPropertyFlag;
    }

    public void setVideoPropertyFlag(Boolean videoPropertyFlag) {
        this.videoPropertyFlag = videoPropertyFlag;
    }
}