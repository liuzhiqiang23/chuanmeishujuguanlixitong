# -*- coding: utf-8 -*-
"""
recommend_api.py
================
将 Movie-Analysis-master 项目里的推荐算法封装为命令行脚本，
供 Java 后端通过 ProcessBuilder 调用。

用法:
    python recommend_api.py --algo <algo> [--user <int>] [--movie <title>] [--keywords <text>] [--top <int=10>]

algo 取值（9 种）:
    demographic     全局流行度/加权得分推荐（naive_recommender.Demographic）
    content         基于 overview 的 TF-IDF 内容相似推荐（naive_recommender.Content）
    keyword         基于 cast/crew/keywords/genres 关键词推荐（naive_recommender.Keyword）
    user_knn        基于用户的 KNN 协同过滤（personal_recommender.KNN_user）
    movie_knn       基于电影的 KNN 协同过滤（personal_recommender.KNN_movie）
    svd             基于 SVD 的协同过滤评分（personal_recommender.Personal_SVD）
    usr_movie_knn   集成：用户KNN 候选 + 电影KNN 精排（ensemble_recommender.KNN_movie_usr_ensemble）
    knn_svd         集成：用户KNN 候选 + SVD 评分精排（ensemble_recommender.KNN_SVD_ensemble）
    usr_keywords    集成：用户KNN 候选 + 关键词相似精排（ensemble_recommender.KNN_usr_keywords_ensemble）

注: usr_movie_knn 同时需要 --user 与 --movie；usr_keywords 同时需要 --user 与 --keywords。

成功输出（单行 JSON，stdout）:
    {"algo": "demographic", "movies": [{"title": "...", "movieId": 278, "score": 8.06}, ...]}
    - movies[i].title    : 电影标题（string）
    - movies[i].movieId  : 电影 TMDB id（int，即 t_video_info.video_id）
    - movies[i].score    : 得分（float，无则为 null）

失败输出（单行 JSON，退出码非 0）:
    {"algo":"...", "error":"...", "trace":"..."}

注意:
    - 不修改 Movie-Analysis-master 中任何既有脚本。
    - naive 三算法基于 tmdb_5000_movies.csv，数据统一从 data/recommendation 读取，
      因此在实例化前将 CWD 切换到对应子目录。
    - personal 三算法返回 MovieLens movieId，通过 data/recommendation/personal/links.csv
      映射回 TMDB id（tmdbId）。
    - personal_recommender/KNN_movie.py 在模块顶层有演示代码，import 时会执行，
      需先 chdir 到 personal_recommender 并抑制其 stdout。
"""

import argparse
import contextlib
import io
import json
import os
import re
import sys
import traceback

# 单线程 BLAS/OMP：多线程会在分配失败时反复重试放大内存峰值（报
# "openBLAS 错误：内存分配在重试10次后仍然失败"），且本机内存长期紧张。
# 必须在任何 numpy/pandas/surprise 导入之前设置。
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

BASE = os.path.dirname(os.path.abspath(__file__))
NAIVE_DIR = os.path.join(BASE, "naive_recommender")
PERSONAL_DIR = os.path.join(BASE, "personal_recommender")
SYSTEM_ROOT = os.path.dirname(os.path.dirname(BASE))  # 系统工程根目录 movie-system/
DATA_DIR = os.path.join(SYSTEM_ROOT, "data", "recommendation")  # 统一数据目录
PERSONAL_DATA_DIR = os.path.join(DATA_DIR, "personal")
ENSEMBLE_DIR = os.path.join(BASE, "ensemble_recommender")

sys.path.insert(0, NAIVE_DIR)
sys.path.insert(0, PERSONAL_DIR)
sys.path.insert(0, ENSEMBLE_DIR)

# 强制 UTF-8 输出：Windows 下管道 stdout 默认可能是 GBK/ANSI，
# Java 端按 UTF-8 解码，故统一 reconfig 为 UTF-8。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

