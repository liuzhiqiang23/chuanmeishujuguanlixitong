-- 历史存档：早期在旧库 vidio_mangage_db 上做的电影元数据扩展脚本。
-- 旧库已于 2026-09-23 迁移合并且删除，现系统唯一库为 movie_analytics_db。
-- 注意：如需在全新环境重建框架表，请使用 sql/backup/ 的库备份或 movie_analytics_db.sql 的新表部分。
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE DATABASE IF NOT EXISTS vidio_mangage_db DEFAULT CHARACTER SET utf8mb4;

USE vidio_mangage_db;

-- 电影主表扩展：在 t_video_info 原 7 列基础上追加电影元数据列
ALTER TABLE t_video_info
  ADD COLUMN original_title    VARCHAR(255) NULL COMMENT '原名',
  ADD COLUMN overview          TEXT         NULL COMMENT '简介',
  ADD COLUMN tagline           VARCHAR(255) NULL COMMENT '标语',
  ADD COLUMN budget            BIGINT       NULL COMMENT '预算',
  ADD COLUMN revenue           BIGINT       NULL COMMENT '票房',
  ADD COLUMN popularity        DOUBLE       NULL COMMENT '受欢迎度',
  ADD COLUMN vote_average      DOUBLE       NULL COMMENT '平均评分',
  ADD COLUMN vote_count        INT          NULL COMMENT '评分人数',
  ADD COLUMN runtime           INT          NULL COMMENT '时长(分)',
  ADD COLUMN release_date      DATE         NULL COMMENT '上映日期',
  ADD COLUMN original_language VARCHAR(10)  NULL COMMENT '语言',
  ADD COLUMN poster_path       VARCHAR(255) NULL COMMENT '海报路径',
  ADD COLUMN heat_score        DOUBLE       NULL COMMENT '热度(计算)';

-- 交互表扩展：加评分列（MovieLens 评分 0.5~5.0）
ALTER TABLE t_user_video_operation
  ADD COLUMN rating DOUBLE NULL COMMENT '用户评分(0.5-5.0)';

-- 修复：TMDB 有电影标题超 50 字符（最长 86），原 varchar(50) 导入会报 Data too long 并回滚，
-- 放宽到 VARCHAR(255)，保持原列的可空性与默认值不变
ALTER TABLE t_video_info MODIFY COLUMN video_name VARCHAR(255) NULL DEFAULT NULL;

SET FOREIGN_KEY_CHECKS = 1;
