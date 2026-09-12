package com.alvis.media.viewmodel.predict;

import lombok.Data;

@Data
public class PredictRequestVM {
    private String model = "lgbm";        // lgbm|rf|lr
    private Double budget;                // 预算（美元）
    private Double popularity;            // 热度 popularity
    private Integer runtime;              // 时长（分钟）
    private String language = "en";       // 原始语言，如 en/zh/ja
    private String status = "Released";   // 状态，如 Released/Rumored
}
