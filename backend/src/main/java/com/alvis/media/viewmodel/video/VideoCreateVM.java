package com.alvis.media.viewmodel.video;

import com.alvis.media.domain.VideoTag;
import lombok.Data;

import java.util.List;

@Data
public class VideoCreateVM {
     private Integer videoId;
     private  String videoUrl;
     private String videoName;
     private Integer videoCategory;

    private List <VideoTag> videoTagList;
}
