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
@TableName("t_video_info")
public class VideoInfo implements Serializable {
    private static final long serialVersionUID = 8114730790884782388L;
    @TableId(value = "video_Id", type = IdType.AUTO)
    private Integer videoId;

    private String videoName;

    private Integer videoCategory;

    private Date createTime;

    private Integer creatorId;

    private Date lastModifyTime;

    private String videoUrl;

    private String originalTitle;

    private String overview;

    private String tagline;

    private Long budget;

    private Long revenue;

    private Double popularity;

    private Double voteAverage;

    private Integer voteCount;

    private Integer runtime;

    private Date releaseDate;

    private String originalLanguage;

    private String posterPath;

    private Double heatScore;

    public Integer getVideoId() {
        return videoId;
    }

    public void setVideoId(Integer videoId) {
        this.videoId = videoId;
    }

    public String getVideoName() {
        return videoName;
    }

    public void setVideoName(String videoName) {
        this.videoName = videoName == null ? null : videoName.trim();
    }

    public Integer getVideoCategory() {
        return videoCategory;
    }

    public void setVideoCategory(Integer videoCategory) {
        this.videoCategory = videoCategory;
    }

    public Date getCreateTime() {
        return createTime;
    }

    public void setCreateTime(Date createTime) {
        this.createTime = createTime;
    }

    public Integer getCreatorId() {
        return creatorId;
    }

    public void setCreatorId(Integer creatorId) {
        this.creatorId = creatorId;
    }

    public Date getLastModifyTime() {
        return lastModifyTime;
    }

    public void setLastModifyTime(Date lastModifyTime) {
        this.lastModifyTime = lastModifyTime;
    }

    public String getVideoUrl() {
        return videoUrl;
    }

    public void setVideoUrl(String videoUrl) {
        this.videoUrl = videoUrl == null ? null : videoUrl.trim();
    }
}