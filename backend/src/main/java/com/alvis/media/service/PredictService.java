package com.alvis.media.service;

import com.alvis.media.domain.movie.PredictionLog;
import com.alvis.media.viewmodel.predict.*;
import com.alvis.media.domain.other.PageResult;

/**
 * 票房预测（新数据集 + 最佳模型）：
 * 单片预测、批量预测、算法对比、预测留痕查询。
 */
public interface PredictService {

    /** 单片预测（带 Redis 结果缓存与留痕） */
    PredictResultVM predict(PredictRequestVM req);

    /** 批量预测 test 集，逐条写入 t_prediction_log */
    BatchPredictResultVM batchPredict(int limit);

    /** 读取 metrics.json，返回 8 种算法对比数据 */
    AlgoCompareVM algoCompare();

    /** 预测留痕分页查询 */
    PageResult<PredictLogVM> logs(PredictLogRequestVM req);

    /** 落一条预测留痕（单片预测内部调用） */
    void saveLog(PredictionLog log);
}
