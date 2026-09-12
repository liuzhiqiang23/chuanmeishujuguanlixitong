package com.alvis.media.viewmodel.recommend;
import lombok.Data;
@Data
public class RecommendItemVM {
    private String title;
    private Integer movieId;
    private Double score;
    private Double popularity;
    private Double voteAverage;
    private String posterPath;
}