# 顶层演示代码 / 模型训练过程会向 stdout 打印，底层库（matplotlib/pandas 等）可能向 stderr 告警，
# stdout/stderr 全部抑制，保证最终只有一行 JSON（Java 端用 redirectErrorStream 合并读取）
def _silent():
    stack = contextlib.ExitStack()
    stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
    stack.enter_context(contextlib.redirect_stderr(io.StringIO()))
    return stack


# ---------------------------------------------------------------------------
# 数据映射：MovieLens movieId -> TMDB id -> 标题
# ---------------------------------------------------------------------------
_LINKS = None          # {MovieLens movieId(int) -> tmdbId(int)}
_MOVIES_INDEX = None   # {MovieLens movieId(int) -> MovieLens title(str)}
_TMDB_TITLES = None    # {tmdbId(int) -> tmdb_5000_movies title(str)}

_YEAR_RE = re.compile(r"\s*\(\d{4}\)\s*$")


def _norm_title(title):
    """将标题归一化：转小写、去掉结尾 (年份)、把 'X, The' 还原为 'The X'。"""
    s = str(title).strip().lower()
    s = _YEAR_RE.sub("", s).strip()
    if "," in s:
        parts = [p.strip() for p in s.split(",")]
        s = " ".join(reversed([p for p in parts if p]))
    s = re.sub(r"\s+", " ", s)
    return s


def get_links():
    """MovieLens movieId -> tmdbId。tmdbId 缺失（NaN）的电影被剔除。"""
    global _LINKS
    if _LINKS is None:
        import pandas as pd
        links = pd.read_csv(os.path.join(PERSONAL_DATA_DIR, "links.csv"))
        links = links.dropna(subset=["tmdbId"])
        links["tmdbId"] = links["tmdbId"].astype(int)
        _LINKS = dict(zip(links["movieId"], links["tmdbId"]))
    return _LINKS


def get_movies_index():
    """MovieLens movieId -> MovieLens title。"""
    global _MOVIES_INDEX
    if _MOVIES_INDEX is None:
        import pandas as pd
        movies = pd.read_csv(os.path.join(PERSONAL_DATA_DIR, "movies.csv"))
        _MOVIES_INDEX = dict(zip(movies["movieId"], movies["title"]))
    return _MOVIES_INDEX


def get_tmdb_titles():
    """tmdbId -> TMDB title（来自 data/tmdb_5000_movies.csv）。"""
    global _TMDB_TITLES
    if _TMDB_TITLES is None:
        import pandas as pd
        tmdb = pd.read_csv(
            os.path.join(DATA_DIR, "tmdb_5000_movies.csv"), usecols=["id", "title"]
        )
        tmdb = tmdb.dropna(subset=["id", "title"])
        tmdb["id"] = tmdb["id"].astype(int)
        _TMDB_TITLES = dict(zip(tmdb["id"], tmdb["title"]))
    return _TMDB_TITLES


def ml_ids_to_movies(ml_ids, ml_titles=None):
    """把 MovieLens movieId 列表转成契约 JSON 的 movies 数组。

    每个元素: {"title": TMDB标题优先/回退MovieLens标题, "movieId": tmdbId, "score": null}
    无法映射到 tmdbId 的电影被剔除。
    """
    links = get_links()
    tmdb_titles = get_tmdb_titles()
    movies_index = get_movies_index()
    if ml_titles is None:
        ml_titles = [movies_index.get(mid, "") for mid in ml_ids]
    out = []
    for mid, ml_title in zip(ml_ids, ml_titles):
        tmdb_id = links.get(int(mid))
        if tmdb_id is None:
            continue
        title = tmdb_titles.get(tmdb_id, ml_title)
        out.append({"title": title, "movieId": int(tmdb_id), "score": None})
    return out


