package com.alvis.media.viewmodel.analysis;

import com.alvis.media.domain.other.KeyValue;
import lombok.Data;

import java.util.List;
import java.util.Map;

/**
 * 用户(观影行为)属性维度分析结果：
 * 评分分布 / 活跃用户 / 用户评分次数分布 / 用户平均评分分布 / 总体指标
 */
@Data
public class UserAnalysisVM {

    /** 总体指标卡：rating_count、user_count、avg_rating、low_count、high_count */
    private Map<String, Object> stats;

    /** 评分分数分布（1-5 分档人数） */
    private List<KeyValue> ratingDistribution;

    /** 活跃用户 TOP10（评分次数最多） */
    private List<KeyValue> activeUsers;

    /** 用户评分次数分段分布 */
    private List<KeyValue> ratingCountDistribution;

    /** 用户平均评分档位分布（苛刻/宽容程度） */
    private List<KeyValue> userAvgRatingDistribution;
}
