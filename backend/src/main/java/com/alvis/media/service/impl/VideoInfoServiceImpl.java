package com.alvis.media.service.impl;

import com.alvis.media.domain.VideoInfo;
import com.alvis.media.domain.VideoPlay;
import com.alvis.media.repository.MediaBaseMapper;
import com.alvis.media.repository.VideoInfoMapper;
import com.alvis.media.repository.VideoPlayMapper;
import com.alvis.media.service.VideoInfoService;
import com.alvis.media.utility.DateTimeUtil;
import com.alvis.media.utility.UserCFUtil;
import com.alvis.media.viewmodel.video.VideoPageRequestVM;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;

import java.util.*;
import java.util.stream.Collectors;

/**
 * @author 奇趣
 */
@Service

public class VideoInfoServiceImpl extends BaseServiceImpl <VideoInfo> implements VideoInfoService {


    private final VideoInfoMapper videoInfoMapper;
    private final VideoPlayMapper videoPlayMapper;


    @Autowired
    public VideoInfoServiceImpl(VideoInfoMapper videoInfoMapper, VideoPlayMapper videoPlayMapper, MediaBaseMapper<VideoInfo> videoInfoMapperr) {
        super(videoInfoMapperr);
        this.videoInfoMapper = videoInfoMapper;
        this.videoPlayMapper = videoPlayMapper;

    }

    @Override
    public int insertByFilter(VideoInfo record) {
        record.setLastModifyTime(new Date());
        record.setCreateTime(new Date());
        return baseMapper.insertSelective(record);
    }




    @Override
    public int selectNewVideoCount(VideoInfo filter) {
        //当月的用户新增视频数量
        //封装查询条件
        filter.setCreateTime(DateTimeUtil.getMonthStartDay());
        // 调用dao 并返回
        return videoInfoMapper.selectNewVideoCount(filter);
    }

    @Override
    public PageInfo <VideoInfo> userPage(VideoPageRequestVM requestVM) {
        // 默认按热度降序：海报/热度的热门电影排前，列表首屏观感正确；video_id 作稳定次序
        return PageHelper.startPage(requestVM.getPageIndex(), requestVM.getPageSize(), "heat_score desc, video_id desc").doSelectPageInfo(() ->
                videoInfoMapper.videoPage(requestVM)
        );
    }

    @Override
    public List <VideoInfo> userAnalysis(Integer recommendUserId) {

        List <VideoInfo> result = new ArrayList <>();
        //和该推荐用户的播放记录有交集的用户的播放记录。
        //第一步查找recommendUserId的播放列表 userid
        //要求推荐的用户播放的视频id列表
        List <Integer> recommendVideoIdPlayList = getPlayVideoIdListByUserId(recommendUserId);
        if (CollectionUtils.isEmpty(recommendVideoIdPlayList)) {
            return videoInfoMapper.selectHotVideoList();
        }

        Set <Integer> relationUserIdList = new HashSet <>();
        //遍历recommendVideoIdPlayList 去查找播放过这些视频的用户
        for (Integer videoId : recommendVideoIdPlayList) {
            VideoPlay filter = new VideoPlay();

            filter.setVideoId(videoId);
            List <VideoPlay> otherUserPlayList = videoPlayMapper.selectVideoPlayInfo(filter);

            if (CollectionUtils.isEmpty(otherUserPlayList)) {
                continue;
            }
            relationUserIdList.addAll(otherUserPlayList.stream()
                    .map(e -> e.getUserId()).collect(Collectors.toSet()));
        }

        //和该推荐用户的播放记录有交集的用户的播放记录。
        Map <Integer, List <Integer>> playList = new HashMap <>();
        playList.put(recommendUserId, recommendVideoIdPlayList);

        for (Integer userId : relationUserIdList) {
            if (userId.equals(recommendUserId)) {
                continue;
            }
            //要求推荐的用户播放的视频id列表
            playList.put(userId, getPlayVideoIdListByUserId(userId));
        }

        List <Integer> recommendVideoIdList = UserCFUtil.getRecommendationVideoList(playList, recommendUserId);
        //如果没有可推荐的
        if(CollectionUtils.isEmpty(recommendVideoIdList))
        {
          return  videoInfoMapper.selectHotVideoList();
        }
        for (Integer videoId : recommendVideoIdList) {
            VideoInfo videoInfo = videoInfoMapper.selectByPrimaryKey(videoId);
            // 过滤数据库中不存在的视频，避免前端拿到 null
            if (videoInfo != null) {
                result.add(videoInfo);
            }
        }
        return result;
    }


