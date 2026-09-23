package com.alvis.media.domain.movie;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.io.Serializable;
import java.util.Date;

/**
 * 票房预测留痕表 t_prediction_log：单片与批量预测都会落一条，
 * 供「预测记录」列表与影片详情页回看。
 */
@Data
@EqualsAndHashCode
@TableName("t_prediction_log")
public class PredictionLog implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(value = "id", type = IdType.AUTO)
    private Integer id;

    /** 关联影片 id（可为空：表单预测的是未入库的新片） */
    private Long movieId;

    private String modelName;

    /** 输入特征快照（JSON 文本） */
    private String inputFeatures;

    private Double predictedLogRevenue;

    private Long predictedRevenue;

    private Date createdAt;
}
