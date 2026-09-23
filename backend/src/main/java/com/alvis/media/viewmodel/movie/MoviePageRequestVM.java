package com.alvis.media.viewmodel.movie;

import lombok.Data;

/** 影片库检索条件（前端「影片库」页） */
@Data
public class MoviePageRequestVM {

    private int pageIndex = 1;

    private int pageSize = 12;

    /** 片名 / 原始片名关键词 */
    private String keyword;

    /** 类型名（英文，如 Animation；对应 t_genre.name） */
    private String genre;

    private Integer yearFrom;

    private Integer yearTo;

    /** 排序字段：popularity | revenue | vote_count | year（服务端做白名单校验） */
    private String sortBy = "popularity";

    /** asc | desc */
    private String sortOrder = "desc";
}
