-- =====================================================================
-- 《电影票房预测与智能推荐系统》新项目数据库  movie_analytics_db
-- 课程作业 · 第四步①：生成数据库表（15 张，满足 ≥8 张要求）
-- 字符集 utf8mb4 / 引擎 InnoDB；电影主表以 TMDB id 为主键
-- 旧库 vidio_mangage_db 在本脚本执行后完整备份并删除（见第四步②）
-- =====================================================================
CREATE DATABASE IF NOT EXISTS movie_analytics_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE movie_analytics_db;

-- 1. 电影主表
CREATE TABLE t_movie (
  id               BIGINT       NOT NULL COMMENT 'TMDB 电影 id（主键）',
  video_name       VARCHAR(255) NOT NULL COMMENT '片名',
  original_title   VARCHAR(255)          DEFAULT NULL COMMENT '原始片名',
  overview         TEXT                  COMMENT '剧情简介',
  tagline          VARCHAR(500)          DEFAULT NULL,
  release_date     DATE                  DEFAULT NULL COMMENT '上映日期',
  year             SMALLINT              DEFAULT NULL COMMENT '上映年',
  month            TINYINT               DEFAULT NULL COMMENT '上映月',
  runtime          INT                   DEFAULT NULL COMMENT '时长(分钟)',
  budget           BIGINT                DEFAULT 0    COMMENT '预算(美元)',
  revenue          BIGINT                DEFAULT 0    COMMENT '票房(美元)',
  log_budget       FLOAT                 DEFAULT NULL COMMENT 'log10 预算',
  log_revenue      FLOAT                 DEFAULT NULL COMMENT 'log10 票房',
  popularity       FLOAT                 DEFAULT 0    COMMENT 'TMDB 热度',
  vote_average     FLOAT                 DEFAULT 0    COMMENT '均分',
  vote_count       INT                   DEFAULT 0    COMMENT '评分人数',
  original_language VARCHAR(16)          DEFAULT NULL COMMENT '原声语言',
  main_genre       VARCHAR(64)          DEFAULT NULL COMMENT '主类型（预处理派生，取 TMDB 首个类型）',
  status           VARCHAR(32)           DEFAULT NULL COMMENT '发行状态',
  homepage         VARCHAR(500)          DEFAULT NULL,
  poster_path      VARCHAR(255)          DEFAULT NULL COMMENT '海报路径',
  is_collection    TINYINT(1)            DEFAULT 0    COMMENT '是否系列片',
  created_at       DATETIME    DEFAULT CURRENT_TIMESTAMP,
  updated_at       DATETIME    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_year (year),
  KEY idx_revenue (revenue),
  KEY idx_name (video_name),
  KEY idx_main_genre (main_genre)
) ENGINE=InnoDB COMMENT='电影主表';

-- 2. 类型字典
CREATE TABLE t_genre (
  id   INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(64) NOT NULL UNIQUE COMMENT '类型名(如 Action/Drama)'
) ENGINE=InnoDB COMMENT='电影类型字典';

-- 3. 电影-类型（多对多）
CREATE TABLE t_movie_genre (
  movie_id BIGINT NOT NULL,
  genre_id INT    NOT NULL,
  PRIMARY KEY (movie_id, genre_id),
  KEY idx_genre (genre_id)
) ENGINE=InnoDB COMMENT='电影-类型关联';

-- 4. 人员（演员/导演/职员）
CREATE TABLE t_person (
  id     INT AUTO_INCREMENT PRIMARY KEY,
  name   VARCHAR(128) NOT NULL COMMENT '姓名',
  gender TINYINT      DEFAULT 0 COMMENT '0未知/1女/2男',
  UNIQUE KEY uk_name (name)
) ENGINE=InnoDB COMMENT='演职人员';

-- 5. 电影-演员
CREATE TABLE t_movie_cast (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  movie_id       BIGINT       NOT NULL,
  person_id      INT          NOT NULL,
  character_name VARCHAR(255) DEFAULT NULL COMMENT '扮演角色',
  cast_order     INT          DEFAULT 0    COMMENT '番位顺序',
  KEY idx_movie (movie_id),
  KEY idx_person (person_id)
) ENGINE=InnoDB COMMENT='电影-演员关联';

