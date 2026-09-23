package com.alvis.media.repository;

import com.alvis.media.domain.movie.PredictionLog;
import com.alvis.media.viewmodel.predict.PredictLogVM;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/** 票房预测留痕（t_prediction_log）：写入用 BaseMapper，列表查询联表取影片名 */
@Mapper
public interface PredictionLogMapper extends BaseMapper<PredictionLog> {

    @Select("<script>" +
            "SELECT l.id, l.movie_id AS movieId, m.video_name AS movieTitle, l.model_name AS modelName, " +
            "       l.predicted_log_revenue AS predictedLogRevenue, l.predicted_revenue AS predictedRevenue, " +
            "       l.created_at AS createdAt " +
            "FROM t_prediction_log l LEFT JOIN t_movie m ON m.id = l.movie_id " +
            "<where><if test='movieId != null'> AND l.movie_id = #{movieId}</if></where> " +
            "ORDER BY l.id DESC" +
            "</script>")
    List<PredictLogVM> selectLogPage(@Param("movieId") Long movieId);
}
