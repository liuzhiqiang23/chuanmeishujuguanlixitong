package com.alvis.media.viewmodel.admin.dashboard;

import com.alvis.media.domain.VideoInfo;
import lombok.Data;

import java.util.List;

@Data
public class IndexVM {
    private Integer newUserCount;
    private Integer newVideoCount;
    private Integer doPlayVideoCount;
    private String hotVideoCount;
    private List<Integer> mothDayUserActionValue;
    private List<Integer> mothDayVideoPlayValue;
    private List<String> mothDayText;
    private List<VideoInfo> heatTopList;
}
