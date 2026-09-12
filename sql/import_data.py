#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""CSV -> MySQL 数据导入脚本（TMDB5000 + MovieLens）。
用法: python import_data.py --host 127.0.0.1 --user root --password xxx --db vidio_mangage_db
"""
import argparse, json, os, sys, datetime
import math
import pandas as pd
import pymysql

# 数据源指向本工程统一数据根 data/recommendation（工程自包含，拷到任何机器无需改动）
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "recommendation")


def _clean(v):
    """把 pandas 读出的各种空值（float nan / numpy nan / pd.NA / 'nan' / 'None' / 空串）统一转 None。"""
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    if isinstance(v, str):
        s = v.strip()
        return None if s in ("", "nan", "NaN", "None", "null", "<NA>") else s
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    return v


def _to_int(v):
    v = _clean(v)
    if v is None:
        return None
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return None


def _to_float(v):
    v = _clean(v)
    if v is None:
        return None
    try:
        f = float(v)
        return None if math.isnan(f) or math.isinf(f) else f
    except (ValueError, TypeError):
        return None


def _to_str(v):
    return _clean(v)


def parse_json_list(s):
    if not isinstance(s, str) or not s.strip():
        return []
    try:
        return json.loads(s)
    except Exception:
        import ast
        try:
            return ast.literal_eval(s)
        except Exception:
            return []

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--user", default="root")
    ap.add_argument("--password", default="")
    ap.add_argument("--db", default="vidio_mangage_db")
    ap.add_argument("--offset", type=int, default=10, help="MovieLens 用户 id 偏移")
    args = ap.parse_args()

    conn = pymysql.connect(host=args.host, user=args.user, password=args.password,
                           database=args.db, charset="utf8mb4", autocommit=False)
    cur = conn.cursor()

    movies = pd.read_csv(f"{DATA}/tmdb_5000_movies.csv")
    ratings = pd.read_csv(f"{DATA}/personal/ratings.csv")
    links = pd.read_csv(f"{DATA}/personal/links.csv")

    # 1) 电影 -> t_video_info（video_id = tmdb id）
    movie_rows = 0
    for _, m in movies.iterrows():
        cur.execute(
            """INSERT INTO t_video_info
               (video_id, video_name, video_category, original_title, overview, tagline,
                budget, revenue, popularity, vote_average, vote_count, runtime,
                release_date, original_language, poster_path, create_time, creator_id)
               VALUES (%s,%s,3,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW(),2)
               ON DUPLICATE KEY UPDATE video_name=VALUES(video_name)""",
            (int(m["id"]), _to_str(m["title"]), _to_str(m.get("original_title")),
             _to_str(m.get("overview")), _to_str(m.get("tagline")),
             _to_int(m.get("budget")), _to_int(m.get("revenue")),
             _to_float(m.get("popularity")), _to_float(m.get("vote_average")),
             _to_int(m.get("vote_count")), _to_int(m.get("runtime")),
             _to_str(m.get("release_date")), _to_str(m.get("original_language")),
             _to_str(m.get("poster_path"))))
        movie_rows += 1

    # 2) 类型/关键词 -> t_tag + t_video_tag
    tag_id = {}
    def tag_id_for(name):
        name = str(name).strip()
        if not name or name == "nan":
            return None
        if name not in tag_id:
            cur.execute("INSERT INTO t_tag (tag_name) VALUES (%s)", (name,))
            tag_id[name] = cur.lastrowid
        return tag_id[name]

    tag_rows = 0
    for _, m in movies.iterrows():
        names = [g.get("name") for g in parse_json_list(m.get("genres"))]
        names += [k.get("name") for k in parse_json_list(m.get("keywords"))]
        for n in names:
            tid = tag_id_for(n)
            if tid:
                cur.execute("INSERT IGNORE INTO t_video_tag (video_id, tag_id, video_property_flag) VALUES (%s,%s,1)",
                            (int(m["id"]), tid))
                tag_rows += 1

    # 3) 用户 -> t_user（id = userId + offset）
    user_rows = 0
    for uid in ratings["userId"].unique():
        uid = int(uid)
        cur.execute(
            """INSERT INTO t_user (id, user_uuid, user_name, password, real_name, status, create_time, deleted, role)
               VALUES (%s,%s,%s,'',%s,1,NOW(),0,1)
               ON DUPLICATE KEY UPDATE user_name=VALUES(user_name)""",
            (uid + args.offset, f"ml-{uid}", f"user{uid}", f"用户{uid}"))
        user_rows += 1

    # 4) links: movieId -> tmdbId
    link_map = {}
    for _, r in links.iterrows():
        if pd.notna(r.get("tmdbId")):
            link_map[int(r["movieId"])] = int(r["tmdbId"])

    # 5) 评分 -> t_user_video_operation（仅保留能命中 TMDB5000 电影的评分）
    valid_tmdb = set(movies["id"].astype(int))
    rating_rows = 0
    play_agg = {}
    for _, r in ratings.iterrows():
        mid = int(r["movieId"])
        tmdb = link_map.get(mid)
        if tmdb is None or tmdb not in valid_tmdb:
            continue
        uid = int(r["userId"]) + args.offset
        rating = float(r["rating"])
        cur.execute(
            """INSERT INTO t_user_video_operation (id, video_id, thumb_up, collection, rating, finally_active_time)
               VALUES (%s,%s,%s,%s,%s,NOW())
               ON DUPLICATE KEY UPDATE rating=VALUES(rating), thumb_up=VALUES(thumb_up), collection=VALUES(collection)""",
            (uid, tmdb, 1 if rating >= 4 else 0, 1 if rating >= 4.5 else 0, rating))
        rating_rows += 1
        play_agg[tmdb] = play_agg.get(tmdb, 0) + 1

    # 6) 播放量 -> t_video_play（每电影聚合一条，play_times = 评分次数）
    play_rows = 0
    for tmdb, cnt in play_agg.items():
        cur.execute(
            """INSERT INTO t_video_play (video_id, user_id, last_play_time, play_times)
               VALUES (%s,2,NOW(),%s) ON DUPLICATE KEY UPDATE play_times=VALUES(play_times)""",
            (tmdb, cnt))
        play_rows += 1

    conn.commit()
    print(json.dumps({"movies": movie_rows, "users": user_rows, "ratings": rating_rows,
                      "tags": tag_rows, "play": play_rows}, ensure_ascii=False))
    cur.close(); conn.close()

if __name__ == "__main__":
    main()
