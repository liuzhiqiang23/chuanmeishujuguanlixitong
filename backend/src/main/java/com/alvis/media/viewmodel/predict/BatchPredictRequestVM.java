package com.alvis.media.viewmodel.predict;

import lombok.Data;

/** 批量预测请求 */
@Data
public class BatchPredictRequestVM {

    /** 预测条数，默认 1000，上限 5000（服务端还会再兜一次底） */
    private Integer limit = 1000;
}