# ---------------------------------------------------------------------------
# naive 三算法（基于 tmdb_5000_movies.csv，返回 TMDB id + title）
# ---------------------------------------------------------------------------
def run_demographic(top):
    import Demographic
    os.chdir(NAIVE_DIR)  # Demographic.py 内部不再使用相对路径（数据统一到 data/recommendation，由脚本自身位置解析）
    with _silent():
        rec = Demographic.Demographic_recommender()
        df = rec.recommend(top)
    sub = rec.movies[["title", "id"]].drop_duplicates(subset="title")
    id_map = dict(zip(sub["title"], sub["id"]))
    movies = []
    for _, row in df.iterrows():
        title = str(row["title"])
        mid = id_map.get(title)
        if mid is None:
            continue
        score = row["score"]
        movies.append(
            {
                "title": title,
                "movieId": int(mid),
                "score": float(score) if score is not None else None,
            }
        )
    return movies


def _resolve_tmdb_title(rec, movie_title):
    """在推荐器的 movies 表中按归一化标题匹配 TMDB 标题（支持模糊匹配）。"""
    norm_map = {}
    for t in rec.movies["title"].dropna().astype(str):
        norm_map.setdefault(_norm_title(t), t)
    key = _norm_title(movie_title)
    resolved = norm_map.get(key)
    if resolved is None:
        raise ValueError("Movie title not found in dataset: %r" % movie_title)
    return resolved


def run_content(movie_title, top):
    import Content
    os.chdir(NAIVE_DIR)  # Content.py 内部不再使用相对路径（数据统一到 data/recommendation，由脚本自身位置解析）
    with _silent():
        rec = Content.Content_recommender()
        title = _resolve_tmdb_title(rec, movie_title)
        # recommend(title) 最多返回 10 部（源码写死 sim_scores[1:11]）
        series = rec.recommend(title)
    sub = rec.movies[["title", "id"]].drop_duplicates(subset="title")
    id_map = dict(zip(sub["title"], sub["id"]))
    movies = []
    for t in series.iloc[:top].tolist():
        mid = id_map.get(t)
        if mid is None:
            continue
        movies.append({"title": t, "movieId": int(mid), "score": None})
    return movies


def run_keyword(movie_title, top):
    import Keyword
    os.chdir(NAIVE_DIR)  # Keyword.py 内部不再使用相对路径（数据统一到 data/recommendation，由脚本自身位置解析）
    with _silent():
        rec = Keyword.Keyword_recommender()
        title = _resolve_tmdb_title(rec, movie_title)
        # recommend(title) 最多返回 10 部（源码写死 sim_scores[1:11]）
        series = rec.recommend(title)
    sub = rec.movies[["title", "id"]].drop_duplicates(subset="title")
    id_map = dict(zip(sub["title"], sub["id"]))
    movies = []
    for t in series.iloc[:top].tolist():
        mid = id_map.get(t)
        if mid is None:
            continue
        movies.append({"title": t, "movieId": int(mid), "score": None})
    return movies


# ---------------------------------------------------------------------------
# personal 三算法（基于 MovieLens，返回 MovieLens movieId，需映射回 TMDB id）
# ---------------------------------------------------------------------------
def run_user_knn(user, top):
    import KNN_user
    with _silent():
        rec = KNN_user.Personal_KNN_recommender()  # mode=0: KNNBaseline
        # recommend(usrID, num=top) -> (titles: list, movieLens_ids: list)
        titles, ml_ids = rec.recommend(user, top)
    return ml_ids_to_movies(ml_ids, titles)


def _resolve_ml_id(movie_title):
    """把 MovieLens 电影标题（支持 'X, The' / 结尾年份写法）解析成 MovieLens movieId。"""
    movies_index = get_movies_index()
    norm_map = {}
    for mid, t in movies_index.items():
        norm_map.setdefault(_norm_title(t), int(mid))
    ml_id = norm_map.get(_norm_title(movie_title))
    if ml_id is None:
        raise ValueError("Movie title not found in MovieLens dataset: %r" % movie_title)
    return ml_id


