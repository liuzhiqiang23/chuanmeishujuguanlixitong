package com.alvis.media.controller;

import com.alvis.media.base.BaseApiController;
import com.alvis.media.base.RestResponse;
import com.alvis.media.service.RecommendService;
import com.alvis.media.viewmodel.recommend.RecommendItemVM;
import com.alvis.media.viewmodel.recommend.RecommendRequestVM;
import lombok.AllArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController("RecommendController")
@RequestMapping(value = "/api/recommend")
@AllArgsConstructor
public class RecommendController extends BaseApiController {

    private final RecommendService recommendService;

    @PostMapping
    public RestResponse<List<RecommendItemVM>> recommend(@RequestBody RecommendRequestVM req) {
        return RestResponse.ok(recommendService.recommend(req));
    }
}
