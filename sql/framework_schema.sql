-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: vidio_mangage_db
-- ------------------------------------------------------
-- Server version	8.0.41

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `vidio_mangage_db`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `vidio_mangage_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `vidio_mangage_db`;

--
-- Table structure for table `t_coupon`
--

DROP TABLE IF EXISTS `t_coupon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_coupon` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '券名',
  `threshold` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '使用门槛，0=无门槛',
  `amount` decimal(10,2) NOT NULL COMMENT '抵扣金额',
  `valid_days` int NOT NULL DEFAULT '7' COMMENT '领取后有效天数',
  `total_count` int NOT NULL DEFAULT '0' COMMENT '发行总量，0=不限量',
  `received_count` int NOT NULL DEFAULT '0' COMMENT '已领取数量',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '1上架 0下架',
  `create_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='优惠券模板';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_coupon`
--

/*!40000 ALTER TABLE `t_coupon` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_coupon` ENABLE KEYS */;

--
-- Table structure for table `t_coupon_share`
--

DROP TABLE IF EXISTS `t_coupon_share`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_coupon_share` (
  `share_id` int NOT NULL AUTO_INCREMENT,
  `sharer_id` int NOT NULL COMMENT '分享者 userId',
  `receiver_id` int NOT NULL COMMENT '被分享者 userId',
  `coupon_id` int NOT NULL COMMENT '发放的券模板 id',
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`share_id`),
  UNIQUE KEY `uk_sharer_receiver` (`sharer_id`,`receiver_id`),
  KEY `idx_sharer` (`sharer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='分享领券记录：同一对用户只发一次，防刷';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_coupon_share`
--

/*!40000 ALTER TABLE `t_coupon_share` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_coupon_share` ENABLE KEYS */;

--
-- Table structure for table `t_member`
--

