package com.alvis.media.viewmodel.video;

import com.alvis.media.domain.UserTag;
import com.alvis.media.domain.UserVideoOperation;
import com.alvis.media.domain.VideoPlay;
import lombok.Data;

import java.util.List;
@Data
public class VideoDetailVM {
    private Integer videoId;
    private String videoName;
    private String originalTitle;
    private String overview;
    private String tagline;
    private Double voteAverage;
    private Double popularity;
    private String releaseDate;
    private String posterPath;
    private List <VideoPlay> videoPlayList;



    private List <UserVideoOperation> videoOperationList;

    private List <UserTag> videoTagList;
}
