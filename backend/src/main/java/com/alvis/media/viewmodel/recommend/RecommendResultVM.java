package com.alvis.media.viewmodel.recommend;

import lombok.Data;

import java.util.List;
import java.util.Map;

/** 推荐结果（含策略与参考影片信息，便于前端切换展示口径） */
@Data
public class RecommendResultVM {

    private String strategy;

    /** similar 策略下回带参考影片信息 */
    private Map<String, Object> seed;

    private List<RecommendItemVM> items;

    /** 脚本内部耗时（秒） */
    private Double seconds;
}
