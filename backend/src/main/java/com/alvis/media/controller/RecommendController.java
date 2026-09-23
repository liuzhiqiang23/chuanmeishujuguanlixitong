package com.alvis.media.controller;

import com.alvis.media.base.BaseApiController;
import com.alvis.media.base.RestResponse;
import com.alvis.media.domain.User;
import com.alvis.media.service.RecommendService;
import com.alvis.media.viewmodel.recommend.RecommendRequestVM;
import com.alvis.media.viewmodel.recommend.RecommendResultVM;
import lombok.AllArgsConstructor;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 智能推荐接口（I7 /api/recommend）。
 * 路径与旧版保持一致以降低前端回归面；当前登录用户由 token 解析，用于站内评分加权。
 */
@RestController("RecommendController")
@RequestMapping(value = "/api/recommend")
@AllArgsConstructor
public class RecommendController extends BaseApiController {

    private final RecommendService recommendService;

    @PostMapping
    public RestResponse<RecommendResultVM> recommend(@RequestBody RecommendRequestVM req) {
        User user = getCurrentUser();
        if (user != null) {
            req.setUserId(user.getId());
        }
        return RestResponse.ok(recommendService.recommend(req));
    }
}
