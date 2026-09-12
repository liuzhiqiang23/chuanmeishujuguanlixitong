-- =====================================================================
-- fix_schema.sql  增量数据库修复脚本（针对已部署环境）
-- ---------------------------------------------------------------------
-- 问题现象：Web 界面的"数媒数据分析"等多个页面标签提示"系统内部错误"
-- 根因：数据库表结构与后端代码（Mapper XML / 实体类）不一致：
--   1. t_message 表缺少 content / send_user_id / send_user_name /
--      send_real_name / receive_user_count / read_count 列
--   2. t_message_user 表缺少 receive_user_name / receive_real_name /
--      create_time 列（旧表只有 send_time）
--   3. 若未执行过 movie_analysis_schema.sql，t_video_info 缺少电影分析
--      扩展列，t_user_video_operation 缺少 rating 列，会导致
--      "用户分析 / 数据可视化分析" 等标签同样报错
--
-- 用法：
--   mysql -uroot -p 数据库名 < fix_schema.sql
--   （或使用 Navicat / DataGrip 等工具直接执行本脚本）
--   本脚本幂等，可重复执行；执行完成后重启后端即可。
-- =====================================================================

-- 重要：脚本内含中文，必须保证连接字符集为 utf8mb4。
-- 若使用命令行执行，请务必加参数：
--   mysql --default-character-set=utf8mb4 -uroot -p 数据库名 < fix_schema.sql
-- 否则在 Windows 下 mysql 客户端会按 GBK 解析本文件中的 UTF-8 中文，报
--   ERROR 1366 (HY000) Incorrect string value ... 错误。
SET NAMES utf8mb4;

-- ---------------------------------------------------------------------
-- 第 1 步：创建辅助存储过程（列不存在时自动补列）
-- ---------------------------------------------------------------------
DROP PROCEDURE IF EXISTS `fix_schema_add_column`;

DELIMITER $$
CREATE PROCEDURE `fix_schema_add_column`(IN tbl VARCHAR(64), IN col VARCHAR(64), IN ddl VARCHAR(512))
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = tbl
          AND COLUMN_NAME = col
    ) THEN
        SET @sql = CONCAT('ALTER TABLE `', tbl, '` ADD COLUMN ', ddl);
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END$$
DELIMITER ;

-- ---------------------------------------------------------------------
-- 第 2 步：修复 t_message 表（补齐代码需要的 6 个列）
-- ---------------------------------------------------------------------
CALL fix_schema_add_column('t_message', 'content',
    '`content` text NULL COMMENT ''消息内容'' AFTER `title`');
CALL fix_schema_add_column('t_message', 'send_user_id',
    '`send_user_id` int(11) NULL COMMENT ''发送人ID'' AFTER `create_time`');
CALL fix_schema_add_column('t_message', 'send_user_name',
    '`send_user_name` varchar(50) NULL COMMENT ''发送人用户名'' AFTER `send_user_id`');
CALL fix_schema_add_column('t_message', 'send_real_name',
    '`send_real_name` varchar(50) NULL COMMENT ''发送人姓名'' AFTER `send_user_name`');
CALL fix_schema_add_column('t_message', 'receive_user_count',
    '`receive_user_count` int(11) NULL DEFAULT 0 COMMENT ''接收人数'' AFTER `send_real_name`');
CALL fix_schema_add_column('t_message', 'read_count',
    '`read_count` int(11) NULL DEFAULT 0 COMMENT ''已读人数'' AFTER `receive_user_count`');

-- ---------------------------------------------------------------------
-- 第 3 步：修复 t_message_user 表
-- （旧表只有 send_time，代码需要 create_time，先把 send_time 改名）
-- ---------------------------------------------------------------------
-- 若 send_time 存在且 create_time 不存在，则改名
DROP PROCEDURE IF EXISTS `fix_schema_rename_column`;
DELIMITER $$
CREATE PROCEDURE `fix_schema_rename_column`(IN tbl VARCHAR(64), IN old_col VARCHAR(64), IN new_col VARCHAR(64), IN ddl VARCHAR(512))
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = tbl
          AND COLUMN_NAME = old_col
    ) AND NOT EXISTS (
        SELECT 1
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = tbl
          AND COLUMN_NAME = new_col
    ) THEN
        SET @sql = CONCAT('ALTER TABLE `', tbl, '` CHANGE COLUMN `', old_col, '` ', ddl);
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END$$
DELIMITER ;

