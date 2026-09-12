package com.alvis.media.domain;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.io.Serializable;
import java.util.Date;
@Data
@EqualsAndHashCode
@TableName("t_video_play")
public class VideoPlay implements Serializable {
    private static final long serialVersionUID = -748176435370936535L;

    private Integer videoId;

    private Integer userId;

    private Date lastPlayTime;

    private Integer playTimes;

    private String videoName;

}