def run_movie_knn(movie_title, top):
    # KNN_movie.py 数据统一从 data/recommendation/personal 读取，且模块顶层有演示代码
    # （import 时即训练模型并打印）-> 必须先 chdir 再 import，并抑制 stdout
    os.chdir(PERSONAL_DIR)
    with _silent():
        import KNN_movie
        rec = KNN_movie.test  # 复用模块顶层已训练好的实例
    ml_id = _resolve_ml_id(movie_title)
    with _silent():
        # get_similar_movies(movieID, num=top) -> 相似电影 MovieLens movieId 列表
        ml_ids = rec.get_similar_movies(ml_id, top)
    return ml_ids_to_movies(ml_ids)


def run_svd(user, top):
    import pandas as pd
    import Personal_SVD
    with _silent():
        rec = Personal_SVD.Personal_SVD_recommender()  # 内含 5-fold cross_validate，较慢
    train = pd.read_csv(os.path.join(PERSONAL_DATA_DIR, "train.csv"))
    rated = set(train[train["userId"] == user]["movieId"].astype(int))
    counts = train.groupby("movieId")["rating"].count().sort_values(ascending=False)
    # 候选池：用户未评分的高人气电影，限制规模以控制响应时间
    cands = [int(mid) for mid in counts.index if int(mid) not in rated][:1000]
    if not cands:
        raise ValueError("No candidate movies for user %s" % user)
    with _silent():
        # recommend(usrID, movies, num=top) -> (titles: list, movieLens_ids: list)
        titles, ml_ids = rec.recommend(user, cands, top)
    return ml_ids_to_movies(ml_ids, titles)


# ---------------------------------------------------------------------------
# ensemble 三算法（集成/混合推荐，基于 MovieLens，返回 MovieLens movieId）
# 说明: ensemble_recommender 的 2 个脚本在模块顶层带演示代码，已加 __main__ 保护
#       使其可被本文件 import；数据路径由脚本自身位置解析，不再依赖 CWD。
# ---------------------------------------------------------------------------
def run_usr_movie_knn(user, movie_title, top):
    """集成：用户KNN 取候选 -> 电影KNN 精排。返回 MovieLens 标题列表，映射回契约。"""
    ml_id = _resolve_ml_id(movie_title)
    os.chdir(ENSEMBLE_DIR)
    with _silent():
        import KNN_movie_usr_ensemble
        ens = KNN_movie_usr_ensemble.KNN_ensemble()
        result = ens.recommend(user, ml_id, top)
    # recommend 返回 list[Series]，每个 Series 是长度为 1 的 MovieLens 标题
    titles = []
    for s in result:
        if hasattr(s, "values") and len(s):
            titles.append(str(s.values[0]))
        elif hasattr(s, "tolist") and len(s):
            titles.append(str(s.tolist()[0]))
        else:
            titles.append(str(s))
    if not titles:
        return []
    movies_index = get_movies_index()
    norm_map = {}
    for mid, t in movies_index.items():
        norm_map.setdefault(_norm_title(t), int(mid))
    ml_ids, valid_titles = [], []
    for t in titles:
        mid = norm_map.get(_norm_title(t))
        if mid is not None:
            ml_ids.append(mid)
            valid_titles.append(t)
    return ml_ids_to_movies(ml_ids, valid_titles)


def run_knn_svd(user, top):
    """集成：用户KNN 取候选 -> SVD 评分精排。返回 MovieLens movieId 列表。"""
    os.chdir(ENSEMBLE_DIR)
    with _silent():
        import KNN_SVD_ensemble
        ens = KNN_SVD_ensemble.KNN_SVD_ensemble()
        # recommend(usrID, num=top) -> movieLens_ids: list
        # （SVD 初始化含 5-fold 交叉验证，响应较慢，与单算法 svd 一致）
        ml_ids = ens.recommend(user, top)
    return ml_ids_to_movies(ml_ids)


