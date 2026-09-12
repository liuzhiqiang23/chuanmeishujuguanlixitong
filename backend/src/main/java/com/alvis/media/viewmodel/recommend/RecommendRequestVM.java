package com.alvis.media.viewmodel.recommend;
import lombok.Data;
@Data
public class RecommendRequestVM {
    private String algo;          // demographic|content|keyword|user_knn|movie_knn|svd|usr_movie_knn|knn_svd|usr_keywords
    private Integer userId;       // 后端 t_user.id（含 +10 偏移）
    private String movieTitle;    // 电影名（content/keyword/movie_knn/usr_movie_knn 需要）
    private String keywords;      // 关键词（usr_keywords 需要，空格分隔）
    private Integer top = 10;
}
