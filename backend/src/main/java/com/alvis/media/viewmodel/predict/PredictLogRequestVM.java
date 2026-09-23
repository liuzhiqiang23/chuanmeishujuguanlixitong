package com.alvis.media.viewmodel.predict;

import lombok.Data;

/** 预测记录查询（分页，可按影片过滤） */
@Data
public class PredictLogRequestVM {

    private int pageIndex = 1;

    private int pageSize = 10;

    /** 可选：只看某部影片的预测记录 */
    private Long movieId;
}
