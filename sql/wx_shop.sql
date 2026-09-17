-- ============================================================================
-- movie-system 小程序商城模块：会员 / 优惠券 / 订单
--
-- 适用库：dev profile 用的是 vidio_mangage_db（注意是 vidio，历史拼写就是这样），
--         生产/预发 profile 里写的是 video_mangage_db，按你实际连的库执行。
-- 执行：mysql -uroot vidio_mangage_db < sql/wx_shop.sql
--
-- 设计说明：
--   * 「商品」复用现有数据，不新建商品表 ——
--       1) 影片观影券：直接用 t_video_info，单价按评分算（>=8.5 → 12 元，
--          >=7.5 → 9 元，其余 6 元），会员再打 8 折；
--       2) 会员套餐：1/3/12 个月，价格写在 Java 常量里（15/40/128 元）。
--   * 券是「满减券」：满 threshold 减 amount，领取后 valid_days 天内有效。
--   * 订单状态：0 待支付 1 已支付 2 已取消。演示版下单即置为已支付（模拟支付成功），
--     正式接入微信支付时应改成「先落待支付 → 支付回调里再置已支付」。
--   * 新表都不带 deleted 字段，避免被 MyBatis-Plus 的全局逻辑删除命中。
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 顺手修一个历史 schema bug：t_user.wx_open_id 是 varchar(0)，存不下任何值，
-- 做微信登录必须能按 openid 找用户。
-- ---------------------------------------------------------------------------
ALTER TABLE `t_user` MODIFY COLUMN `wx_open_id` varchar(64)
    CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '微信openid';

-- ---------------------------------------------------------------------------
-- 优惠券模板
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS `t_coupon`;
CREATE TABLE `t_coupon` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '券名',
  `threshold` decimal(10,2) NOT NULL DEFAULT 0.00 COMMENT '使用门槛，0=无门槛',
  `amount` decimal(10,2) NOT NULL COMMENT '抵扣金额',
  `valid_days` int(11) NOT NULL DEFAULT 7 COMMENT '领取后有效天数',
  `total_count` int(11) NOT NULL DEFAULT 0 COMMENT '发行总量，0=不限量',
  `received_count` int(11) NOT NULL DEFAULT 0 COMMENT '已领取数量',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1上架 0下架',
  `create_time` datetime(0) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '优惠券模板' ROW_FORMAT = Dynamic;

-- 种子券
INSERT INTO `t_coupon` (`title`, `threshold`, `amount`, `valid_days`, `total_count`, `received_count`, `status`, `create_time`) VALUES
('新人无门槛券', 0.00, 3.00, 7, 0, 0, 1, NOW()),
('满20减5券', 20.00, 5.00, 15, 0, 0, 1, NOW()),
('会员专享 满30减10', 30.00, 10.00, 30, 0, 0, 1, NOW());

-- ---------------------------------------------------------------------------
-- 用户持有的券
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS `t_user_coupon`;
CREATE TABLE `t_user_coupon` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL COMMENT 't_user.id',
  `coupon_id` int(11) NOT NULL COMMENT 't_coupon.id',
  `title` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '领券时的券名快照',
  `threshold` decimal(10,2) NOT NULL DEFAULT 0.00 COMMENT '门槛快照',
  `amount` decimal(10,2) NOT NULL COMMENT '抵扣金额快照',
  `status` tinyint(1) NOT NULL DEFAULT 0 COMMENT '0未使用 1已使用 2已过期',
  `receive_time` datetime(0) NULL DEFAULT NULL,
  `expire_time` datetime(0) NULL DEFAULT NULL,
  `use_time` datetime(0) NULL DEFAULT NULL,
  `order_no` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '用在哪个订单上',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_coupon_user` (`user_id`, `status`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '用户优惠券' ROW_FORMAT = Dynamic;

-- ---------------------------------------------------------------------------
-- 会员（一个用户一行，续费就往后延 expire_time）
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS `t_member`;
CREATE TABLE `t_member` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL COMMENT 't_user.id',
  `level` tinyint(1) NOT NULL DEFAULT 1 COMMENT '会员等级，目前只有 1',
  `expire_time` datetime(0) NOT NULL COMMENT '到期时间',
  `create_time` datetime(0) NULL DEFAULT NULL,
  `update_time` datetime(0) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_member_user` (`user_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会员' ROW_FORMAT = Dynamic;

-- ---------------------------------------------------------------------------
-- 订单
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS `t_order`;
CREATE TABLE `t_order` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_no` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '订单号',
  `user_id` int(11) NOT NULL,
  `order_type` tinyint(1) NOT NULL COMMENT '1影片观影券 2会员套餐',
  `title` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '订单标题',
  `total_amount` decimal(10,2) NOT NULL COMMENT '原价',
  `discount_amount` decimal(10,2) NOT NULL DEFAULT 0.00 COMMENT '优惠合计（会员折扣+券）',
  `pay_amount` decimal(10,2) NOT NULL COMMENT '实付',
  `user_coupon_id` int(11) NULL DEFAULT NULL COMMENT '用了哪张券',
  `status` tinyint(1) NOT NULL DEFAULT 0 COMMENT '0待支付 1已支付 2已取消',
  `create_time` datetime(0) NULL DEFAULT NULL,
  `pay_time` datetime(0) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_order_no` (`order_no`) USING BTREE,
  INDEX `idx_order_user` (`user_id`, `status`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '订单' ROW_FORMAT = Dynamic;

-- ---------------------------------------------------------------------------
-- 订单明细
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS `t_order_item`;
CREATE TABLE `t_order_item` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL,
  `order_no` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `item_type` tinyint(1) NOT NULL COMMENT '1影片 2会员套餐',
  `item_id` int(11) NULL DEFAULT NULL COMMENT '影片ID，或会员套餐的月数',
  `item_name` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  `quantity` int(11) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_order_item_no` (`order_no`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '订单明细' ROW_FORMAT = Dynamic;
