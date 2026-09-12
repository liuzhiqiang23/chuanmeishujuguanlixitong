package com.alvis.media.viewmodel.video;

import com.alvis.media.domain.VideoInfo;
import lombok.Data;

import java.util.List;
@Data
public class UserAnalysisVM {
    private List <VideoInfo> videoRecommendList;
}
