# -*- coding: utf-8 -*-
"""
智能推荐引擎（新项目《电影票房预测与智能推荐系统》· 第六步）
================================================================
数据源：新数据集清洗产物 data/processed/train_clean.csv + test_clean.csv（10000 部）
        —— 不依赖已按作业要求删除的 MovieLens 评分数据，详见 docs/05 审查记录 §2-2。

用法（后端通过 ProcessBuilder 调用，stdout 最后一行必须是合法 JSON）：
  相似影片：  python recommend_api.py --movie 9331 --top 10
  类型热门：  python recommend_api.py --genre Action --top 10
  个性化加权：python recommend_api.py --movie 9331 --top 10 --boost-genres "Action,Drama"
             （boost-genres 由后端从站内评分表 t_rating 统计出"用户高分影片的类型"后传入）

相似度特征权重（与 docs/04_系统详细设计.md §4.3 一致）：
  类型 ×2.0、关键词 TF-IDF ×1.0、导演 ×1.5、前三主演 ×1.2、公司 ×0.8、国家 ×0.8、语种 ×0.5

输出：
  {"ok":true,"strategy":"similar","seed":{...},"items":[{"movieId":863,"title":"...","year":1995,
   "posterPath":"/x.jpg","score":0.83,"reasons":["同类型：动画","同导演：John Lasseter"]}]}
输出（失败）：{"error":"可读原因"}
"""
import argparse
import ast
import json
import os
import sys
import time

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.preprocessing import MultiLabelBinarizer, normalize
from sklearn.feature_extraction.text import TfidfVectorizer

sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SYSTEM_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
DATA_DIR = os.path.join(SYSTEM_ROOT, "data", "processed")
CACHE_DIR = os.path.join(SCRIPT_DIR, "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# 中文类型名 → 数据集里的英文类型名（界面上两种写法都能用）
GENRE_ALIAS = {
    "动作": "Action", "冒险": "Adventure", "动画": "Animation", "喜剧": "Comedy",
    "犯罪": "Crime", "纪录": "Documentary", "纪录片": "Documentary", "剧情": "Drama",
    "家庭": "Family", "奇幻": "Fantasy", "历史": "History", "恐怖": "Horror",
    "音乐": "Music", "悬疑": "Mystery", "爱情": "Romance", "科幻": "Science Fiction",
    "惊悚": "Thriller", "战争": "War", "西部": "Western",
}

_cache = {"df": None, "matrix": None, "meta": None}
CACHE_VERSION = 1
_MATRIX_NPZ = os.path.join(CACHE_DIR, "matrix.npz")
_MOVIES_PKL = os.path.join(CACHE_DIR, "movies.pkl")
_CACHE_META = os.path.join(CACHE_DIR, "cache_meta.json")


def _cache_key():
    """缓存键 = 两个清洗产物的大小与修改时间 + 版本号（数据重跑后自动失效）"""
    parts = []
    for name in ("train_clean.csv", "test_clean.csv"):
        st = os.stat(os.path.join(DATA_DIR, name))
        parts.append(f"{name}:{int(st.st_mtime)}:{st.st_size}")
    return "|".join(parts) + f"|v{CACHE_VERSION}"


def _try_load_cache():
    """命中磁盘缓存则直接装载（矩阵构建约占 14s，缓存后 <1s）"""
    if not (os.path.exists(_MATRIX_NPZ) and os.path.exists(_MOVIES_PKL) and os.path.exists(_CACHE_META)):
        return False
    try:
        with open(_CACHE_META, encoding="utf-8") as f:
            saved = json.load(f)
        if saved.get("key") != _cache_key():
            return False
        import pickle
        with open(_MOVIES_PKL, "rb") as f:
            df = pickle.load(f)
        _cache["df"] = df
        _cache["matrix"] = sparse.load_npz(_MATRIX_NPZ).tocsr()
        _cache["meta"] = {"rows": len(df), "id_index": {int(m): i for i, m in enumerate(df["id"].tolist())}}
        return True
    except Exception:
        return False


def _save_cache(df, matrix):
    try:
        import pickle
        sparse.save_npz(_MATRIX_NPZ, matrix)
        with open(_MOVIES_PKL, "wb") as f:
            pickle.dump(df, f)
        with open(_CACHE_META, "w", encoding="utf-8") as f:
            json.dump({"key": _cache_key(), "rows": len(df)}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[提示] 推荐缓存写入失败（不影响本次结果）: {e}", file=sys.stderr)


def _parse_list(value):
    """preprocess.py 产物里列表字段是 Python 字面量字符串（如 "['Action', 'Drama']"）"""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return []
    text = str(value).strip()
    if not text or text in ("nan", "[]"):
        return []
    try:
        parsed = ast.literal_eval(text)
        return [str(x).strip() for x in parsed] if isinstance(parsed, (list, tuple, set)) else []
    except (ValueError, SyntaxError):
        return [p.strip() for p in text.strip("[]").split(",") if p.strip()]


def _parse_cast(value):
    return [p.strip() for p in str(value or "").split("|") if p.strip()]


def load_data():
    """读取 train + test 清洗产物并拼接；进程内与磁盘双层缓存"""
    if _cache["df"] is not None:
        return _cache["df"]
    if _try_load_cache():
        return _cache["df"]

    frames = []
    for name in ("train_clean.csv", "test_clean.csv"):
        path = os.path.join(DATA_DIR, name)
        if not os.path.exists(path):
            raise FileNotFoundError(f"缺少数据文件 {path}；请先运行 algorithm/FeatureEDA/preprocess.py")
        frames.append(pd.read_csv(path, low_memory=False))
    df = pd.concat(frames, ignore_index=True).drop_duplicates(subset="id").reset_index(drop=True)

    for col in ("genres_list", "keywords_list", "companies_list", "countries_list"):
        df[col + "_parsed"] = df[col].map(_parse_list)
    df["cast_parsed"] = df["top3_cast"].map(_parse_cast)
    df["director"] = df["director"].fillna("").astype(str)
    df["original_language"] = df["original_language"].fillna("").astype(str)
    df["title"] = df["title"].fillna(df["original_title"]).fillna("").astype(str)
    for col in ("popularity", "vote_count", "year", "vote_average"):
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # 只保留推荐所需的列（缓存更小、装载更快）
    keep = ["id", "title", "year", "poster_path", "main_genre", "popularity", "vote_count",
            "original_language", "director", "genres_list_parsed", "keywords_list_parsed",
            "companies_list_parsed", "countries_list_parsed", "cast_parsed"]
    df = df[keep]
    _cache["df"] = df
    return df


def build_matrix(df):
    """加权特征矩阵（各块内部先做 TF-IDF/独热，再乘权重，最后整体 L2 归一化）"""
    if _cache["matrix"] is not None:
        return _cache["matrix"], _cache["meta"]

    blocks, weights = [], []

    def add_mlb(series, weight):
        mlb = MultiLabelBinarizer()
        blocks.append(mlb.fit_transform(series))
        weights.append(weight)

    add_mlb(df["genres_list_parsed"], 2.0)
    add_mlb(df["cast_parsed"], 1.2)
    add_mlb(df["countries_list_parsed"], 0.8)
    add_mlb(df["companies_list_parsed"], 0.8)
    add_mlb(df["director"].map(lambda s: [s] if s else []), 1.5)
    add_mlb(df["original_language"].map(lambda s: [s] if s else []), 0.5)

    tfidf = TfidfVectorizer(analyzer=lambda kws: kws, min_df=2)
    blocks.append(tfidf.fit_transform(df["keywords_list_parsed"]))
    weights.append(1.0)

    matrix = sparse.hstack([b.astype(np.float64) * w for b, w in zip(blocks, weights)]).tocsr()
    matrix = normalize(matrix)

    meta = {"rows": len(df), "id_index": {int(mid): i for i, mid in enumerate(df["id"].tolist())}}
    _cache["matrix"], _cache["meta"] = matrix, meta
    _save_cache(df, matrix)
    return matrix, meta


def _row(df, idx):
    return df.iloc[idx]


def _brief(df, idx):
    r = _row(df, idx)
    return {"movieId": int(r["id"]), "title": r["title"], "year": int(r["year"]) if r["year"] else None,
            "posterPath": r["poster_path"] if isinstance(r["poster_path"], str) else None,
            "mainGenre": r["main_genre"] if isinstance(r["main_genre"], str) else None}


def _similar_reasons(src, cand):
    reasons = []
    shared_genres = [g for g in src["genres_list_parsed"] if g in cand["genres_list_parsed"]]
    if shared_genres:
        reasons.append("同类型：" + "、".join(shared_genres[:3]))
    if src["director"] and src["director"] == cand["director"]:
        reasons.append("同导演：" + src["director"])
    shared_cast = [c for c in src["cast_parsed"] if c in cand["cast_parsed"]]
    if shared_cast:
        reasons.append("同主演：" + "、".join(shared_cast[:2]))
    shared_kw = [k for k in src["keywords_list_parsed"] if k in cand["keywords_list_parsed"]]
    if shared_kw:
        reasons.append("共同关键词：" + "、".join(shared_kw[:3]))
    if src["original_language"] and src["original_language"] == cand["original_language"]:
        reasons.append("同语种：" + src["original_language"])
    return reasons[:4]


def recommend_similar(movie_id, top_n, boost_genres):
    df = load_data()
    matrix, meta = build_matrix(df)
    idx = meta["id_index"].get(int(movie_id))
    if idx is None:
        raise ValueError(f"影片 id={movie_id} 不在数据集中")
    src = _row(df, idx)

    sims = (matrix[idx] @ matrix.T).toarray().ravel()
    if boost_genres:
        boosted = set()
        for g in boost_genres:
            boosted.add(GENRE_ALIAS.get(g, g))
        hit = df["genres_list_parsed"].map(lambda gs: bool(boosted & set(gs)))
        sims = sims + 0.15 * hit.to_numpy()

    order = np.argsort(-sims)
    items, boost_note = [], "、".join(sorted(boosted)) if boost_genres else ""
    for j in order:
        if int(j) == idx:
            continue
        cand = _row(df, j)
        reasons = _similar_reasons(src, cand)
        if boost_note and set(cand["genres_list_parsed"]) & boosted:
            reasons.append("因为你给「" + boost_note + "」类影片评分较高")
        items.append(dict(_brief(df, j), score=round(float(sims[j]), 4), reasons=reasons))
        if len(items) >= top_n:
            break
    return {"strategy": "similar", "seed": _brief(df, idx), "items": items}


def recommend_genre_hot(genre, top_n, boost_genres):
    df = load_data()
    target = GENRE_ALIAS.get(genre, genre)

    def has_genre(gs):
        return target in gs

    mask = df["genres_list_parsed"].map(has_genre)
    if not mask.any():
        raise ValueError(f"没有找到类型为「{genre}」的影片（可用英文类型名或常见中文名）")
    sub = df[mask].copy()

    pop = sub["popularity"].astype(float)
    vc = np.log1p(sub["vote_count"].astype(float))
    pop_z = (pop - pop.mean()) / (pop.std() or 1.0)
    vc_z = (vc - vc.mean()) / (vc.std() or 1.0)
    score = 0.6 * pop_z + 0.4 * vc_z

    if boost_genres:
        boosted = {GENRE_ALIAS.get(g, g) for g in boost_genres}
        score = score + 0.15 * sub["genres_list_parsed"].map(lambda gs: bool(boosted & set(gs))).astype(float)

    order = np.argsort(-score.to_numpy())
    items = []
    for pos in order[:top_n]:
        row_idx = sub.index[pos]
        c = _row(df, row_idx)
        items.append(dict(_brief(df, row_idx), score=round(float(score.iloc[pos]), 4),
                          reasons=[f"类型：{target}",
                                   f"热度 {float(c['popularity']):.1f}",
                                   f"评分人数 {int(c['vote_count'])}"]))
    return {"strategy": "genre_hot", "genre": target, "items": items}


def main():
    p = argparse.ArgumentParser(description="智能推荐引擎（内容相似 / 类型热门 / 评分加权）")
    p.add_argument("--movie", type=int, default=None, help="种子影片 id（相似推荐）")
    p.add_argument("--genre", default=None, help="类型名（类型热门推荐）")
    p.add_argument("--top", type=int, default=10)
    p.add_argument("--boost-genres", default="", help="站内高分影片的类型，逗号分隔（个性化加权）")
    args = p.parse_args()
    boost = [g.strip() for g in args.boost_genres.split(",") if g.strip()]

    try:
        t0 = time.time()
        if args.movie:
            result = recommend_similar(args.movie, max(1, args.top), boost)
        elif args.genre:
            result = recommend_genre_hot(args.genre, max(1, args.top), boost)
        else:
            raise ValueError("请指定 --movie <id> 或 --genre <类型>")
        result["ok"] = True
        result["seconds"] = round(time.time() - t0, 2)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": f"推荐失败: {e}"}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
