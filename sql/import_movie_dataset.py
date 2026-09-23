#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
新数据集 → movie_analytics_db 导入脚本（15 张表）
=================================================
数据源：data/processed/train_clean.csv + test_clean.csv（各 5000 行，共 10000 部影片）
目标库：movie_analytics_db（第四步新建；本脚本只写新项目表，不碰框架表）

写入内容：
  t_movie（主表）+ 字典表（t_genre/t_keyword/t_person/t_company/t_country）
  + 关联表（t_movie_genre/t_movie_keyword/t_movie_cast/t_movie_crew/t_movie_company/t_movie_country）

幂等：主表 ON DUPLICATE KEY UPDATE；关联表按影片先删后插，可反复执行。

用法：
  python import_movie_dataset.py                          # 默认 root/123456 @127.0.0.1
  python import_movie_dataset.py --limit 200              # 只导前 200 部（自测用）
  python import_movie_dataset.py --password xxx --db movie_analytics_db
"""
import argparse
import ast
import json
import math
import os
import sys
import time

import pandas as pd
import pymysql

sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SYSTEM_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(SYSTEM_ROOT, "data", "processed")

MAX_CAST = 10            # 每部影片只入库前 10 位主演，控制数据量
BATCH = 1000


def _clean(v):
    """pandas 的各种空值统一成 None"""
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    if isinstance(v, str) and v.strip().lower() in ("nan", "none", "null", ""):
        return None
    return v


def _num(v, cast=float):
    v = _clean(v)
    if v is None:
        return None
    try:
        f = float(v)
        return None if math.isnan(f) else cast(f)
    except (TypeError, ValueError):
        return None


def _str(v, limit=None):
    """取字符串并做长度截断（TMDB 有些字段远超建表长度，如 character_name）"""
    v = _clean(v)
    if v is None:
        return None
    s = str(v)
    return s[:limit] if limit and len(s) > limit else s


def _int(v, default=0):
    n = _num(v, float)
    return default if n is None else int(n)


def _lit(v):
    """预处理产物里的列表字段是 Python 字面量字符串：['Action', 'Drama']"""
    v = _clean(v)
    if not v:
        return []
    try:
        parsed = ast.literal_eval(str(v))
        return [str(x).strip() for x in parsed] if isinstance(parsed, (list, tuple, set)) else []
    except (ValueError, SyntaxError):
        return [p.strip() for p in str(v).strip("[]").split(",") if p.strip()]


def _json_list(v):
    """cast/crew 列的数组字符串——预处理产物用的是 Python 字面量（单引号），
    兼容 JSON 双引号写法：两种都试。"""
    v = _clean(v)
    if not v:
        return []
    text = str(v)
    try:
        parsed = ast.literal_eval(text)
        return parsed if isinstance(parsed, list) else []
    except (ValueError, SyntaxError):
        pass
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, list) else []
    except (ValueError, TypeError):
        return []


def load_movies(limit=None):
    frames = []
    for name in ("train_clean.csv", "test_clean.csv"):
        path = os.path.join(DATA_DIR, name)
        if not os.path.exists(path):
            raise FileNotFoundError(f"缺少 {path}；请先运行 algorithm/FeatureEDA/preprocess.py")
        frames.append(pd.read_csv(path, low_memory=False))
    df = pd.concat(frames, ignore_index=True).drop_duplicates(subset="id").reset_index(drop=True)
    if limit:
        df = df.head(limit).copy()
    return df


def upsert_dict(cur, table, names, extra=None):
    """把一批名字写入字典表，返回 name -> id 映射（extra: name -> 额外列值）"""
    names = [n for n in dict.fromkeys(names) if n]
    if names:
        cur.executemany(f"INSERT IGNORE INTO {table} (name) VALUES (%s)", [(n,) for n in names])
    cur.execute(f"SELECT id, name FROM {table}")
    return {row[1]: row[0] for row in cur.fetchall()}


def main():
    ap = argparse.ArgumentParser(description="新数据集导入 movie_analytics_db（15 张表）")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=3306)
    ap.add_argument("--user", default="root")
    ap.add_argument("--password", default="123456")
    ap.add_argument("--db", default="movie_analytics_db")
    ap.add_argument("--limit", type=int, default=None, help="只导入前 N 部（自测用）")
    args = ap.parse_args()

    t0 = time.time()
    df = load_movies(args.limit)
    print(f"读入影片 {len(df)} 部（train+test 去重后）")

    conn = pymysql.connect(host=args.host, port=args.port, user=args.user,
                           password=args.password, database=args.db, charset="utf8mb4",
                           autocommit=False)
    cur = conn.cursor()

    # ---------- 1. 主表 ----------
    movie_rows = []
    for _, r in df.iterrows():
        movie_rows.append((
            _int(r["id"]), _str(r["title"] or r["original_title"], 255) or "",
            _str(r["original_title"], 255), _clean(r["overview"]), _str(r["tagline"], 500),
            _clean(r["release_date"]), _int(r["year"]) if _num(r["year"], float) is not None else None,
            _int(r["month"]) if _num(r["month"], float) is not None else None,
            _int(r["runtime"]) if _num(r["runtime"], float) is not None else None,
            _int(r["budget"]), _int(r["revenue"]),
            _num(r["log_budget"], float), _num(r["log_revenue"], float),
            _num(r["popularity"], float), _num(r["vote_average"], float), _int(r["vote_count"]),
            _str(r["original_language"], 16), _str(r["status"], 32), _str(r["homepage"], 500),
            _str(r["poster_path"], 255), 1 if _int(r["is_collection"]) else 0,
        ))
    sql_movie = """
        INSERT INTO t_movie (id, video_name, original_title, overview, tagline, release_date, year, month,
                             runtime, budget, revenue, log_budget, log_revenue, popularity, vote_average,
                             vote_count, original_language, status, homepage, poster_path, is_collection)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE video_name=VALUES(video_name), original_title=VALUES(original_title),
            overview=VALUES(overview), tagline=VALUES(tagline), release_date=VALUES(release_date),
            year=VALUES(year), month=VALUES(month), runtime=VALUES(runtime), budget=VALUES(budget),
            revenue=VALUES(revenue), log_budget=VALUES(log_budget), log_revenue=VALUES(log_revenue),
            popularity=VALUES(popularity), vote_average=VALUES(vote_average), vote_count=VALUES(vote_count),
            original_language=VALUES(original_language), status=VALUES(status), homepage=VALUES(homepage),
            poster_path=VALUES(poster_path), is_collection=VALUES(is_collection)
    """
    for i in range(0, len(movie_rows), BATCH):
        cur.executemany(sql_movie, movie_rows[i:i + BATCH])
    conn.commit()
    print(f"t_movie 写入 {len(movie_rows)} 行")

    # ---------- 2. 字典表 ----------
    genre_ids = upsert_dict(cur, "t_genre", [_str(g, 64) for row in df["genres_list"] for g in _lit(row)])
    kw_ids = upsert_dict(cur, "t_keyword", [_str(k, 128) for row in df["keywords_list"] for k in _lit(row)])
    comp_ids = upsert_dict(cur, "t_company", [_str(c, 191) for row in df["companies_list"] for c in _lit(row)])
    country_ids = upsert_dict(cur, "t_country", [_str(c, 128) for row in df["countries_list"] for c in _lit(row)])

    person_names, cast_plan, crew_plan = [], [], []
    for _, r in df.iterrows():
        mid = _int(r["id"])
        for c in _json_list(r["cast"])[:MAX_CAST]:
            name = _str(c.get("name"), 128)
            if name:
                person_names.append(name)
                cast_plan.append((mid, name, _str(c.get("character"), 255), _int(c.get("order"), 99)))
        for c in _json_list(r["crew"]):
            if _str(c.get("job"), 64) == "Director":
                name = _str(c.get("name"), 128)
                if name:
                    person_names.append(name)
                    crew_plan.append((mid, name, _str(c.get("department"), 64), "Director"))
    # 导演列兜底：crew 解析失败时用 preprocess 的 director 字段
    for _, r in df.iterrows():
        mid, name = _int(r["id"]), _str(r["director"], 128)
        if name and not any(c[0] == mid for c in crew_plan):
            person_names.append(name)
            crew_plan.append((mid, name, "Directing", "Director"))
    person_ids = upsert_dict(cur, "t_person", person_names)
    print(f"字典表: 类型 {len(genre_ids)} / 关键词 {len(kw_ids)} / 公司 {len(comp_ids)} "
          f"/ 国家 {len(country_ids)} / 人员 {len(person_ids)}")

    # ---------- 3. 关联表（先删后插，保证幂等） ----------
    ids = [_int(v) for v in df["id"].tolist()]
    for tbl in ("t_movie_genre", "t_movie_keyword", "t_movie_cast", "t_movie_crew",
                "t_movie_company", "t_movie_country"):
        for i in range(0, len(ids), BATCH):
            cur.executemany(f"DELETE FROM {tbl} WHERE movie_id=%s",
                            [(m,) for m in ids[i:i + BATCH]])
    conn.commit()

    def insert_pairs(sql, pairs):
        for i in range(0, len(pairs), BATCH):
            cur.executemany(sql, pairs[i:i + BATCH])
        conn.commit()
        return len(pairs)

    mg = [( _int(r["id"]), genre_ids[g]) for _, r in df.iterrows() for g in _lit(r["genres_list"]) if g in genre_ids]
    mk = [( _int(r["id"]), kw_ids[k]) for _, r in df.iterrows() for k in _lit(r["keywords_list"]) if k in kw_ids]
    mc = [( _int(r["id"]), comp_ids[c]) for _, r in df.iterrows() for c in _lit(r["companies_list"]) if c in comp_ids]
    mn = [( _int(r["id"]), country_ids[c]) for _, r in df.iterrows() for c in _lit(r["countries_list"]) if c in country_ids]
    cast_rows = [(mid, person_ids[n], ch, order) for mid, n, ch, order in cast_plan if n in person_ids]
    crew_rows = [(mid, person_ids[n], dep, job) for mid, n, dep, job in crew_plan if n in person_ids]

    n1 = insert_pairs("INSERT IGNORE INTO t_movie_genre (movie_id, genre_id) VALUES (%s,%s)", list(dict.fromkeys(mg)))
    n2 = insert_pairs("INSERT IGNORE INTO t_movie_keyword (movie_id, keyword_id) VALUES (%s,%s)", list(dict.fromkeys(mk)))
    n3 = insert_pairs("INSERT INTO t_movie_cast (movie_id, person_id, character_name, cast_order) VALUES (%s,%s,%s,%s)", cast_rows)
    n4 = insert_pairs("INSERT INTO t_movie_crew (movie_id, person_id, department, job) VALUES (%s,%s,%s,%s)", crew_rows)
    n5 = insert_pairs("INSERT IGNORE INTO t_movie_company (movie_id, company_id) VALUES (%s,%s)", list(dict.fromkeys(mc)))
    n6 = insert_pairs("INSERT IGNORE INTO t_movie_country (movie_id, country_id) VALUES (%s,%s)", list(dict.fromkeys(mn)))
    print(f"关联表: 类型 {n1} / 关键词 {n2} / 演员 {n3} / 职员 {n4} / 公司 {n5} / 国家 {n6}")

    # ---------- 4. 汇总复核 ----------
    print("\n---- 库内行数复核 ----")
    for tbl in ("t_movie", "t_genre", "t_keyword", "t_person", "t_company", "t_country",
                "t_movie_genre", "t_movie_keyword", "t_movie_cast", "t_movie_crew",
                "t_movie_company", "t_movie_country"):
        cur.execute(f"SELECT COUNT(*) FROM {tbl}")
        print(f"  {tbl:18s} {cur.fetchone()[0]:>8d}")
    conn.close()
    print(f"\n导入完成，用时 {time.time() - t0:.1f} 秒")


if __name__ == "__main__":
    main()
