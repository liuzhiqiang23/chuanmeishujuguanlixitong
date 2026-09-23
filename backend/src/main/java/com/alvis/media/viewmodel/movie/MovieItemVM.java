package com.alvis.media.viewmodel.movie;

import lombok.Data;

/** 影片列表项（海报墙卡片） */
@Data
public class MovieItemVM {

    private Long id;

    private String title;

    private String posterPath;

    private Integer year;

    private String mainGenre;

    private Double voteAverage;

    private Integer voteCount;

    private Double popularity;

    private Long budget;

    private Long revenue;
}