    private List <Integer> getPlayVideoIdListByUserId(Integer userId) {
        VideoPlay filter = new VideoPlay();
        filter.setUserId(userId);
        List <VideoPlay> recommendUserPlayList = videoPlayMapper.selectVideoPlayInfo(filter);
        //如果没有播放列表，则没有推荐产品
        if (CollectionUtils.isEmpty(recommendUserPlayList)) {
            return new ArrayList <>();
        }
        //要求推荐的用户播放的视频id列表
        List <Integer> recommendVideoIdPlayList = recommendUserPlayList.stream()
                .map(e -> e.getVideoId()).collect(Collectors.toList());

        return recommendVideoIdPlayList;
    }

    @Override
    public int insertVideoPlay(String realUrl, Integer userId) {
        // TMDB 元数据电影没有视频文件（video_url 为 NULL），
        // 此时 selectVideoIdByUrl 的 <if> 会丢掉 WHERE 变成全表查询（4908 行）导致 selectOne 崩溃。
        if (realUrl == null || realUrl.isEmpty()) {
            return 0;
        }
        //step1 组装数据
        VideoPlay videoPlay = new VideoPlay();
        videoPlay.setUserId(userId);
        //根据user_url获取videoId，
        videoPlay.setVideoId(videoInfoMapper.selectVideoIdByUrl(realUrl));
        //根据videoId和userId获取播放次数，
        List <VideoPlay> videoPlayListDb = videoPlayMapper.selectVideoPlayInfo(videoPlay);
        videoPlay.setLastPlayTime(new Date());
        if (CollectionUtils.isEmpty(videoPlayListDb)) {
            //insert
            videoPlay.setPlayTimes(1);
            videoPlayMapper.insertSelective(videoPlay);
        } else {
            VideoPlay videoPlayDb = videoPlayListDb.get(0);
            videoPlay.setPlayTimes(videoPlayDb.getPlayTimes() + 1);
            videoPlayMapper.updateByPrimaryKeySelective(videoPlay);
        }


        // 往t_video_paly这表insert一条数据或者update.
        return 0;
    }

    @Override
    public List <VideoPlay> selectVideoPlayByVideoId(Integer videoId) {
        VideoPlay filter = new VideoPlay();
        filter.setVideoId(videoId);
        return videoPlayMapper.selectVideoPlayInfo(filter);
    }

    @Override
    public int recalculateHeat() {
        // IMDB 加权分: score = v/(v+m)*r + m/(m+v)*c, 10 分制
        List<VideoInfo> all = videoInfoMapper.selectAll();
        double m = all.stream().mapToDouble(v -> v.getVoteCount() == null ? 0 : v.getVoteCount()).average().orElse(1);
        double c = all.stream().mapToDouble(v -> v.getVoteAverage() == null ? 0 : v.getVoteAverage()).average().orElse(0);
        double maxPop = all.stream().mapToDouble(v -> v.getPopularity() == null ? 0 : v.getPopularity()).max().orElse(1);
        double minPop = all.stream().mapToDouble(v -> v.getPopularity() == null ? 0 : v.getPopularity()).min().orElse(0);
        int updated = 0;
        for (VideoInfo v : all) {
            double vc = v.getVoteCount() == null ? 0 : v.getVoteCount();
            double r  = v.getVoteAverage() == null ? 0 : v.getVoteAverage();
            double imdb = (vc / (vc + m)) * r + (m / (m + vc)) * c;
            double pop = v.getPopularity() == null ? 0 : v.getPopularity();
            double normPop = (maxPop == minPop) ? 0 : (pop - minPop) / (maxPop - minPop) * 10;
            double play = vc; // 简化: 投票数≈热度（计划备注）
            double heat = 0.5 * Math.log10(1 + play) + 0.3 * imdb + 0.2 * normPop;
            v.setHeatScore(heat);
            videoInfoMapper.updateByPrimaryKeySelective(v);
            updated++;
        }
        return updated;
    }

    @Override
    public List<VideoInfo> heatTop(Integer limit) {
        if (limit == null || limit <= 0) limit = 10;
        return videoInfoMapper.selectHeatTop(limit);
    }

//    @Override
//    public int insertVideoPlay(String realUrl, Integer userId) {
//
//        VideoPlay videoPlay = new VideoPlay();
//        videoPlay.setUserId(userId);
//
//        videoPlay.setVideoId(videoInfoMapper.selectVideoIdByUrl(realUrl));
//
//        List <VideoPlay> videoPlayDb = videoPlayMapper.selectByUserIdAndVideoId(videoPlay);
//        if (null == videoPlayDb || 0 == videoPlayDb.size()) {
//            videoPlay.setLastPlayTime(new Date());
//            videoPlay.setPlayTimes(1);
//            videoPlayMapper.insertSelective(videoPlay);
//        } else {
//            videoPlay.setLastPlayTime(new Date());
//            videoPlay.setPlayTimes(videoPlayDb.get(0).getPlayTimes() + 1);
//            videoPlayMapper.updateByPrimaryKeySelective(videoPlay);
//        }
//        return 0;
//    }
}
