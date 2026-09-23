package com.alvis.media.viewmodel.predict;

import lombok.Data;

/** 批量预测汇总（结果已逐条写入 t_prediction_log） */
@Data
public class BatchPredictResultVM {

    /** 参与预测的条数 */
    private Integer total;

    /** 脚本内部耗时（秒） */
    private Double seconds;

    /** 实际落库条数 */
    private Integer logRows;

    private Long avgRevenue;

    private Long minRevenue;

    private Long maxRevenue;
}
