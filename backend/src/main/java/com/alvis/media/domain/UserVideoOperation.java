package com.alvis.media.domain;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.util.Date;

@Data
@EqualsAndHashCode
@TableName("t_user_video_operation")
public class UserVideoOperation extends UserVideoOperationKey {
    private Integer thumbUp;

    private Integer collection;

    private Integer praiseBadReviews;

    private String comment;

    private Date finallyActiveTime;

    private Double rating;

    private String videoName;


}