CALL fix_schema_rename_column('t_message_user', 'send_time', 'create_time',
    '`create_time` datetime NULL DEFAULT NULL');

-- 补齐 t_message_user 缺少的列
CALL fix_schema_add_column('t_message_user', 'receive_user_name',
    '`receive_user_name` varchar(50) NULL COMMENT ''接收人用户名'' AFTER `receive_user_id`');
CALL fix_schema_add_column('t_message_user', 'receive_real_name',
    '`receive_real_name` varchar(50) NULL COMMENT ''接收人姓名'' AFTER `receive_user_name`');

-- ---------------------------------------------------------------------
-- 第 4 步：修复电影分析扩展列（若未执行过 movie_analysis_schema.sql）
-- ---------------------------------------------------------------------
-- t_video_info：TMDB 电影字段
CALL fix_schema_add_column('t_video_info', 'original_title',
    '`original_title` varchar(255) NULL COMMENT ''原始标题'' AFTER `video_name`');
CALL fix_schema_add_column('t_video_info', 'overview',
    '`overview` text NULL COMMENT ''简介'' AFTER `original_title`');
CALL fix_schema_add_column('t_video_info', 'tagline',
    '`tagline` varchar(500) NULL COMMENT ''标语'' AFTER `overview`');
CALL fix_schema_add_column('t_video_info', 'budget',
    '`budget` bigint(20) NULL DEFAULT 0 COMMENT ''预算'' AFTER `tagline`');
CALL fix_schema_add_column('t_video_info', 'revenue',
    '`revenue` bigint(20) NULL DEFAULT 0 COMMENT ''票房'' AFTER `budget`');
CALL fix_schema_add_column('t_video_info', 'popularity',
    '`popularity` double NULL DEFAULT 0 COMMENT ''热度值'' AFTER `revenue`');
CALL fix_schema_add_column('t_video_info', 'vote_average',
    '`vote_average` double NULL DEFAULT 0 COMMENT ''平均评分'' AFTER `popularity`');
CALL fix_schema_add_column('t_video_info', 'vote_count',
    '`vote_count` int(11) NULL DEFAULT 0 COMMENT ''评分人数'' AFTER `vote_average`');
CALL fix_schema_add_column('t_video_info', 'runtime',
    '`runtime` int(11) NULL DEFAULT 0 COMMENT ''片长(分钟)'' AFTER `vote_count`');
CALL fix_schema_add_column('t_video_info', 'release_date',
    '`release_date` date NULL COMMENT ''上映日期'' AFTER `runtime`');
CALL fix_schema_add_column('t_video_info', 'original_language',
    '`original_language` varchar(10) NULL COMMENT ''原始语言'' AFTER `release_date`');
CALL fix_schema_add_column('t_video_info', 'poster_path',
    '`poster_path` varchar(500) NULL COMMENT ''海报路径'' AFTER `original_language`');
CALL fix_schema_add_column('t_video_info', 'heat_score',
    '`heat_score` double NULL DEFAULT 0 COMMENT ''综合热度评分'' AFTER `poster_path`');

-- t_video_info.video_name 需容纳 TMDB 长片名（最长 86 字符；原 varchar(50)
-- 会导致 import_data.py 导入时报 1406 Data too long for column 'video_name'）
ALTER TABLE t_video_info MODIFY COLUMN `video_name` varchar(255) NULL COMMENT '影片名';

-- t_user_video_operation：评分字段
CALL fix_schema_add_column('t_user_video_operation', 'rating',
    '`rating` double NULL DEFAULT NULL COMMENT ''用户评分'' AFTER `finally_active_time`');

-- ---------------------------------------------------------------------
-- 第 5 步：清理辅助存储过程
-- ---------------------------------------------------------------------
DROP PROCEDURE IF EXISTS `fix_schema_add_column`;
DROP PROCEDURE IF EXISTS `fix_schema_rename_column`;

-- =====================================================================
-- 执行完成后请重启后端服务，再刷新前端页面验证。
-- 若仍报错，请查看后端日志：
--   backend/log/exam-YYYYMMDD.log 中 ERROR 日志的具体 SQL 原因。
-- =====================================================================
