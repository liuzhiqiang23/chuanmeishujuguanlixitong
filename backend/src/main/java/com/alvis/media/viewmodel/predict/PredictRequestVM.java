package com.alvis.media.viewmodel.predict;

import lombok.Data;

/**
 * 票房预测表单。字段兼容旧版（model/budget/popularity/runtime/language/status），
 * 新增可选的 genres（主类型）与 releaseMonth（上映月份）。
 */
@Data
public class PredictRequestVM {

    /** 兼容参数：在线预测固定使用最佳模型（随机森林），脚本会在响应中回报实际模型名 */
    private String model = "best";

    /** 预算（美元） */
    private Double budget;

    /** TMDB 热度 */
    private Double popularity;

    /** 时长（分钟） */
    private Integer runtime;

    /** 原始语言，如 en/zh/ja */
    private String language = "en";

    /** 发行状态，如 Released/Rumored */
    private String status = "Released";

    /** 主类型（英文，如 Animation；可空） */
    private String genres;

    /** 上映月份 1~12（可空） */
    private Integer releaseMonth;

    /** 上映年份（可空，缺省用训练集中位年份） */
    private Integer year;

    /** 评分均值（可空，缺省用训练集中位数） */
    private Double voteAverage;

    /** 评分人数（可空，缺省用训练集中位数） */
    private Double voteCount;
}
