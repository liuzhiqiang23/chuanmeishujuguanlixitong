package com.alvis.media.repository;

import com.alvis.media.domain.movie.Movie;
import com.alvis.media.viewmodel.movie.GenreCountVM;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/**
 * 影片库（新数据集 t_movie 及关联表）。
 * 基础 CRUD 走 MyBatis-Plus 的 BaseMapper；关联查询是固定 SQL，用注解写在下面，不单开 XML。
 */
@Mapper
public interface MovieMapper extends BaseMapper<Movie> {

    @Select("SELECT g.name FROM t_movie_genre mg JOIN t_genre g ON g.id = mg.genre_id " +
            "WHERE mg.movie_id = #{movieId} ORDER BY g.id")
    List<String> selectGenres(@Param("movieId") Long movieId);

    @Select("SELECT k.name FROM t_movie_keyword mk JOIN t_keyword k ON k.id = mk.keyword_id " +
            "WHERE mk.movie_id = #{movieId} ORDER BY k.id LIMIT #{limit}")
    List<String> selectKeywords(@Param("movieId") Long movieId, @Param("limit") int limit);

    @Select("SELECT c.name FROM t_movie_company mc JOIN t_company c ON c.id = mc.company_id " +
            "WHERE mc.movie_id = #{movieId} ORDER BY c.id LIMIT #{limit}")
    List<String> selectCompanies(@Param("movieId") Long movieId, @Param("limit") int limit);

    @Select("SELECT n.name FROM t_movie_country mn JOIN t_country n ON n.id = mn.country_id " +
            "WHERE mn.movie_id = #{movieId} ORDER BY n.id")
    List<String> selectCountries(@Param("movieId") Long movieId);

    @Select("SELECT p.name FROM t_movie_crew cr JOIN t_person p ON p.id = cr.person_id " +
            "WHERE cr.movie_id = #{movieId} AND cr.job = 'Director' ORDER BY cr.id LIMIT 1")
    String selectDirector(@Param("movieId") Long movieId);

    @Select("SELECT p.name FROM t_movie_cast cs JOIN t_person p ON p.id = cs.person_id " +
            "WHERE cs.movie_id = #{movieId} ORDER BY cs.cast_order, cs.id LIMIT #{limit}")
    List<String> selectCast(@Param("movieId") Long movieId, @Param("limit") int limit);

    @Select("SELECT COUNT(*) FROM t_movie")
    long countAll();

    @Select("SELECT COUNT(*) FROM t_movie WHERE revenue > 0")
    long countWithRevenue();

    @Select("SELECT MIN(year) FROM t_movie")
    Integer minYear();

    @Select("SELECT MAX(year) FROM t_movie")
    Integer maxYear();

    @Select("SELECT AVG(NULLIF(budget, 0)) FROM t_movie")
    Double avgBudget();

    @Select("SELECT AVG(NULLIF(revenue, 0)) FROM t_movie")
    Double avgRevenue();

    @Select("SELECT g.name AS name, COUNT(*) AS count FROM t_movie_genre mg " +
            "JOIN t_genre g ON g.id = mg.genre_id GROUP BY g.id, g.name " +
            "ORDER BY COUNT(*) DESC LIMIT #{limit}")
    List<GenreCountVM> selectGenreTop(@Param("limit") int limit);

    /**
     * 站内评分加权（推荐策略 C）的输入：某用户评分 >= minScore 的影片里出现最多的类型。
     * t_rating 为空（没人打过分）时返回空列表，推荐脚本会自动跳过加权。
     */
    @Select("SELECT g.name FROM t_rating r " +
            "JOIN t_movie_genre mg ON mg.movie_id = r.movie_id " +
            "JOIN t_genre g ON g.id = mg.genre_id " +
            "WHERE r.user_id = #{userId} AND r.score >= #{minScore} " +
            "GROUP BY g.id, g.name ORDER BY COUNT(*) DESC LIMIT #{limit}")
    List<String> selectTopGenresByUserRating(@Param("userId") Integer userId,
                                             @Param("minScore") double minScore,
                                             @Param("limit") int limit);
}
