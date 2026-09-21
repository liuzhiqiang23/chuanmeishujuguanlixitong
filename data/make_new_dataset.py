# -*- coding: utf-8 -*-
"""
从 Kaggle 数据集 rounakbanik/the-movies-dataset 生成新的 train.csv / test.csv
（作业步骤 2：随机抽取，各 5000 行，替换 data/ 下数据集）

数据源三个文件（下载后解压在本目录 new_source/ 下）：
    movies_metadata.csv  ~45,000 行，含 budget/revenue/genres 等
    credits.csv          cast / crew（按 id 关联）
    keywords.csv         Keywords（按 id 关联）

抽样规则（seed=42 可复现）：
    train.csv  从 revenue>0 的电影里随机抽 5000 行（保留 revenue，23 列，与原格式一致）
    test.csv   从剩余行里随机抽 5000 行（不含 revenue，22 列，与原格式一致）
"""
import ast
import os
import sys

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(DATA_DIR, "new_source")


def wrap_collection(v):
    """movies_metadata 的 belongs_to_collection 是 {...} 字典字符串，
    老格式（preprocess.py 解析器约定）是 [{...}] 列表 —— 这里统一转成列表 repr"""
    if pd.isna(v) or str(v).strip() in ("", "nan"):
        return ""
    try:
        p = ast.literal_eval(v) if isinstance(v, str) else v
    except Exception:
        return v
    if isinstance(p, dict):
        return repr([p])
    return v

# 与原 train.csv 一致的列顺序（revenue 除外），另加 TMDB 评分两列供 EDA 用
BASE_COLS = [
    "id", "belongs_to_collection", "budget", "genres", "homepage", "imdb_id",
    "original_language", "original_title", "overview", "popularity", "poster_path",
    "production_companies", "production_countries", "release_date", "runtime",
    "spoken_languages", "status", "tagline", "title", "Keywords", "cast", "crew",
    "vote_average", "vote_count",
]

def load_source():
    meta = pd.read_csv(os.path.join(SRC_DIR, "movies_metadata.csv"),
                       low_memory=False, dtype={"id": str})
    meta = meta[meta["id"].str.strip().str.isnumeric()].copy()
    meta["id"] = meta["id"].astype(int)
    meta = meta.drop_duplicates(subset="id")  # 源文件存在重复行，去重保证 train/test 不含同一部电影

    credits = pd.read_csv(os.path.join(SRC_DIR, "credits.csv"), dtype=str)
    id_col = "id" if "id" in credits.columns else "movie_id"
    credits[id_col] = pd.to_numeric(credits[id_col], errors="coerce")
    credits = credits.dropna(subset=[id_col])
    credits[id_col] = credits[id_col].astype(int)
    credits = credits.rename(columns={id_col: "id"})[["id", "cast", "crew"]]
    credits = credits.drop_duplicates(subset="id")  # 关联表重复 id 会让合并后行数翻倍

    kw = pd.read_csv(os.path.join(SRC_DIR, "keywords.csv"), dtype={"id": str})
    kw["id"] = pd.to_numeric(kw["id"], errors="coerce")
    kw = kw.dropna(subset=["id"])
    kw["id"] = kw["id"].astype(int)
    kw = kw.rename(columns={"keywords": "Keywords"})[["id", "Keywords"]]
    kw = kw.drop_duplicates(subset="id")

    df = meta.merge(credits, on="id", how="left").merge(kw, on="id", how="left")
    df["belongs_to_collection"] = df["belongs_to_collection"].apply(wrap_collection)
    # 数值列清洗（movies_metadata 里 budget 是字符串）
    for c in ("budget", "revenue", "popularity", "runtime", "vote_average", "vote_count"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def main():
    df = load_source()
    print("合并后总行数:", len(df))
    rev_pos = df[df["revenue"] > 0].copy()
    print("revenue>0 可用于训练的行数:", len(rev_pos))
    if len(rev_pos) < 5000 or len(df) - len(rev_pos) < 5000:
        print("错误: 行数不足 5000+5000，需要换抽样规则")
        return

    train = rev_pos.sample(n=5000, random_state=42).copy()
    rest = df.drop(train.index)
    test = rest.sample(n=5000, random_state=42).copy()

    train = train[BASE_COLS + ["revenue"]]
    test = test[BASE_COLS]

    for name, part in (("train.csv", train), ("test.csv", test)):
        out = os.path.join(DATA_DIR, name)
        backup = os.path.join(DATA_DIR, "backup_original", name)
        if os.path.exists(out) and not os.path.exists(backup):
            print("注意: 原文件备份缺失，先手动确认再覆盖:", out)
            return
        part.to_csv(out, index=False, encoding="utf-8-sig")
        print("写出 %s  %d 行 x %d 列" % (name, len(part), part.shape[1]))

    # ---- 供步骤 4（大模型初步分析）用的摘要 ----
    yr = pd.to_datetime(train["release_date"], format="mixed", errors="coerce").dt.year
    print("\n新 train.csv 概况:")
    print("  年份范围:", int(yr.min()), "~", int(yr.max()))
    print("  budget>0:", (train["budget"] > 0).sum(), "行, revenue>0:", (train["revenue"] > 0).sum(), "行")
    print("  train/test 合计覆盖电影数:", len(train) + len(test))

if __name__ == "__main__":
    main()
