package com.alvis.media.service;

import com.alvis.media.domain.other.PageResult;
import com.alvis.media.viewmodel.movie.MovieDetailVM;
import com.alvis.media.viewmodel.movie.MovieItemVM;
import com.alvis.media.viewmodel.movie.MoviePageRequestVM;
import com.alvis.media.viewmodel.movie.MovieStatsVM;

/** 影片库检索（新数据集 t_movie 及关联表） */
public interface MovieQueryService {

    PageResult<MovieItemVM> page(MoviePageRequestVM req);

    MovieDetailVM detail(Long id);

    MovieStatsVM stats();
}
