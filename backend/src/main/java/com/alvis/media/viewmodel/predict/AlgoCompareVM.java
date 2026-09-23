package com.alvis.media.viewmodel.predict;

import lombok.Data;

import java.util.List;

/** 多算法对比（读 algorithm/boxoffice_prediction/metrics.json，前端「算法对比」页） */
@Data
public class AlgoCompareVM {

    private String best;

    /** 对比图地址（后端 /algo-figures/** 静态映射） */
    private String figure;

    private Integer nFeatures;

    private Integer nTrain;

    private Integer nVal;

    private List<AlgoMetricVM> algorithms;

    @Data
    public static class AlgoMetricVM {
        private String name;
        private Double rmse;
        private Double mae;
        private Double r2;
        private Double fitSeconds;
    }
}
