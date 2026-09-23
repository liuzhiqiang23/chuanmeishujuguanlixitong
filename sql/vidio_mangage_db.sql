-- 历史存档：旧库 vidio_mangage_db 的建表脚本（Navicat 导出）。
-- 该库已于 2026-09-23 按作业要求迁移合并且删除；现系统唯一库为 movie_analytics_db
-- （框架表已迁入其中），新项目表见同目录 movie_analytics_db.sql。
/*
 Navicat Premium Data Transfer

 Source Server         : 3306
 Source Server Type    : MySQL
 Source Server Version : 80012
 Source Host           : localhost:3306
 Source Schema         : vidio_mangage_db

 Target Server Type    : MySQL
 Target Server Version : 80012
 Date: 27/09/2021 11:07:43
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for t_message
-- ----------------------------
DROP TABLE IF EXISTS `t_message`;
CREATE TABLE `t_message`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '标题',
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '消息内容',
  `create_time` datetime(0) NULL DEFAULT NULL,
  `send_user_id` int(11) NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人用户名',
  `send_real_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人姓名',
  `receive_user_count` int(11) NULL DEFAULT 0 COMMENT '接收人数',
  `read_count` int(11) NULL DEFAULT 0 COMMENT '已读人数',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of t_message
-- ----------------------------
INSERT INTO `t_message` VALUES (1, '分为非', NULL, '2019-09-07 06:59:59', 2, 'admin', '管理员', 1, 1);
INSERT INTO `t_message` VALUES (2, 'dd', NULL, '2021-08-12 13:54:34', 2, 'admin', '管理员', 1, 0);
INSERT INTO `t_message` VALUES (3, 'gg', NULL, '2021-08-12 13:55:45', 2, 'admin', '管理员', 1, 0);

-- ----------------------------
-- Table structure for t_message_user
-- ----------------------------
DROP TABLE IF EXISTS `t_message_user`;
CREATE TABLE `t_message_user`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `message_id` int(11) NULL DEFAULT NULL COMMENT '消息内容ID',
  `receive_user_id` int(11) NULL DEFAULT NULL COMMENT '接收人ID',
  `receive_user_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收人用户名',
  `receive_real_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收人姓名',
  `readed` bit(1) NULL DEFAULT NULL COMMENT '是否已读',
  `create_time` datetime(0) NULL DEFAULT NULL,
  `read_time` datetime(0) NULL DEFAULT NULL COMMENT '阅读时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `fk_message_user_id`(`receive_user_id`) USING BTREE,
  INDEX `fk_message_id`(`message_id`) USING BTREE,
  CONSTRAINT `fk_message_id` FOREIGN KEY (`message_id`) REFERENCES `t_message` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_message_user_id` FOREIGN KEY (`receive_user_id`) REFERENCES `t_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of t_message_user
-- ----------------------------
INSERT INTO `t_message_user` VALUES (1, 1, 1, 'admin', '管理员', b'1', '2019-09-07 06:59:59', '2019-09-07 07:06:50');
INSERT INTO `t_message_user` VALUES (2, 2, 1, 'admin', '管理员', b'0', '2021-08-12 13:54:34', NULL);
INSERT INTO `t_message_user` VALUES (3, 3, 1, 'admin', '管理员', b'0', '2021-08-12 13:55:45', NULL);

-- ----------------------------
-- Table structure for t_role
-- ----------------------------
DROP TABLE IF EXISTS `t_role`;
CREATE TABLE `t_role`  (
  `role_id` int(11) NOT NULL,
  `user_id` int(11) NULL DEFAULT NULL,
  `role_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `role_describe` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`role_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of t_role
-- ----------------------------
INSERT INTO `t_role` VALUES (3, 2, 'ADMIN', '管理员');

-- ----------------------------
-- Table structure for t_tag
-- ----------------------------
DROP TABLE IF EXISTS `t_tag`;
CREATE TABLE `t_tag`  (
  `tag_id` int(11) NOT NULL AUTO_INCREMENT,
  `tag_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`tag_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for t_user
-- ----------------------------
DROP TABLE IF EXISTS `t_user`;
CREATE TABLE `t_user`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_uuid` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `user_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '用户名',
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `real_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '真实姓名',
  `age` int(11) NULL DEFAULT NULL,
  `sex` tinyint(1) NULL DEFAULT NULL COMMENT '1.男 0女',
  `birth_day` datetime(0) NULL DEFAULT NULL,
  `phone` char(11) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `status` int(11) NULL DEFAULT NULL COMMENT '1.启用 2禁用',
  `image_path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '头像地址',
  `create_time` datetime(0) NULL DEFAULT NULL,
  `modify_time` datetime(0) NULL DEFAULT NULL,
  `last_active_time` datetime(0) NULL DEFAULT NULL,
  `deleted` tinyint(1) NULL DEFAULT NULL COMMENT '是否删除',
  `city` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `job` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `wx_open_id` varchar(0) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `role` int(11) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of t_user
-- ----------------------------
INSERT INTO `t_user` VALUES (1, 'd2d29da2-dcb3-4013-b874-727626236f47', 'student', 'D1AGFL+Gx37t0NPG4d6biYP5Z31cNbwhK5w1lUeiHB2zagqbk8efYfSjYoh1Z/j1dkiRjHU+b0EpwzCh8IGsksJjzD65ci5LsnodQVf4Uj6D3pwoscXGqmkjjpzvSJbx42swwNTA+QoDU8YLo7JhtbUK2X0qCjFGpd+8eJ5BGvk=', '学生', 17, 1, '2019-09-07 18:54:40', '15007133738', 1, NULL, '2021-09-07 18:55:02', NULL, NULL, 0, '南京', '学生', NULL, 1);
INSERT INTO `t_user` VALUES (2, '52045f5f-a13f-4ccc-93dd-f7ee8270ad4c', 'admin', 'D1AGFL+Gx37t0NPG4d6biYP5Z31cNbwhK5w1lUeiHB2zagqbk8efYfSjYoh1Z/j1dkiRjHU+b0EpwzCh8IGsksJjzD65ci5LsnodQVf4Uj6D3pwoscXGqmkjjpzvSJbx42swwNTA+QoDU8YLo7JhtbUK2X0qCjFGpd+8eJ5BGvk=', '管理员', 35, 1, '2019-09-07 18:56:07', NULL, 1, NULL, '2019-09-07 18:56:21', NULL, NULL, 0, NULL, NULL, NULL, 3);
INSERT INTO `t_user` VALUES (3, '52379b13-5c01-43f9-a427-899ae57989c0', 'alvis', 'fnanT3ob78rUADLF8Mky+N29gFyP5952C861ONTSn0A9n8VXU414aSqIVghU+YOVc6UHltxMM+AVymdZPssw+zIUiJtbWu4+zYH4iDfpIHyJW1Tb01IVs3nJPId5YMVWd9rMBBkavA73zOjdwkm13HcV98bFMxyhIqoNuuWdCSY=', 'alvis', NULL, NULL, NULL, NULL, 1, NULL, '2019-09-07 06:54:49', '2021-08-27 02:48:02', '2019-09-07 06:54:49', 0, NULL, NULL, NULL, 1);
INSERT INTO `t_user` VALUES (4, '4e182be9-3ee0-45a4-8329-fd79aee3b8e2', '32', 'je+NzP95ymeyrTYnFy7+SLqWlePAYvV4AoZBnVhNAJcYYPDJ9hpLMOj0epD7nkz9N1F/IunV4kK8HylCqGZoDFGx4/ey8LKVElG1JYxbZEvAf6OM8Qu/gvL6Hhyan3UHMbYcgXQ16gZtasHrz3K4s3Pb0x14GZtN9WBqqBw4Vec=', '32', NULL, NULL, NULL, NULL, 1, NULL, '2019-09-07 06:56:28', '2021-09-27 03:03:34', '2019-09-07 06:56:28', 0, NULL, NULL, NULL, 1);
INSERT INTO `t_user` VALUES (5, 'f0cfa3c5-7131-48af-a2be-b8c792018daa', 'bbbvc', 'kc0DETYvKgh9AYyb2oV+b7Z9+DOrcrAbp5F/KMFCtLE5hPyhXy7kHqksNEcCvsPgW2jygkGF6Gfj5iyhRwA/fhacW/LR7+8zOGUQ3hyejPygLW+H2VEkUVnV/LlkD5ge7chqAdBRUkU7uW6MoFGscPL1oTTLusjE5e1hRmHkdWQ=', '2323', NULL, NULL, NULL, NULL, 1, NULL, '2019-09-07 06:57:16', NULL, '2019-09-07 06:57:16', 0, NULL, NULL, NULL, 1);
INSERT INTO `t_user` VALUES (6, '43484f2d-61a2-434a-a8b3-be9b53602fd6', '的', 'STVxlaVguREAwKsIZPAllSYhII2ET8GQn7X9JCnMCjTRDsq5J3NfCKX8V6TuhjcgX1m+yVsUy8rZyLVCl2rbOuTQ3lFA6Bcztp+TluCucRyDuh1fPiyId2MD2ScMDdBCQv6RGxt5DKO+bHBE1Vxpmm5iTqISbw2+93hxYaztGE8=', '得到', NULL, NULL, NULL, NULL, 1, NULL, '2021-09-26 15:21:42', NULL, '2021-09-26 15:21:42', 0, NULL, NULL, NULL, 3);

-- ----------------------------
-- Table structure for t_user_event_log
-- ----------------------------
DROP TABLE IF EXISTS `t_user_event_log`;
CREATE TABLE `t_user_event_log`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NULL DEFAULT NULL COMMENT '用户id',
  `user_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '用户名',
  `real_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '真实姓名',
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '内容',
  `create_time` datetime(0) NULL DEFAULT NULL COMMENT '时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `fk_user_log`(`user_id`) USING BTREE,
  CONSTRAINT `fk_user_log` FOREIGN KEY (`user_id`) REFERENCES `t_user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 26 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of t_user_event_log
-- ----------------------------
INSERT INTO `t_user_event_log` VALUES (1, 1, 'student', '学生', 'student 登录了传媒数据管理与分析系统', '2019-09-07 06:49:23');
INSERT INTO `t_user_event_log` VALUES (2, 2, 'admin', '管理员', 'admin 登录了传媒数据管理与分析系统', '2019-09-07 06:51:35');
INSERT INTO `t_user_event_log` VALUES (3, 2, 'admin', '管理员', 'admin 登出了传媒数据管理与分析系统', '2019-09-07 07:00:38');
INSERT INTO `t_user_event_log` VALUES (4, 1, 'student', '学生', 'student 登录了传媒数据管理与分析系统', '2019-09-07 07:00:44');
INSERT INTO `t_user_event_log` VALUES (5, 1, 'student', '学生', 'student 提交试卷：固定试卷 得分：3 耗时：4 秒', '2019-09-07 07:07:09');
INSERT INTO `t_user_event_log` VALUES (6, 1, 'student', '学生', 'student 批改试卷：固定试卷 得分：6', '2019-09-07 07:07:20');
INSERT INTO `t_user_event_log` VALUES (7, 1, 'student', '学生', 'student 登录了传媒数据管理与分析系统', '2021-08-12 08:34:25');
INSERT INTO `t_user_event_log` VALUES (8, 2, 'admin', '管理员', 'admin 登出了传媒数据管理与分析系统', '2021-08-16 07:20:13');
INSERT INTO `t_user_event_log` VALUES (9, 2, 'admin', '管理员', 'admin 登录了传媒数据管理与分析系统', '2021-08-16 07:23:45');
INSERT INTO `t_user_event_log` VALUES (10, 2, 'admin', '管理员', 'admin 登录了传媒数据管理与分析系统', '2021-08-27 02:47:11');
INSERT INTO `t_user_event_log` VALUES (11, 2, 'admin', '管理员', 'admin 登录了传媒数据管理与分析系统', '2021-08-27 07:58:02');
INSERT INTO `t_user_event_log` VALUES (12, 2, 'admin', '管理员', 'admin 登录了传媒数据管理与分析系统', '2021-08-28 02:57:59');
INSERT INTO `t_user_event_log` VALUES (13, 2, 'admin', '管理员', 'admin 登录了传媒数据管理与分析系统', '2021-09-08 10:40:38');
INSERT INTO `t_user_event_log` VALUES (14, 2, 'admin', '管理员', 'admin 登录了传媒数据管理与分析系统', '2021-09-22 03:45:29');
INSERT INTO `t_user_event_log` VALUES (15, 2, 'admin', '管理员', 'admin 登录了传媒数据管理与分析系统', '2021-09-22 03:51:24');
INSERT INTO `t_user_event_log` VALUES (16, 2, 'admin', '管理员', 'admin 登录了传媒数据管理与分析系统', '2021-09-22 03:52:09');
INSERT INTO `t_user_event_log` VALUES (17, 2, 'admin', '管理员', 'admin 登录了传媒数据管理与分析系统', '2021-09-22 06:08:55');
INSERT INTO `t_user_event_log` VALUES (18, 2, 'admin', '管理员', 'admin 登出了传媒数据管理与分析系统', '2021-09-22 06:25:30');
INSERT INTO `t_user_event_log` VALUES (19, 2, 'admin', '管理员', 'admin 登录了传媒数据管理与分析系统', '2021-09-22 06:35:14');
INSERT INTO `t_user_event_log` VALUES (20, 2, 'admin', '管理员', 'admin 登录了传媒数据管理与分析系统', '2021-09-22 14:19:40');
INSERT INTO `t_user_event_log` VALUES (21, 2, 'admin', '管理员', 'admin 登出了传媒数据管理与分析系统', '2021-09-22 14:39:29');
INSERT INTO `t_user_event_log` VALUES (22, 2, 'admin', '管理员', 'admin 登录了传媒数据管理与分析系统', '2021-09-22 14:39:37');
INSERT INTO `t_user_event_log` VALUES (23, 2, 'admin', '管理员', 'admin 登录了传媒数据管理与分析系统', '2021-09-23 06:13:18');
INSERT INTO `t_user_event_log` VALUES (24, 2, 'admin', '管理员', 'admin 登录了传媒数据管理与分析系统', '2021-09-23 07:48:11');
INSERT INTO `t_user_event_log` VALUES (25, 2, 'admin', '管理员', 'admin 登录了传媒数据管理与分析系统', '2021-09-26 00:39:42');

-- ----------------------------
-- Table structure for t_user_role_relation
-- ----------------------------
DROP TABLE IF EXISTS `t_user_role_relation`;
CREATE TABLE `t_user_role_relation`  (
  `role_id` int(11) NOT NULL,
  `user_id` int(11) NULL DEFAULT NULL,
  INDEX `fk_relation_user_id`(`user_id`) USING BTREE,
  INDEX `fk_relation_role_id`(`role_id`) USING BTREE,
  CONSTRAINT `fk_relation_role_id` FOREIGN KEY (`role_id`) REFERENCES `t_role` (`role_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_relation_user_id` FOREIGN KEY (`user_id`) REFERENCES `t_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for t_user_tag
-- ----------------------------
DROP TABLE IF EXISTS `t_user_tag`;
CREATE TABLE `t_user_tag`  (
  `user_id` int(11) NOT NULL,
  `tag_id` int(11) NULL DEFAULT NULL,
  `user_property_flag` tinyint(1) NULL DEFAULT NULL COMMENT '是否分析得到的数据是1否0',
  INDEX `fk_user_likes`(`user_id`) USING BTREE,
  INDEX `fk_t_user_tagId`(`tag_id`) USING BTREE,
  CONSTRAINT `fk_user_likes` FOREIGN KEY (`user_id`) REFERENCES `t_user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_t_user_tagId` FOREIGN KEY (`tag_id`) REFERENCES `t_tag` (`tag_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for t_user_token
-- ----------------------------
DROP TABLE IF EXISTS `t_user_token`;
CREATE TABLE `t_user_token`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `token` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `user_id` int(11) NULL DEFAULT NULL COMMENT '用户Id',
  `wx_open_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '微信openId',
  `create_time` datetime(0) NULL DEFAULT NULL,
  `end_time` datetime(0) NULL DEFAULT NULL,
  `user_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '用户名',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `fk_toke_user_id`(`user_id`) USING BTREE,
  CONSTRAINT `fk_toke_user_id` FOREIGN KEY (`user_id`) REFERENCES `t_user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for t_user_video_operation
-- ----------------------------
DROP TABLE IF EXISTS `t_user_video_operation`;
CREATE TABLE `t_user_video_operation`  (
  `id` int(11) NOT NULL COMMENT '用户ID',
  `video_id` int(11) NOT NULL COMMENT '视频ID',
  `thumb_up` int(11) NULL DEFAULT NULL COMMENT '是否点赞,1为点赞，0或null为不点赞',
  `collection` int(11) NULL DEFAULT NULL COMMENT '是否收藏,1为收藏,0或null为不收藏',
  `praise_bad_reviews` int(11) NULL DEFAULT NULL COMMENT '1为好评，0为差评',
  `comment` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '评论内容',
  `finally_active_time` datetime(6) NULL DEFAULT NULL COMMENT '最后活跃时间',
  PRIMARY KEY (`id`, `video_id`) USING BTREE,
  INDEX `fk_user_operation_video_id`(`video_id`) USING BTREE,
  CONSTRAINT `fk_user_operation_id` FOREIGN KEY (`id`) REFERENCES `t_user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_user_operation_video_id` FOREIGN KEY (`video_id`) REFERENCES `t_video_info` (`video_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for t_video_info
-- ----------------------------
DROP TABLE IF EXISTS `t_video_info`;
CREATE TABLE `t_video_info`  (
  `video_id` int(11) NOT NULL AUTO_INCREMENT,
  `video_name` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `video_category` tinyint(1) NULL DEFAULT NULL COMMENT '1.教学视频，2，娱乐短视频，3，电影 4电视剧',
  `create_time` date NULL DEFAULT NULL,
  `creator_id` int(11) NULL DEFAULT NULL COMMENT '视频上传者的id',
  `last_modify_time` datetime(0) NULL DEFAULT NULL,
  `video_url` varchar(500) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '视频保存的地址',
  PRIMARY KEY (`video_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of t_video_info
-- ----------------------------
INSERT INTO `t_video_info` VALUES (3, '小猪佩奇', 2, '2020-04-02', NULL, NULL, NULL);
INSERT INTO `t_video_info` VALUES (4, '冰雪传奇', 2, '2020-04-02', NULL, NULL, NULL);
INSERT INTO `t_video_info` VALUES (5, '冰河世纪', 2, '2020-04-02', NULL, NULL, NULL);
INSERT INTO `t_video_info` VALUES (6, '指环王', 1, '2020-04-02', NULL, NULL, NULL);

-- ----------------------------
-- Table structure for t_video_play
-- ----------------------------
DROP TABLE IF EXISTS `t_video_play`;
CREATE TABLE `t_video_play`  (
  `video_id` int(10) NULL DEFAULT NULL,
  `user_id` int(10) NULL DEFAULT NULL,
  `last_play_time` datetime(0) NULL DEFAULT NULL,
  `play_times` int(11) NOT NULL,
  INDEX `fk_media_play_mediaId`(`user_id`) USING BTREE,
  INDEX `fk_video_play_video_id`(`video_id`) USING BTREE,
  CONSTRAINT `fk_media_play_mediaId` FOREIGN KEY (`user_id`) REFERENCES `t_user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_video_play_video_id` FOREIGN KEY (`video_id`) REFERENCES `t_video_info` (`video_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for t_video_tag
-- ----------------------------
DROP TABLE IF EXISTS `t_video_tag`;
CREATE TABLE `t_video_tag`  (
  `video_id` int(11) NOT NULL,
  `tag_id` int(11) NULL DEFAULT NULL COMMENT '视频属性标签',
  `video_property_flag` tinyint(1) NULL DEFAULT NULL COMMENT '是否未分析得到的数据是1不是2',
  INDEX `fk_video_property_id`(`video_id`) USING BTREE,
  INDEX `fk_t_video_tagId`(`tag_id`) USING BTREE,
  CONSTRAINT `fk_video_property_id` FOREIGN KEY (`video_id`) REFERENCES `t_video_info` (`video_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_t_video_tagId` FOREIGN KEY (`tag_id`) REFERENCES `t_tag` (`tag_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
