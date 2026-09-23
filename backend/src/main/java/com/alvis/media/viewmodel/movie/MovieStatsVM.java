package com.alvis.media.viewmodel.movie;

import lombok.Data;

import java.util.List;

/** 影片库数据概览（影片库页头部与预测页类型下拉都用它） */
@Data
public class MovieStatsVM {

    private Long total;

    private Long withRevenue;

    /** [最小年份, 最大年份] */
    private List<Integer> yearRange;

    private Long avgBudget;

    private Long avgRevenue;

    private List<GenreCountVM> genreTop;
}
