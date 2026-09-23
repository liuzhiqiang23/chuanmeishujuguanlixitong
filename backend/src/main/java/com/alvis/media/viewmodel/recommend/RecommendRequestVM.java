package com.alvis.media.viewmodel.recommend;

import lombok.Data;

/**
 * 智能推荐请求。
 * 策略：similar（给一部参考影片，返回内容相似的影片）| genre_hot（给一个类型，返回该类型热门）。
 */
@Data
public class RecommendRequestVM {

    /** similar | genre_hot（缺省时按传入字段自动判断） */
    private String strategy;

    /** 参考影片 id（strategy=similar 必填，对应 t_movie.id） */
    private Long movieId;

    /** 类型名，英文如 Animation，也兼容常见中文名如 动画（strategy=genre_hot 必填） */
    private String genre;

    private Integer topN = 10;

    /** 当前登录用户 id（控制器从 token 取，客户端不需要传）——用于站内评分加权 */
    private Integer userId;
}
