package com.alvis.media.viewmodel.analysis;

import com.alvis.media.domain.VideoInfo;
import com.alvis.media.domain.other.KeyValue;
import lombok.Data;

import java.util.List;
import java.util.Map;

/**
 * 视频(电影)属性维度分析结果：
 * 类型分布 / 年份分布 / 预算-票房散点 / 时长分布 / 语言分布 / TOP 票房影片 / 总体指标
 */
@Data
public class VideoAnalysisVM {

    /** 总体指标卡：video_count、avg_budget、avg_revenue、avg_vote、avg_runtime、avg_popularity */
    private Map<String, Object> stats;

    /** 类型分布（标签聚合） */
    private List<KeyValue> genreDistribution;

    /** 发行年份分布 */
    private List<KeyValue> yearDistribution;

    /** 预算-票房数据点（散点图，轻量字段：videoName/budget/revenue/popularity/voteAverage） */
    private List<Map<String, Object>> budgetRevenue;

    /** 时长分段分布 */
    private List<KeyValue> runtimeDistribution;

    /** 原始语言分布 TOP10 */
    private List<KeyValue> languageDistribution;

    /** 票房 TOP 影片 */
    private List<VideoInfo> topRevenue;
}
