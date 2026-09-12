package com.alvis.media.controller;

import com.alvis.media.base.BaseApiController;
import com.alvis.media.base.NonStaticResourceHttpRequestHandler;
import com.alvis.media.base.RestResponse;
import com.alvis.media.domain.*;
import com.alvis.media.service.VideoInfoService;
import com.alvis.media.utility.PageInfoHelper;
import com.alvis.media.viewmodel.video.*;
import com.github.pagehelper.PageInfo;
import lombok.AllArgsConstructor;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.Valid;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

//导包


@RestController("VideoController")
@RequestMapping(value = "/api/admin/video")
@AllArgsConstructor
public class VideoController  extends BaseApiController {

    private  final VideoInfoService videoInfoService;

    @Autowired
    private NonStaticResourceHttpRequestHandler nonStaticResourceHttpRequestHandler;

    @GetMapping("/play/**")
    public void playVideo(HttpServletRequest request, HttpServletResponse response) throws Exception {
        //realPath 即视频所在的完整地址
        String url = request.getRequestURL().toString();
        int index=  url.lastIndexOf("D:");
        String realPath = url.substring(index);

        Path filePath = Paths.get(realPath);
        if (Files.exists(filePath)) {
            // 利用 Files.probeContentType 获取文件类型
            String mimeType = Files.probeContentType(filePath);
            if (!StringUtils.isEmpty(mimeType)) {
                // 设置 response
                response.setContentType(mimeType);
            }
            request.setAttribute(nonStaticResourceHttpRequestHandler.filepath, filePath);
            // 利用 ResourceHttpRequestHandler.handlerRequest() 实现返回视频流
            nonStaticResourceHttpRequestHandler.handleRequest(request, response);
        } else {
            response.setStatus(HttpServletResponse.SC_NOT_FOUND);
            response.setCharacterEncoding(StandardCharsets.UTF_8.toString());
        }
    }

    @RequestMapping(value = "/select/{id}", method = RequestMethod.POST)
    public RestResponse<VideoResponseVM> select(@PathVariable Integer id) {
        VideoInfo video = videoInfoService.selectById(id);
        videoInfoService.insertVideoPlay(video.getVideoUrl(), getCurrentUser().getId());
        video.setVideoUrl("/api/admin/video/play/"+video.getVideoUrl());
        VideoResponseVM videoVm = VideoResponseVM.from(video);
        return RestResponse.ok(videoVm);
    }

    @RequestMapping(value = "/getVideoDetailByVideoId/{id}", method = RequestMethod.POST)
    public RestResponse <VideoDetailVM> getVideoDetailByVideoId(@PathVariable Integer id) {
        VideoInfo video = videoInfoService.selectById(id);
        if (video == null) {
            return new RestResponse<>(404, "视频不存在");
        }
        VideoDetailVM vm = new VideoDetailVM();
        vm.setVideoId(video.getVideoId());
        vm.setVideoName(video.getVideoName());
        vm.setOriginalTitle(video.getOriginalTitle());
        vm.setOverview(video.getOverview());
        vm.setTagline(video.getTagline());
        vm.setVoteAverage(video.getVoteAverage());
        vm.setPopularity(video.getPopularity());
        vm.setReleaseDate(video.getReleaseDate() == null ? null : new java.text.SimpleDateFormat("yyyy-MM-dd").format(video.getReleaseDate()));
        vm.setPosterPath(video.getPosterPath());
        vm.setVideoPlayList(videoInfoService.selectVideoPlayByVideoId(id));
        vm.setVideoOperationList(new ArrayList <>());
        vm.setVideoTagList(new ArrayList <>());
        return RestResponse.ok(vm);
    }

    @RequestMapping(value = "/page/list", method = RequestMethod.POST)
    public RestResponse<PageInfo <VideoResponseVM>> pageList(@RequestBody VideoPageRequestVM model) {
        PageInfo<VideoInfo> pageInfo = videoInfoService.userPage(model);
        PageInfo<VideoResponseVM> page = PageInfoHelper.copyMap(pageInfo, d -> VideoResponseVM.from(d));
        return RestResponse.ok(page);
    }

    @RequestMapping(value = "/create", method = RequestMethod.POST)
    public RestResponse<VideoResponseVM> createVideo(@RequestBody @Valid VideoCreateVM model) {
         //step1 校验视频是否上传 （判断url是否为空）
        if(StringUtils.isBlank(model.getVideoUrl()))
        {
            return RestResponse.fail(500,"视频文件未上传");
        }
        //字段映射
        VideoInfo video = modelMapper.map(model,VideoInfo.class);

        User user = getCurrentUser();
        video.setCreatorId(user.getId());
         //step2 调用service层做入库操作
        videoInfoService.insertByFilter(video);

        return RestResponse.ok();
    }

    @RequestMapping(value = "/edit", method = RequestMethod.POST)
    public RestResponse<VideoResponseVM> editVideo(@RequestBody @Valid VideoCreateVM model) {
        //step1 校验视频是否上传 （判断url是否为空）
        if(StringUtils.isBlank(model.getVideoUrl()))
        {
            return RestResponse.fail(500,"视频文件未上传");
        }


        return RestResponse.ok();
    }

    @RequestMapping(value = "/delete/{id}", method = RequestMethod.POST)
    public RestResponse delete(@PathVariable Integer id) {
        return RestResponse.ok();
    }


    @RequestMapping(value = "/userAnalysis/{id}", method = RequestMethod.POST)
    public RestResponse <UserAnalysisVM> userAnalysis(@PathVariable Integer id) {

        List<VideoInfo> recommendVideoList = videoInfoService.userAnalysis(id);
        UserAnalysisVM vm = new UserAnalysisVM();
        vm.setVideoRecommendList(recommendVideoList);
        return RestResponse.ok(vm);

    }
}
