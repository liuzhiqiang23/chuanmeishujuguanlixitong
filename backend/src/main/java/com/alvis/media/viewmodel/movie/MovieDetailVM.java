package com.alvis.media.viewmodel.movie;

import com.alvis.media.viewmodel.predict.PredictLogVM;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.util.List;

/** 影片详情：主表字段 + 关联信息 + 本站预测留痕 */
@Data
@EqualsAndHashCode(callSuper = true)
public class MovieDetailVM extends MovieItemVM {

    private String originalTitle;

    private Integer runtime;

    private String originalLanguage;

    private Boolean isCollection;

    private String overview;

    private List<String> genres;

    private List<String> keywords;

    private List<String> companies;

    private List<String> countries;

    private String director;

    /** 前 10 位主演（按番位） */
    private List<String> cast;

    private List<PredictLogVM> predictionLog;
}
