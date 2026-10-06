-- ============================================================================
-- movie-system 小程序 AI 客服模块：FAQ 知识库 + 对话日志
--
-- 适用库：movie_analytics_db（dev profile）
-- 执行：mysql -uroot -p电影_analytics_db < sql/ai_chat.sql
--       （或带环境变量：call local_env.cmd && mysql -uroot -p%DB_PASSWORD% ...）
--
-- 设计说明：
--   * 私有知识 = t_chat_faq（运营规则类，人工维护）+ t_movie（影片数据，已有）。
--     回答问题时先在两边做关键词检索，把命中的资料拼进 prompt 再交给 GLM，
--     模型只负责组织语言 —— 知识变了改表就行，不用重训任何东西（RAG 路线）。
--   * t_chat_faq.hit 记录命中次数，方便后续观察哪些问题高频、该补充哪些条目。
--   * t_chat_log 落每轮问答（含来源 faq/glm/fallback），方便排查与复盘。
--   * 与 wx_shop.sql 同一约定：不带 deleted 字段，避开 MyBatis-Plus 逻辑删除。
-- ============================================================================

-- ---------------------------------------------------------------------------
-- FAQ 知识库
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS `t_chat_faq`;
CREATE TABLE `t_chat_faq` (
  `id`         bigint       NOT NULL AUTO_INCREMENT COMMENT '主键',
  `keywords`   varchar(500) NOT NULL COMMENT '命中关键词，竖线分隔，如 会员|开通|续费',
  `question`   varchar(500) NOT NULL COMMENT '标准问法（展示/检索用）',
  `answer`     text         NOT NULL COMMENT '标准答案（命中后作为资料给模型，兜底时直接返回）',
  `category`   varchar(64)  DEFAULT 'general' COMMENT '分类：member/coupon/order/platform/movie',
  `enabled`    tinyint(1)   DEFAULT 1 COMMENT '1 启用 0 停用',
  `hit`        int          DEFAULT 0 COMMENT '命中次数',
  `created_at` datetime     DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_faq_enabled` (`enabled`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI客服FAQ知识库';

-- ---------------------------------------------------------------------------
-- 对话日志
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS `t_chat_log`;
CREATE TABLE `t_chat_log` (
  `id`         bigint       NOT NULL AUTO_INCREMENT,
  `user_id`    int          DEFAULT NULL COMMENT '用户id（演示版由前端传）',
  `question`   varchar(1000) NOT NULL COMMENT '用户问题',
  `answer`     text         COMMENT '最终回答',
  `source`     varchar(16)  DEFAULT NULL COMMENT 'glm=模型生成 faq=直接命中 f ailed=调用失败',
  `refs`       varchar(500) DEFAULT NULL COMMENT '引用了哪些资料（faq条目/影片名），逗号分隔',
  `cost_ms`    int          DEFAULT NULL COMMENT '接口耗时',
  `created_at` datetime     DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_chat_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI客服对话日志';

-- ---------------------------------------------------------------------------
-- 种子 FAQ：内容取自小程序实际规则（wx_shop 设计说明 + 会员页文案）
-- ---------------------------------------------------------------------------
INSERT INTO `t_chat_faq` (`keywords`, `question`, `answer`, `category`) VALUES
('会员|开通会员|办会员|vip', '怎么开通会员？会员有什么用？',
 '会员有月卡/季卡/年卡三种，价格分别是 15 元、40 元、128 元。开通后在有效期内：买观影券全场 8 折，每月自动发优惠券。在「会员」页面选择套餐下单即可开通。', 'member'),
('会员|续费|到期|过期', '会员到期了怎么续费？',
 '在「我的」页面点「续费」，或进「会员」页重新选套餐下单即可，新时长会在现有有效期上顺延。', 'member'),
('优惠券|券|领券|满减', '优惠券怎么领？怎么用？',
 '领券：首页或「我的-我的券」进入领券中心，点击领取。用法：优惠券是满减券，下单金额达到使用门槛后自动抵扣，每单限用一张。领取后一般 30 天内有效，请在「我的券」里查看具体金额与有效期。', 'coupon'),
('观影券|买票|票价|多少钱|价格', '观影券多少钱一张？',
 '观影券单价按影片评分定价：评分 8.5 分及以上 12 元，7.5~8.5 分 9 元，其余 6 元。会员在此基础上再打 8 折。在影片详情页点「购买观影券」即可下单。', 'coupon'),
('退|退款|取消订单', '订单能退吗？',
 '未支付订单可以直接取消；已支付订单目前为演示流程，如需退款请联系管理员在后台处理。', 'order'),
('支付|微信支付|付不了|虚拟支付', '怎么支付？',
 '当前为演示版本，下单即模拟支付成功，不真实扣款。正式支付能力（微信虚拟支付）正在开通流程中，开通后会员和观影券购买将支持小程序内直接支付。', 'order'),
('登录|openid|授权', '需要注册登录吗？',
 '不需要注册。打开小程序自动通过微信登录（openid），无需输入账号密码。', 'platform'),
('什么|介绍|功能|能干什么', '这个小程序是干什么的？',
 '「阿强观影」是一个电影票务演示小程序：可以浏览 1 万部影片的资料库（评分、票房、类型、上映时间），购买观影券、开通会员、领优惠券，还有票房预测和个性化推荐等智能功能。', 'platform'),
('推荐|猜你喜欢|个性化', '推荐功能是怎么算的？',
 '系统会根据你的浏览、购票等行为记录，用协同过滤等算法推荐你可能感兴趣的影片，在首页「猜你喜欢」里可以看到。', 'platform'),
('票房|预测|预测票房', '票房预测是怎么做的？',
 '系统内置票房预测模型，基于影片的预算、类型、档期、热度等特征，用机器学习模型（历史 5000+ 影片训练）预测票房区间。在影片详情页可以看到预测结果。', 'movie');

-- ---------------------------------------------------------------------------
-- 2026-09-29 补：漫威/超级英雄片单（用户实际提问"漫威相关的电影有哪些"，
-- 片名检索答不了系列类问题，按 RAG 思路把这条知识补进 FAQ；片单来自
-- t_video_info 实查，改库后如片单变化记得同步更新本条）
-- ---------------------------------------------------------------------------
INSERT INTO `t_chat_faq` (`keywords`, `question`, `answer`, `category`) VALUES
('漫威|漫威宇宙|超级英雄|marvel|复仇者|钢铁侠|美国队长|雷神|蚁人|银河护卫队',
 '库里有哪些漫威/超级英雄电影？',
 '平台库里的漫威超级英雄片有：《复仇者联盟》四部（终局之战 8.2 分最高）、《钢铁侠》《钢铁侠3》《美国队长2、3》《雷神2》《蚁人》《银河护卫队》《死侍》，还有《蜘蛛侠》前两部和新版动画《蜘蛛侠：纵横宇宙》（8.3 分，库内评分最高）。在首页搜索框输入片名就能找到。', 'movie');
