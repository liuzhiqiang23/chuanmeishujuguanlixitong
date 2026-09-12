package com.alvis.media.viewmodel.predict;

import lombok.Data;

import java.util.Map;

@Data
public class PredictResultVM {
    private String model;                 // 使用的模型 lgbm|rf|lr
    private Double prediction;            // 预测票房（美元）
    private String currency;              // 币种 USD
    private Boolean trainedNow;           // 本次调用是否新训练了模型
    private Map<String, Double> metrics;  // 模型评估指标 rmse/mae/r2（测试集）
}