DROP TABLE IF EXISTS `t_member`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_member` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL COMMENT 't_user.id',
  `level` tinyint(1) NOT NULL DEFAULT '1' COMMENT '会员等级，目前只有 1',
  `expire_time` datetime NOT NULL COMMENT '到期时间',
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_member_user` (`user_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='会员';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_member`
--

/*!40000 ALTER TABLE `t_member` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_member` ENABLE KEYS */;

--
-- Table structure for table `t_message`
--

DROP TABLE IF EXISTS `t_message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_message` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '标题',
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '消息内容',
  `create_time` datetime DEFAULT NULL,
  `send_user_id` int DEFAULT NULL COMMENT '发送人ID',
  `send_user_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '发送人用户名',
  `send_real_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '发送人姓名',
  `receive_user_count` int DEFAULT '0' COMMENT '接收人数',
  `read_count` int DEFAULT '0' COMMENT '已读人数',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_message`
--

/*!40000 ALTER TABLE `t_message` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_message` ENABLE KEYS */;

--
-- Table structure for table `t_message_user`
--

DROP TABLE IF EXISTS `t_message_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_message_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `message_id` int DEFAULT NULL COMMENT '消息内容ID',
  `receive_user_id` int DEFAULT NULL COMMENT '接收人ID',
  `receive_user_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '接收人用户名',
  `receive_real_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '接收人姓名',
  `readed` bit(1) DEFAULT NULL COMMENT '是否已读',
  `create_time` datetime DEFAULT NULL,
  `read_time` datetime DEFAULT NULL COMMENT '阅读时间',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `fk_message_user_id` (`receive_user_id`) USING BTREE,
  KEY `fk_message_id` (`message_id`) USING BTREE,
  CONSTRAINT `fk_message_id` FOREIGN KEY (`message_id`) REFERENCES `t_message` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_message_user_id` FOREIGN KEY (`receive_user_id`) REFERENCES `t_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_message_user`
--

/*!40000 ALTER TABLE `t_message_user` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_message_user` ENABLE KEYS */;

--
-- Table structure for table `t_order`
--

DROP TABLE IF EXISTS `t_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_order` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_no` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '订单号',
  `user_id` int NOT NULL,
  `order_type` tinyint(1) NOT NULL COMMENT '1影片观影券 2会员套餐',
  `title` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '订单标题',
  `total_amount` decimal(10,2) NOT NULL COMMENT '原价',
  `discount_amount` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '优惠合计（会员折扣+券）',
  `pay_amount` decimal(10,2) NOT NULL COMMENT '实付',
  `user_coupon_id` int DEFAULT NULL COMMENT '用了哪张券',
  `status` tinyint(1) NOT NULL DEFAULT '0' COMMENT '0待支付 1已支付 2已取消',
  `create_time` datetime DEFAULT NULL,
  `pay_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_order_no` (`order_no`) USING BTREE,
  KEY `idx_order_user` (`user_id`,`status`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='订单';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_order`
--

/*!40000 ALTER TABLE `t_order` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_order` ENABLE KEYS */;

--
-- Table structure for table `t_order_item`
--

DROP TABLE IF EXISTS `t_order_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_order_item` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `order_no` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `item_type` tinyint(1) NOT NULL COMMENT '1影片 2会员套餐',
  `item_id` int DEFAULT NULL COMMENT '影片ID，或会员套餐的月数',
  `item_name` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  `quantity` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_order_item_no` (`order_no`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='订单明细';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_order_item`
--

/*!40000 ALTER TABLE `t_order_item` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_order_item` ENABLE KEYS */;

--
-- Table structure for table `t_role`
--

DROP TABLE IF EXISTS `t_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_role` (
  `role_id` int NOT NULL,
  `user_id` int DEFAULT NULL,
  `role_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `role_describe` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`role_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_role`
--

/*!40000 ALTER TABLE `t_role` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_role` ENABLE KEYS */;

--
-- Table structure for table `t_tag`
--

DROP TABLE IF EXISTS `t_tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_tag` (
  `tag_id` int NOT NULL AUTO_INCREMENT,
  `tag_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`tag_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=9831 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_tag`
--

/*!40000 ALTER TABLE `t_tag` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_tag` ENABLE KEYS */;

--
-- Table structure for table `t_user`
--

DROP TABLE IF EXISTS `t_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_uuid` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `user_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '用户名',
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `real_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '真实姓名',
  `age` int DEFAULT NULL,
  `sex` tinyint(1) DEFAULT NULL COMMENT '1.男 0女',
  `birth_day` datetime DEFAULT NULL,
  `phone` char(11) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `status` int DEFAULT NULL COMMENT '1.启用 2禁用',
  `image_path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '头像地址',
  `create_time` datetime DEFAULT NULL,
  `modify_time` datetime DEFAULT NULL,
  `last_active_time` datetime DEFAULT NULL,
  `deleted` tinyint(1) DEFAULT NULL COMMENT '是否删除',
  `city` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `job` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `wx_open_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '微信openid',
  `role` int DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=685 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_user`
--

/*!40000 ALTER TABLE `t_user` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_user` ENABLE KEYS */;

--
-- Table structure for table `t_user_coupon`
--

DROP TABLE IF EXISTS `t_user_coupon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_user_coupon` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL COMMENT 't_user.id',
  `coupon_id` int NOT NULL COMMENT 't_coupon.id',
  `title` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '领券时的券名快照',
  `threshold` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '门槛快照',
  `amount` decimal(10,2) NOT NULL COMMENT '抵扣金额快照',
  `status` tinyint(1) NOT NULL DEFAULT '0' COMMENT '0未使用 1已使用 2已过期',
  `receive_time` datetime DEFAULT NULL,
  `expire_time` datetime DEFAULT NULL,
  `use_time` datetime DEFAULT NULL,
  `order_no` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '用在哪个订单上',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_user_coupon_user` (`user_id`,`status`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='用户优惠券';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_user_coupon`
--

/*!40000 ALTER TABLE `t_user_coupon` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_user_coupon` ENABLE KEYS */;

--
-- Table structure for table `t_user_event_log`
--

DROP TABLE IF EXISTS `t_user_event_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_user_event_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL COMMENT '用户id',
  `user_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '用户名',
  `real_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '真实姓名',
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '内容',
  `create_time` datetime DEFAULT NULL COMMENT '时间',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `fk_user_log` (`user_id`) USING BTREE,
  CONSTRAINT `fk_user_log` FOREIGN KEY (`user_id`) REFERENCES `t_user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=109 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_user_event_log`
--

/*!40000 ALTER TABLE `t_user_event_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_user_event_log` ENABLE KEYS */;

--
-- Table structure for table `t_user_role_relation`
--

DROP TABLE IF EXISTS `t_user_role_relation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_user_role_relation` (
  `role_id` int NOT NULL,
  `user_id` int DEFAULT NULL,
  KEY `fk_relation_user_id` (`user_id`) USING BTREE,
  KEY `fk_relation_role_id` (`role_id`) USING BTREE,
  CONSTRAINT `fk_relation_role_id` FOREIGN KEY (`role_id`) REFERENCES `t_role` (`role_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_relation_user_id` FOREIGN KEY (`user_id`) REFERENCES `t_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_user_role_relation`
--

/*!40000 ALTER TABLE `t_user_role_relation` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_user_role_relation` ENABLE KEYS */;

--
-- Table structure for table `t_user_tag`
--

DROP TABLE IF EXISTS `t_user_tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_user_tag` (
  `user_id` int NOT NULL,
  `tag_id` int DEFAULT NULL,
  `user_property_flag` tinyint(1) DEFAULT NULL COMMENT '是否分析得到的数据是1否0',
  KEY `fk_user_likes` (`user_id`) USING BTREE,
  KEY `fk_t_user_tagId` (`tag_id`) USING BTREE,
  CONSTRAINT `fk_t_user_tagId` FOREIGN KEY (`tag_id`) REFERENCES `t_tag` (`tag_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_user_likes` FOREIGN KEY (`user_id`) REFERENCES `t_user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_user_tag`
--

/*!40000 ALTER TABLE `t_user_tag` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_user_tag` ENABLE KEYS */;

--
-- Table structure for table `t_user_token`
--

DROP TABLE IF EXISTS `t_user_token`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_user_token` (
  `id` int NOT NULL AUTO_INCREMENT,
  `token` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `user_id` int DEFAULT NULL COMMENT '用户Id',
  `wx_open_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '微信openId',
  `create_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `user_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '用户名',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `fk_toke_user_id` (`user_id`) USING BTREE,
  CONSTRAINT `fk_toke_user_id` FOREIGN KEY (`user_id`) REFERENCES `t_user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_user_token`
--

/*!40000 ALTER TABLE `t_user_token` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_user_token` ENABLE KEYS */;

--
-- Table structure for table `t_user_video_operation`
--

DROP TABLE IF EXISTS `t_user_video_operation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_user_video_operation` (
  `id` int NOT NULL COMMENT '用户ID',
  `video_id` int NOT NULL COMMENT '视频ID',
  `thumb_up` int DEFAULT NULL COMMENT '是否点赞,1为点赞，0或null为不点赞',
  `collection` int DEFAULT NULL COMMENT '是否收藏,1为收藏,0或null为不收藏',
  `praise_bad_reviews` int DEFAULT NULL COMMENT '1为好评，0为差评',
  `comment` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '评论内容',
  `finally_active_time` datetime(6) DEFAULT NULL COMMENT '最后活跃时间',
  `rating` double DEFAULT NULL COMMENT '用户评分',
  PRIMARY KEY (`id`,`video_id`) USING BTREE,
  KEY `fk_user_operation_video_id` (`video_id`) USING BTREE,
  CONSTRAINT `fk_user_operation_id` FOREIGN KEY (`id`) REFERENCES `t_user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_user_operation_video_id` FOREIGN KEY (`video_id`) REFERENCES `t_video_info` (`video_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_user_video_operation`
--

/*!40000 ALTER TABLE `t_user_video_operation` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_user_video_operation` ENABLE KEYS */;

--
-- Table structure for table `t_video_info`
--

DROP TABLE IF EXISTS `t_video_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_video_info` (
  `video_id` int NOT NULL AUTO_INCREMENT,
  `video_name` varchar(255) DEFAULT NULL COMMENT '影片名',
  `original_title` varchar(255) DEFAULT NULL COMMENT '原始标题',
  `overview` text COMMENT '简介',
  `tagline` varchar(500) DEFAULT NULL COMMENT '标语',
  `budget` bigint DEFAULT '0' COMMENT '预算',
  `revenue` bigint DEFAULT '0' COMMENT '票房',
  `popularity` double DEFAULT '0' COMMENT '热度值',
  `vote_average` double DEFAULT '0' COMMENT '平均评分',
  `vote_count` int DEFAULT '0' COMMENT '评分人数',
  `runtime` int DEFAULT '0' COMMENT '片长(分钟)',
  `release_date` date DEFAULT NULL COMMENT '上映日期',
  `original_language` varchar(10) DEFAULT NULL COMMENT '原始语言',
  `poster_path` varchar(500) DEFAULT NULL COMMENT '海报路径',
  `heat_score` double DEFAULT '0' COMMENT '综合热度评分',
  `video_category` tinyint(1) DEFAULT NULL COMMENT '1.教学视频，2，娱乐短视频，3，电影 4电视剧',
  `create_time` date DEFAULT NULL,
  `creator_id` int DEFAULT NULL COMMENT '视频上传者的id',
  `last_modify_time` datetime DEFAULT NULL,
  `video_url` varchar(500) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL COMMENT '视频保存的地址',
  PRIMARY KEY (`video_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=459591 DEFAULT CHARSET=utf8mb3 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_video_info`
--

/*!40000 ALTER TABLE `t_video_info` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_video_info` ENABLE KEYS */;

--
-- Table structure for table `t_video_play`
--

DROP TABLE IF EXISTS `t_video_play`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_video_play` (
  `video_id` int DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  `last_play_time` datetime DEFAULT NULL,
  `play_times` int NOT NULL,
  KEY `fk_media_play_mediaId` (`user_id`) USING BTREE,
  KEY `fk_video_play_video_id` (`video_id`) USING BTREE,
  CONSTRAINT `fk_media_play_mediaId` FOREIGN KEY (`user_id`) REFERENCES `t_user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_video_play_video_id` FOREIGN KEY (`video_id`) REFERENCES `t_video_info` (`video_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_video_play`
--

/*!40000 ALTER TABLE `t_video_play` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_video_play` ENABLE KEYS */;

--
-- Table structure for table `t_video_tag`
--

DROP TABLE IF EXISTS `t_video_tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_video_tag` (
  `video_id` int NOT NULL,
  `tag_id` int DEFAULT NULL COMMENT '视频属性标签',
  `video_property_flag` tinyint(1) DEFAULT NULL COMMENT '是否未分析得到的数据是1不是2',
  KEY `fk_video_property_id` (`video_id`) USING BTREE,
  KEY `fk_t_video_tagId` (`tag_id`) USING BTREE,
  CONSTRAINT `fk_t_video_tagId` FOREIGN KEY (`tag_id`) REFERENCES `t_tag` (`tag_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_video_property_id` FOREIGN KEY (`video_id`) REFERENCES `t_video_info` (`video_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_video_tag`
--

/*!40000 ALTER TABLE `t_video_tag` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_video_tag` ENABLE KEYS */;

--
-- Dumping routines for database 'vidio_mangage_db'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-22  9:29:41
