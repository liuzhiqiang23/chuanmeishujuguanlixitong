package com.alvis.media.service.impl;

import com.alvis.media.domain.VideoPlay;
import com.alvis.media.domain.other.KeyValue;
import com.alvis.media.repository.MediaBaseMapper;
import com.alvis.media.repository.VideoPlayMapper;
import com.alvis.media.service.VideoPlayService;
import com.alvis.media.utility.DateTimeUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Date;
import java.util.List;
import java.util.stream.Collectors;

/**
 * @author 奇趣
 */
@Service

public class VideoPlayServiceImpl extends BaseServiceImpl <VideoPlay> implements VideoPlayService {

    private final VideoPlayMapper videoPlayMapper;


    @Autowired
    public VideoPlayServiceImpl(VideoPlayMapper videoPlayMapper, MediaBaseMapper <VideoPlay> videoInfoMapperr) {
        super(videoInfoMapperr);
        this.videoPlayMapper = videoPlayMapper;

    }


    @Override
    public int selectVideoPlayCount(VideoPlay filter) {
        //当月的用户新增视频数量
        //封装查询条件
        filter.setLastPlayTime(DateTimeUtil.getMonthStartDay());
        // 调用dao 并返回
        Integer count = videoPlayMapper.selectVideoPlayCount(filter);

        return count == null ? 0 : count;
    }

    @Override
    public String selectBestVideo(VideoPlay filter) {
        //当月的最佳影片
        //封装查询条件
        filter.setLastPlayTime(DateTimeUtil.getMonthStartDay());
        // 调用dao 并返回
        return videoPlayMapper.selectBestVideo(filter);
    }

    @Override
    public List<Integer> selectMothCount() {
		// 获取当前月的第一天
        Date startTime = DateTimeUtil.getMonthStartDay();
		// 获取当前月的最后一天
        Date endTime = DateTimeUtil.getMonthEndDay();
		
		// 按照最后播放时间分组后得到的每一组播放次数
        List <KeyValue> mouthCount = videoPlayMapper.selectCountByDate(startTime, endTime);
        
		List <String> mothStartToNowFormat = DateTimeUtil.MothStartToNowFormat();
        return mothStartToNowFormat.stream().map(md -> {
            KeyValue keyValue = mouthCount.stream().filter(kv -> kv.getName().equals(md)).findAny().orElse(null);
            return null == keyValue ? 0 : keyValue.getValue();
        }).collect(Collectors.toList());
    }
}
