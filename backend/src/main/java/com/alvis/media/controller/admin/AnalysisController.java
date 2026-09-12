package com.alvis.media.controller.admin;

import com.alvis.media.base.BaseApiController;
import com.alvis.media.base.RestResponse;
import com.alvis.media.repository.UserVideoOperationMapper;
import com.alvis.media.repository.VideoInfoMapper;
import com.alvis.media.viewmodel.analysis.AnalysisVM;
import com.alvis.media.viewmodel.analysis.UserAnalysisVM;
import com.alvis.media.viewmodel.analysis.VideoAnalysisVM;
import lombok.AllArgsConstructor;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;

@RestController("AdminAnalysisController")
@RequestMapping(value = "/api/admin/analysis")
@AllArgsConstructor
public class AnalysisController extends BaseApiController {

    private final VideoInfoMapper videoInfoMapper;
    private final UserVideoOperationMapper userVideoOperationMapper;

    @RequestMapping(value = "/overview", method = RequestMethod.POST)
    public RestResponse<AnalysisVM> overview() {
        AnalysisVM vm = new AnalysisVM();
        vm.setGenreDistribution(videoInfoMapper.selectGenreDistribution());
        vm.setYearDistribution(videoInfoMapper.selectYearDistribution());
        vm.setBudgetRevenue(videoInfoMapper.selectBudgetRevenue());
        vm.setRatingDistribution(userVideoOperationMapper.selectRatingDistribution());
        vm.setActiveUsers(userVideoOperationMapper.selectActiveUsers());
        return RestResponse.ok(vm);
    }

    /** 视频(电影)属性维度：类型/年份/预算票房/时长/语言/票房TOP/总体指标 */
    @RequestMapping(value = "/video-overview", method = RequestMethod.POST)
    public RestResponse<VideoAnalysisVM> videoOverview() {
        VideoAnalysisVM vm = new VideoAnalysisVM();
        vm.setStats(videoInfoMapper.selectVideoStats());
        vm.setGenreDistribution(videoInfoMapper.selectGenreDistribution());
        vm.setYearDistribution(videoInfoMapper.selectYearDistribution());
        vm.setBudgetRevenue(videoInfoMapper.selectBudgetRevenuePoints());
        vm.setRuntimeDistribution(videoInfoMapper.selectRuntimeDistribution());
        vm.setLanguageDistribution(videoInfoMapper.selectLanguageDistribution());
        vm.setTopRevenue(videoInfoMapper.selectTopRevenue(10));
        return RestResponse.ok(vm);
    }

    /** 用户(观影行为)属性维度：评分分布/活跃用户/评分次数分布/用户均分分布/总体指标 */
    @RequestMapping(value = "/user-overview", method = RequestMethod.POST)
    public RestResponse<UserAnalysisVM> userOverview() {
        UserAnalysisVM vm = new UserAnalysisVM();
        vm.setStats(userVideoOperationMapper.selectUserStats());
        vm.setRatingDistribution(userVideoOperationMapper.selectRatingDistribution());
        vm.setActiveUsers(userVideoOperationMapper.selectActiveUsers());
        vm.setRatingCountDistribution(userVideoOperationMapper.selectRatingCountDistribution());
        vm.setUserAvgRatingDistribution(userVideoOperationMapper.selectUserAvgRatingDistribution());
        return RestResponse.ok(vm);
    }
}
