package com.alvis.media.config;

import com.alvis.media.service.VideoInfoService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

/**
 * 应用启动后自动触发热度计算（heat_score），
 * 避免首页「视频热度榜单 TOP10」因 heat_score 为 NULL 而永远为空。
 */
@Slf4j
@Component
public class HeatInitRunner implements CommandLineRunner {

    private final VideoInfoService videoInfoService;

    public HeatInitRunner(VideoInfoService videoInfoService) {
        this.videoInfoService = videoInfoService;
    }

    @Override
    public void run(String... args) {
        try {
            int n = videoInfoService.recalculateHeat();
            log.info("视频热度初始化完成，共更新 {} 部电影", n);
        } catch (Exception e) {
            log.warn("视频热度初始化失败（可能尚未导入数据），已跳过", e);
        }
    }
}
