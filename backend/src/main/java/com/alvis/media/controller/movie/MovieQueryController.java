package com.alvis.media.controller.movie;

import com.alvis.media.base.BaseApiController;
import com.alvis.media.base.RestResponse;
import com.alvis.media.domain.other.PageResult;
import com.alvis.media.service.MovieQueryService;
import com.alvis.media.viewmodel.movie.MovieDetailVM;
import com.alvis.media.viewmodel.movie.MovieItemVM;
import com.alvis.media.viewmodel.movie.MoviePageRequestVM;
import com.alvis.media.viewmodel.movie.MovieStatsVM;
import lombok.AllArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 影片库接口（新数据集）：分页检索 / 详情 / 数据概览。
 * 契约见 docs/04_系统详细设计.md §5.2 的 I1 / I2 / I3。
 */
@RestController("MovieQueryController")
@RequestMapping(value = "/api/movie")
@AllArgsConstructor
public class MovieQueryController extends BaseApiController {

    private final MovieQueryService movieQueryService;

    @PostMapping("/page")
    public RestResponse<PageResult<MovieItemVM>> page(@RequestBody MoviePageRequestVM req) {
        return RestResponse.ok(movieQueryService.page(req));
    }

    @GetMapping("/detail/{id}")
    public RestResponse<MovieDetailVM> detail(@PathVariable("id") Long id) {
        return RestResponse.ok(movieQueryService.detail(id));
    }

    @GetMapping("/stats")
    public RestResponse<MovieStatsVM> stats() {
        return RestResponse.ok(movieQueryService.stats());
    }
}
