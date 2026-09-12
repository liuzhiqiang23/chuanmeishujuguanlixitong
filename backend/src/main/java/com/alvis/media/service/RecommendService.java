package com.alvis.media.service;
import com.alvis.media.viewmodel.recommend.RecommendItemVM;
import com.alvis.media.viewmodel.recommend.RecommendRequestVM;
import java.util.List;
public interface RecommendService {
    List<RecommendItemVM> recommend(RecommendRequestVM req);
}