def run_usr_keywords(user, keywords, top):
    """集成：用户KNN 候选 + 关键词 TF-IDF 相似精排。返回 (TMDB标题, 相似度) 列表。"""
    os.chdir(ENSEMBLE_DIR)
    with _silent():
        import KNN_usr_keywords
        ens = KNN_usr_keywords.KNN_usr_keywords_ensemble()
        # recommend(usrID, keywords, num=top) -> [(title, similarity), ...]
        result = ens.recommend(user, keywords, top)
    # 标题是 tmdb_5000_movies 的 TMDB 标题 -> 反向映射 tmdbId
    tmdb_titles = get_tmdb_titles()
    norm_map = {}
    for tid, t in tmdb_titles.items():
        norm_map.setdefault(_norm_title(t), int(tid))
    movies = []
    for title, sim in result:
        tmdb_id = norm_map.get(_norm_title(str(title)))
        if tmdb_id is None:
            continue
        movies.append({
            "title": str(title),
            "movieId": tmdb_id,
            "score": float(sim) if sim is not None else None,
        })
    return movies


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)


def main():
    algo = None
    try:
        parser = _Parser(prog="recommend_api.py")
        parser.add_argument("--algo", required=True,
                            choices=["demographic", "content", "keyword",
                                     "user_knn", "movie_knn", "svd",
                                     "usr_movie_knn", "knn_svd", "usr_keywords"])
        parser.add_argument("--user", type=int, default=None)
        parser.add_argument("--movie", default=None)
        parser.add_argument("--keywords", default=None)
        parser.add_argument("--top", type=int, default=10)
        args = parser.parse_args()

        algo = args.algo
        top = max(1, min(args.top or 10, 50))

        if algo == "demographic":
            movies = run_demographic(top)
        elif algo == "content":
            if not args.movie:
                raise ValueError("--movie is required for algo 'content'")
            movies = run_content(args.movie, top)
        elif algo == "keyword":
            if not args.movie:
                raise ValueError("--movie is required for algo 'keyword'")
            movies = run_keyword(args.movie, top)
        elif algo == "user_knn":
            if args.user is None:
                raise ValueError("--user is required for algo 'user_knn'")
            movies = run_user_knn(args.user, top)
        elif algo == "movie_knn":
            if not args.movie:
                raise ValueError("--movie is required for algo 'movie_knn'")
            movies = run_movie_knn(args.movie, top)
        elif algo == "svd":
            if args.user is None:
                raise ValueError("--user is required for algo 'svd'")
            movies = run_svd(args.user, top)
        elif algo == "usr_movie_knn":
            if args.user is None:
                raise ValueError("--user is required for algo 'usr_movie_knn'")
            if not args.movie:
                raise ValueError("--movie is required for algo 'usr_movie_knn'")
            movies = run_usr_movie_knn(args.user, args.movie, top)
        elif algo == "knn_svd":
            if args.user is None:
                raise ValueError("--user is required for algo 'knn_svd'")
            movies = run_knn_svd(args.user, top)
        elif algo == "usr_keywords":
            if args.user is None:
                raise ValueError("--user is required for algo 'usr_keywords'")
            if not args.keywords:
                raise ValueError("--keywords is required for algo 'usr_keywords'")
            movies = run_usr_keywords(args.user, args.keywords, top)
        else:
            raise ValueError("unknown algo: %s" % algo)

        print(json.dumps({"algo": algo, "movies": movies}, ensure_ascii=False))
        sys.exit(0)
    except BaseException as exc:  # noqa: BLE001 - 统一转成契约 JSON
        # SystemExit(0) 之外的失败都输出错误 JSON
        if isinstance(exc, SystemExit) and exc.code == 0:
            raise
        print(json.dumps({
            "algo": algo,
            "error": str(exc),
            "trace": traceback.format_exc(),
        }, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
