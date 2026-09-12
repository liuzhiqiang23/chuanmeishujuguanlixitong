# -*- coding: utf-8 -*-
"""
数据清洗与特征工程脚本（可复用模块）
====================================
本脚本服务于电影分析系统的三个需求：
    1) 数据分析与可视化（EDA）
    2) 票房预测
    3) 电影推荐

处理内容：
    - 解析 TMDB 风格字段（genres/Keywords/cast/crew 等为 Python repr 列表）
    - 日期解析（release_date: m/d/yy -> year / month）
    - 数值清洗（budget<=0、runtime<=0 视为缺失）
    - 派生特征（主类型、类型数、导演、主演、制作国、公司、系列片标记等）

用法：
    python algorithm/FeatureEDA/preprocess.py   # 运行并将结果存到 data/processed
    from preprocess import build_data           # 供 EDA/建模脚本直接 import 复用
"""
import os
import sys
import ast

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

# ---- 系统工程目录常量 ----
#   movie-system/ 系统根目录（即 system）
#   ├── data/                  # 数据集（原始 CSV 放此处）
#   │   └── processed/         # 清洗产物（FeatureEDA/prediction/recommendation 共享）
#   └── algorithm/
#       └── FeatureEDA/        # 本模块所在
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))    # .../algorithm/FeatureEDA
ALGO_DIR = os.path.dirname(SCRIPT_DIR)                     # .../algorithm
SYSTEM_ROOT = os.path.dirname(ALGO_DIR)                    # 系统根目录
DATA_DIR = os.path.join(SYSTEM_ROOT, "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

# 需要解析的“列表式”字段（TMDB 风格 repr 字符串）
LIST_COLS = [
    "belongs_to_collection", "genres", "production_companies",
    "production_countries", "spoken_languages", "Keywords", "cast", "crew",
]

# 年份有效范围（超过 2026 属未来异常值，最早老电影动态判定）
YEAR_MAX = 2026


def parse_list(s):
    """把 repr 风格字符串安全解析为 list，空/缺失返回 []"""
    if pd.isna(s) or str(s).strip() == "":
        return []
    try:
        v = ast.literal_eval(s)
        return v if isinstance(v, list) else []
    except Exception:
        return []


def names_of(lst):
    """从 [{...'name': xx}] 中抽取 name 列表"""
    return [d.get("name") for d in lst if isinstance(d, dict) and d.get("name")]


def preprocess(df: pd.DataFrame, is_train: bool = True) -> pd.DataFrame:
    df = df.copy()

    # ---------- 1. 解析列表字段 ----------
    for col in LIST_COLS:
        df[col] = df[col].apply(parse_list)

    # ---------- 2. 日期 -> 年份/月份 ----------
    df["date"] = pd.to_datetime(df["release_date"], format="mixed", errors="coerce")
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    # 异常年份（未来数据）置为缺失
    df.loc[df["year"] > YEAR_MAX, ["year", "month", "date"]] = np.nan

    # ---------- 3. 数值清洗 ----------
    # 预算/时长为 0 或负数视为缺失（0 通常是未公开/录入缺失）
    df.loc[df["budget"] <= 0, "budget"] = np.nan
    df.loc[df["runtime"] <= 0, "runtime"] = np.nan

    # ---------- 4. 类型相关特征 ----------
    df["genres_list"] = df["genres"].apply(names_of)
    df["main_genre"] = df["genres_list"].apply(lambda x: x[0] if x else "Unknown")
    df["n_genres"] = df["genres_list"].apply(len)

    # ---------- 5. 关键词 ----------
    df["keywords_list"] = df["Keywords"].apply(names_of)
    df["n_keywords"] = df["keywords_list"].apply(len)

    # ---------- 6. 制作国家（取主要国家 = 列表第一项） ----------
    df["countries_list"] = df["production_countries"].apply(names_of)
    df["main_country"] = df["countries_list"].apply(lambda x: x[0] if x else "Unknown")
    df["n_countries"] = df["countries_list"].apply(len)

    # ---------- 7. 制作公司 ----------
    df["companies_list"] = df["production_companies"].apply(names_of)
    df["n_companies"] = df["companies_list"].apply(len)

    # ---------- 8. 语言 ----------
    df["languages_list"] = df["spoken_languages"].apply(names_of)
    df["n_languages"] = df["languages_list"].apply(len)
    df["is_english"] = df["languages_list"].apply(lambda x: "English" in x)

    # ---------- 9. 是否为系列电影（belongs_to_collection 非空） ----------
    df["is_collection"] = df["belongs_to_collection"].apply(lambda x: len(x) > 0)

    # ---------- 10. 导演（crew 中 job == 'Director'） ----------
    def get_director(lst):
        for d in lst:
            if isinstance(d, dict) and d.get("job") == "Director":
                return d.get("name")
        return np.nan

    df["director"] = df["crew"].apply(get_director)

    # ---------- 11. 主演特征（cast 已按 order 升序，取前 3） ----------
    def top_cast(lst, k=3):
        out = []
        for d in lst:
            if isinstance(d, dict) and d.get("name"):
                out.append(d["name"])
            if len(out) >= k:
                break
        return out

    df["top3_cast"] = df["cast"].apply(lambda x: "|".join(top_cast(x)))
    df["cast_size"] = df["cast"].apply(len)

    # ---------- 12. 对数变换特征（长尾数据可视化/建模常用） ----------
    df["log_budget"] = np.log10(df["budget"])
    df["log_popularity"] = np.log10(df["popularity"].clip(lower=1e-6))
    if is_train and "revenue" in df.columns:
        df["log_revenue"] = np.log10(df["revenue"])

    return df


def build_data():
    """构建并返回清洗后的 train / test，同时落盘到 data/processed（跨模块共享）"""
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    train = preprocess(pd.read_csv(os.path.join(DATA_DIR, "train.csv")), is_train=True)
    test = preprocess(pd.read_csv(os.path.join(DATA_DIR, "test.csv")), is_train=False)

    train.to_csv(os.path.join(PROCESSED_DIR, "train_clean.csv"), index=False, encoding="utf-8-sig")
    test.to_csv(os.path.join(PROCESSED_DIR, "test_clean.csv"), index=False, encoding="utf-8-sig")
    return train, test


def _summary(df: pd.DataFrame, name: str):
    print(f"\n[cleaned {name}] shape = {df.shape}")
    print(f"年份范围: {int(df['year'].min())} ~ {int(df['year'].max())}  (缺失 {df['year'].isna().sum()})")
    print(f"预算缺失(<=0): {df['budget'].isna().sum()}  时长缺失(<=0): {df['runtime'].isna().sum()}")
    print(f"导演缺失: {df['director'].isna().sum()}  主类型 Unknown: {(df['main_genre'] == 'Unknown').sum()}")
    print(f"系列电影占比: {(df['is_collection'].mean() * 100):.1f}%  |  英语电影占比: {(df['is_english'].mean() * 100):.1f}%")


if __name__ == "__main__":
    train, test = build_data()
    _summary(train, "train")
    _summary(test, "test")
    print(f"\n处理结果已保存到: {PROCESSED_DIR}")
    print("train_clean.csv / test_clean.csv")
