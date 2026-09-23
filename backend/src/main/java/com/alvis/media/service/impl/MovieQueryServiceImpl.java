package com.alvis.media.service.impl;

import com.alvis.media.domain.movie.Movie;
import com.alvis.media.domain.other.PageResult;
import com.alvis.media.repository.MovieMapper;
import com.alvis.media.repository.PredictionLogMapper;
import com.alvis.media.service.MovieQueryService;
import com.alvis.media.viewmodel.movie.MovieDetailVM;
import com.alvis.media.viewmodel.movie.MovieItemVM;
import com.alvis.media.viewmodel.movie.MoviePageRequestVM;
import com.alvis.media.viewmodel.movie.MovieStatsVM;
import com.alvis.media.viewmodel.predict.PredictLogVM;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 影片库检索实现。
 * 分页按「自己算 count + LIMIT」的方式做（对齐 PageResult 的设计说明，不额外注册分页插件）；
 * 排序字段走白名单，避免把前端参数直接拼进 SQL。
 */
@Service
@AllArgsConstructor
public class MovieQueryServiceImpl implements MovieQueryService {

    /** 允许的排序字段白名单（前端值 → 列名） */
    private static final Map<String, String> SORT_COLUMNS = Map.of(
            "popularity", "popularity",
            "revenue", "revenue",
            "vote_count", "vote_count",
            "year", "year"
    );

    private static final int DETAIL_LOG_LIMIT = 3;
    private static final int DETAIL_KEYWORD_LIMIT = 12;
    private static final int DETAIL_COMPANY_LIMIT = 10;
    private static final int DETAIL_CAST_LIMIT = 10;

    private final MovieMapper movieMapper;
    private final PredictionLogMapper predictionLogMapper;

    @Override
    public PageResult<MovieItemVM> page(MoviePageRequestVM req) {
        int pageIndex = Math.max(1, req.getPageIndex());
        int pageSize = Math.min(48, Math.max(1, req.getPageSize()));

        long total = movieMapper.selectCount(buildWrapper(req));

        String column = SORT_COLUMNS.getOrDefault(
                req.getSortBy() == null ? "popularity" : req.getSortBy(), "popularity");
        boolean asc = "asc".equalsIgnoreCase(req.getSortOrder());
        QueryWrapper<Movie> wrapper = buildWrapper(req)
                .orderBy(true, asc, column)
                .last("LIMIT " + (pageIndex - 1) * pageSize + "," + pageSize);

        List<MovieItemVM> list = movieMapper.selectList(wrapper).stream()
                .map(this::toItem)
                .collect(Collectors.toList());
        return new PageResult<>(total, pageIndex, pageSize, list);
    }

    @Override
    public MovieDetailVM detail(Long id) {
        Movie movie = movieMapper.selectById(id);
        if (movie == null) {
            throw new IllegalArgumentException("未找到影片 id=" + id);
        }
        MovieDetailVM vm = new MovieDetailVM();
        vm.setId(movie.getId());
        vm.setTitle(movie.getVideoName());
        vm.setPosterPath(movie.getPosterPath());
        vm.setYear(movie.getYear());
        vm.setMainGenre(movie.getMainGenre());
        vm.setVoteAverage(movie.getVoteAverage());
        vm.setVoteCount(movie.getVoteCount());
        vm.setPopularity(movie.getPopularity());
        vm.setBudget(movie.getBudget());
        vm.setRevenue(movie.getRevenue());
        vm.setOriginalTitle(movie.getOriginalTitle());
        vm.setRuntime(movie.getRuntime());
        vm.setOriginalLanguage(movie.getOriginalLanguage());
        vm.setIsCollection(movie.getIsCollection() != null && movie.getIsCollection() == 1);
        vm.setOverview(movie.getOverview());
        vm.setGenres(movieMapper.selectGenres(id));
        vm.setKeywords(movieMapper.selectKeywords(id, DETAIL_KEYWORD_LIMIT));
        vm.setCompanies(movieMapper.selectCompanies(id, DETAIL_COMPANY_LIMIT));
        vm.setCountries(movieMapper.selectCountries(id));
        vm.setDirector(movieMapper.selectDirector(id));
        vm.setCast(movieMapper.selectCast(id, DETAIL_CAST_LIMIT));

        List<PredictLogVM> logs = predictionLogMapper.selectLogPage(id);
        vm.setPredictionLog(logs.size() > DETAIL_LOG_LIMIT ? logs.subList(0, DETAIL_LOG_LIMIT) : logs);
        return vm;
    }

    @Override
    public MovieStatsVM stats() {
        MovieStatsVM vm = new MovieStatsVM();
        vm.setTotal(movieMapper.countAll());
        vm.setWithRevenue(movieMapper.countWithRevenue());
        Integer min = movieMapper.minYear();
        Integer max = movieMapper.maxYear();
        vm.setYearRange(Arrays.asList(min == null ? 0 : min, max == null ? 0 : max));
        Double avgBudget = movieMapper.avgBudget();
        Double avgRevenue = movieMapper.avgRevenue();
        vm.setAvgBudget(avgBudget == null ? 0L : avgBudget.longValue());
        vm.setAvgRevenue(avgRevenue == null ? 0L : avgRevenue.longValue());
        vm.setGenreTop(movieMapper.selectGenreTop(15));
        return vm;
    }

    /** 关键词 / 类型 / 年份区间三个筛选条件；类型筛走 EXISTS 子查询（带参占位符，不拼字符串） */
    private QueryWrapper<Movie> buildWrapper(MoviePageRequestVM req) {
        QueryWrapper<Movie> wrapper = new QueryWrapper<>();
        if (StringUtils.hasText(req.getKeyword())) {
            String keyword = req.getKeyword().trim();
            wrapper.and(q -> q.like("video_name", keyword).or().like("original_title", keyword));
        }
        if (StringUtils.hasText(req.getGenre())) {
            wrapper.exists("SELECT 1 FROM t_movie_genre mg JOIN t_genre g ON g.id = mg.genre_id "
                    + "WHERE mg.movie_id = t_movie.id AND g.name = {0}", req.getGenre().trim());
        }
        if (req.getYearFrom() != null) {
            wrapper.ge("year", req.getYearFrom());
        }
        if (req.getYearTo() != null) {
            wrapper.le("year", req.getYearTo());
        }
        return wrapper;
    }

    private MovieItemVM toItem(Movie movie) {
        MovieItemVM vm = new MovieItemVM();
        vm.setId(movie.getId());
        vm.setTitle(movie.getVideoName());
        vm.setPosterPath(movie.getPosterPath());
        vm.setYear(movie.getYear());
        vm.setMainGenre(movie.getMainGenre());
        vm.setVoteAverage(movie.getVoteAverage());
        vm.setVoteCount(movie.getVoteCount());
        vm.setPopularity(movie.getPopularity());
        vm.setBudget(movie.getBudget());
        vm.setRevenue(movie.getRevenue());
        return vm;
    }
}
