package com.alvis.media.viewmodel.predict;

import lombok.Data;

import java.util.Date;

/** 票房预测留痕（t_prediction_log + 影片名） */
@Data
public class PredictLogVM {

    private Integer id;

    private Long movieId;

    /** 影片名（联表 t_movie 取回，未入库影片为空） */
    private String movieTitle;

    private String modelName;

    private Double predictedLogRevenue;

    private Long predictedRevenue;

    private Date createdAt;
}