-- 6. 电影-职员
CREATE TABLE t_movie_crew (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  movie_id   BIGINT       NOT NULL,
  person_id  INT          NOT NULL,
  department VARCHAR(64)  DEFAULT NULL COMMENT '部门(Directing等)',
  job        VARCHAR(64)  DEFAULT NULL COMMENT '职务(Director等)',
  KEY idx_movie (movie_id),
  KEY idx_person (person_id),
  KEY idx_job (job)
) ENGINE=InnoDB COMMENT='电影-职员关联';

-- 7. 关键词字典
CREATE TABLE t_keyword (
  id   INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(128) NOT NULL UNIQUE
) ENGINE=InnoDB COMMENT='关键词字典';

-- 8. 电影-关键词（多对多）
CREATE TABLE t_movie_keyword (
  movie_id   BIGINT NOT NULL,
  keyword_id INT    NOT NULL,
  PRIMARY KEY (movie_id, keyword_id),
  KEY idx_keyword (keyword_id)
) ENGINE=InnoDB COMMENT='电影-关键词关联';

-- 9. 制作公司
CREATE TABLE t_company (
  id   INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(191) NOT NULL UNIQUE
) ENGINE=InnoDB COMMENT='制作公司';

-- 10. 电影-公司（多对多）
CREATE TABLE t_movie_company (
  movie_id   BIGINT NOT NULL,
  company_id INT    NOT NULL,
  PRIMARY KEY (movie_id, company_id),
  KEY idx_company (company_id)
) ENGINE=InnoDB COMMENT='电影-公司关联';

-- 11. 国家/地区字典
CREATE TABLE t_country (
  id       INT AUTO_INCREMENT PRIMARY KEY,
  iso_code VARCHAR(8)   DEFAULT NULL COMMENT 'ISO 代码(US/CN…)',
  name     VARCHAR(128) NOT NULL UNIQUE
) ENGINE=InnoDB COMMENT='制作国家字典';

-- 12. 电影-国家（多对多）
CREATE TABLE t_movie_country (
  movie_id   BIGINT NOT NULL,
  country_id INT    NOT NULL,
  PRIMARY KEY (movie_id, country_id),
  KEY idx_country (country_id)
) ENGINE=InnoDB COMMENT='电影-国家关联';

-- 13. 用户（站内评分用户；命名为 t_movie_user 以避开框架登录表 t_user，避免迁入同库时重名）
CREATE TABLE t_movie_user (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  username   VARCHAR(64)  NOT NULL UNIQUE,
  password   VARCHAR(255) NOT NULL COMMENT 'RSA 加密存储',
  nickname   VARCHAR(64)  DEFAULT NULL,
  role       VARCHAR(16)  DEFAULT 'user' COMMENT 'user/admin',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='站内评分用户（与框架登录表 t_user 区分）';

-- 14. 用户评分（推荐算法数据源；user_id → t_movie_user.id）
CREATE TABLE t_rating (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  user_id    INT      NOT NULL,
  movie_id   BIGINT   NOT NULL,
  score      DECIMAL(3,1) NOT NULL COMMENT '评分 0.5~10',
  comment    VARCHAR(500) DEFAULT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_user_movie (user_id, movie_id),
  KEY idx_movie (movie_id)
) ENGINE=InnoDB COMMENT='用户评分';

-- 15. 票房预测记录（算法服务落库）
CREATE TABLE t_prediction_log (
  id                    INT AUTO_INCREMENT PRIMARY KEY,
  movie_id              BIGINT      DEFAULT NULL COMMENT '关联电影(可空=未入库影片)',
  model_name            VARCHAR(64) NOT NULL COMMENT '模型名(如 RandomForest)',
  input_features        JSON                 COMMENT '输入特征快照',
  predicted_log_revenue FLOAT       DEFAULT NULL COMMENT '预测 log10 票房',
  predicted_revenue     BIGINT      DEFAULT NULL COMMENT '预测票房(美元)',
  created_at            DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_movie (movie_id),
  KEY idx_model (model_name)
) ENGINE=InnoDB COMMENT='票房预测记录';
