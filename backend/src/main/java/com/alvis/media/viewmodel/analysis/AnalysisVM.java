package com.alvis.media.viewmodel.analysis;

import com.alvis.media.domain.other.KeyValue;
import com.alvis.media.domain.VideoInfo;
import lombok.Data;
import java.util.List;

@Data
public class AnalysisVM {
    private List<KeyValue> genreDistribution;   // 类型分布
    private List<KeyValue> yearDistribution;    // 年份分布
    private List<VideoInfo> budgetRevenue;      // 票房vs预算散点
    private List<KeyValue> ratingDistribution;  // 评分分布
    private List<KeyValue> activeUsers;         // TOP 活跃用户
}
