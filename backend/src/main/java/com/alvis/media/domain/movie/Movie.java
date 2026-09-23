package com.alvis.media.domain.movie;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.io.Serializable;
import java.util.Date;

/**
 * 电影主表 t_movie —— 新数据集（Kaggle The Movies Dataset 抽样 10000 部）的落地表，
 * 主键沿用 TMDB 电影 id。由 sql/import_movie_dataset.py 从 data/processed 清洗产物导入。
 */
@Data
@EqualsAndHashCode
@TableName("t_movie")
public class Movie implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(value = "id", type = IdType.INPUT)
    private Long id;

    /** 片名（数据集用英文名，字段名沿用框架影片表的命名习惯） */
    private String videoName;

    private String originalTitle;

    private String overview;

    private String tagline;

    private Date releaseDate;

    private Integer year;

    private Integer month;

    /** 时长（分钟） */
    private Integer runtime;

    /** 预算（美元） */
    private Long budget;

    /** 票房（美元）；测试集影片为 0，表示无票房记录 */
    private Long revenue;

    private Double logBudget;

    private Double logRevenue;

    private Double popularity;

    private Double voteAverage;

    private Integer voteCount;

    private String originalLanguage;

    /** 主类型（预处理派生，取 TMDB 类型列表的第一项） */
    private String mainGenre;

    private String status;

    private String homepage;

    /** TMDB 海报相对路径（前端拼 https://image.tmdb.org/t/p/w300） */
    private String posterPath;

    /** 是否系列片 */
    private Integer isCollection;

    private Date createdAt;

    private Date updatedAt;
}
