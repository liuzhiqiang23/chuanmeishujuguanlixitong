package com.alvis.media.service;

import com.alvis.media.viewmodel.recommend.RecommendRequestVM;
import com.alvis.media.viewmodel.recommend.RecommendResultVM;

/** 智能推荐：基于新数据集的内容相似 / 类型热门 / 站内评分加权 */
public interface RecommendService {

    RecommendResultVM recommend(RecommendRequestVM req);
}
