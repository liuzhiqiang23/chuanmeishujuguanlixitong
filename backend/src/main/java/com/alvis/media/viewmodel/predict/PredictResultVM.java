package com.alvis.media.viewmodel.predict;

import lombok.Data;

import java.util.List;
import java.util.Map;

/** 单片票房预测结果 */
@Data
public class PredictResultVM {

    private String model;

    /** 预测票房（美元，已从 log 尺度还原） */
    private Long prediction;

    private String currency;

    /** 对数尺度预测值 log10(票房) */
    private Double logRevenue;

    /** 参考区间（10^(ŷ ± 1.96·RMSE)，对数正态近似） */
    private RangeVM range;

    /** 模型验证集指标 rmse / mae / r2 */
    private Map<String, Double> metrics;

    /** 本次调用是否新训练了模型（新实现为离线训练，恒为 false） */
    private Boolean trainedNow;

    /** 未提供、按训练集中位数补齐的字段（提示用户结果不确定性更大） */
    private List<String> imputedFields;

    private String note;

    @Data
    public static class RangeVM {
        private Long low;
        private Long high;
    }
}
