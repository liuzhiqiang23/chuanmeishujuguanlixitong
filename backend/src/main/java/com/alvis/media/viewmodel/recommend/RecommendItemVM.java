package com.alvis.media.viewmodel.recommend;

import lombok.Data;

import java.util.List;

/** 推荐结果条目：影片信息 + 分值 + 可读理由 */
@Data
public class RecommendItemVM {

    private Long movieId;

    private String title;

    private Integer year;

    private String posterPath;

    /** 相似度（strategy=similar，0~1）或热度分（strategy=genre_hot，z 分数） */
    private Double score;

    /** 推荐理由，如「同类型：动画、冒险」「同导演：John Lasseter」 */
    private List<String> reasons;
}
