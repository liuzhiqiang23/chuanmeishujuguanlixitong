# -*- coding: utf-8 -*-
"""
票房预测推理服务（新项目《电影票房预测与智能推荐系统》· 第六步）
================================================================
模型：algorithm/boxoffice_prediction/models/best_model.joblib（train_all.py 产物）
元数据：models/feature_meta.json（34 维列顺序 + 独热类别表 + runtime/year 中位数 + 指标）
       —— 特征构造规则与 train_all.build_features 完全一致，保证训练/推理不偏移。

用法（后端通过 ProcessBuilder 调用，stdout 最后一行必须是合法 JSON）：
  单片预测：
    python predict_api.py --budget 150000000 --popularity 18.6 --runtime 110 --language en
                          [--status Released] [--genres Action] [--release-month 6]
                          [--vote-average 7.5] [--vote-count 5000] [--model best]
  批量预测：
    python predict_api.py --batch ../../data/processed/test_clean.csv --limit 1000 --out batch.jsonl

输出（成功）：
  {"ok":true,"model":"RandomForest 随机森林","log_revenue":8.12,"prediction":131825673,
   "currency":"USD","range":{"low":21379664,"high":813100000},"metrics":{"rmse":0.875,"mae":0.5546,"r2":0.591},
   "trainedNow":false}
输出（失败）：{"error":"可读原因"}
"""
import argparse
import json
import os
import sys
import time

import numpy as np
import pandas as pd
import joblib

sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(SCRIPT_DIR, "models", "best_model.joblib")
META_PATH = os.path.join(SCRIPT_DIR, "models", "feature_meta.json")

_cache = {"model": None, "meta": None}


def load_assets():
    """加载模型与元数据（进程内只加载一次）"""
    if _cache["model"] is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"未找到模型文件 {MODEL_PATH}；请先在 algorithm/boxoffice_prediction 下运行 train_all.py")
        _cache["model"] = joblib.load(MODEL_PATH)["model"]
    if _cache["meta"] is None:
        if not os.path.exists(META_PATH):
            raise FileNotFoundError(
                f"未找到推理元数据 {META_PATH}；请运行 train_all.py --dump-meta 生成")
        with open(META_PATH, encoding="utf-8") as f:
            _cache["meta"] = json.load(f)
    return _cache["model"], _cache["meta"]


def make_features(df: pd.DataFrame, meta: dict) -> pd.DataFrame:
    """按训练端规则把原始字段构造成 34 维特征矩阵（列顺序取自 meta）

    未提供的字段（NaN）用 meta['defaults'] 里训练集中位数补齐：新片本就没有评分/演职员数据，
    填 0 会把影片推到训练特征空间的最角落（=零热度小片），导致预测系统性偏低。
    """
    X = pd.DataFrame(index=df.index)
    d = meta.get("defaults", {})

    def col(name):
        return pd.to_numeric(df[name], errors="coerce") if name in df.columns else pd.Series([np.nan] * len(df), index=df.index)

    budget = col("budget")
    log_budget = np.where(budget > 0, np.log10(budget.where(budget > 0)), np.nan)
    X["log_budget"] = pd.Series(log_budget, index=df.index).fillna(0.0)
    X["has_budget"] = (budget > 0).astype(int)

    popularity = col("popularity")
    X["log_popularity"] = np.log10(popularity.clip(lower=1e-6).where(popularity > 0)) \
        .fillna(d.get("log_popularity", 0.0))
    X["runtime"] = col("runtime").fillna(meta["runtime_median"])
    X["vote_average"] = col("vote_average").fillna(d.get("vote_average", 0.0))
    X["log_vote_count"] = np.log1p(col("vote_count").clip(lower=0)).fillna(d.get("log_vote_count", 0.0))

    for c in ("n_genres", "n_keywords", "n_countries", "n_companies", "n_languages", "cast_size"):
        X[c] = col(c).fillna(d.get(c, 0.0))

    X["is_collection"] = col("is_collection").fillna(0).astype(int)
    if "is_english" in df.columns:
        X["is_english"] = col("is_english").fillna(0).astype(int)
    else:
        lang = df["language"].fillna("").astype(str).str.lower() if "language" in df.columns \
            else pd.Series([""] * len(df), index=df.index)
        X["is_english"] = (lang == "en").astype(int)

    X["year"] = col("year").fillna(meta.get("year_median", 0.0))
    X["month"] = col("month").fillna(0.0)

    # 类别独热：类别表取自 meta（未知/长尾一律归 Other），与训练端列语义完全一致
    for prefix, src in (("main_genre", "main_genre"), ("main_country", "main_country")):
        values = df[src].fillna("").astype(str) if src in df.columns \
            else pd.Series([""] * len(df), index=df.index)
        known = [c.replace(prefix + "_", "") for c in meta[f"{prefix}_categories"] if c != f"{prefix}_Other"]
        matched = values.isin(known)
        for cat in known:
            X[f"{prefix}_{cat}"] = (values == cat).astype(int)
        X[f"{prefix}_Other"] = (~matched).astype(int)

    return X.reindex(columns=meta["columns"], fill_value=0).astype(float)


def predict_frame(df: pd.DataFrame):
    """对一个 DataFrame（每行含原始字段）做预测，返回 log10 票房数组"""
    model, meta = load_assets()
    X = make_features(df, meta)
    return model.predict(X), meta


def build_result(log_revenue: float, meta: dict, requested_model: str = "best") -> dict:
    """把 log10 预测值还原为美元并给出区间"""
    metrics = meta.get("metrics") or {}
    rmse = metrics.get("rmse")
    low = high = None
    if rmse:
        low = float(10 ** (log_revenue - 1.96 * rmse))
        high = float(10 ** (log_revenue + 1.96 * rmse))
    out = {
        "ok": True,
        "model": meta.get("best", "best_model"),
        "requestedModel": requested_model,
        "logRevenue": round(float(log_revenue), 4),
        "prediction": int(round(float(10 ** log_revenue))),
        "currency": "USD",
        "range": {"low": int(round(low)) if low else None, "high": int(round(high)) if high else None},
        "metrics": metrics,
        "trainedNow": False,
    }
    return out


def run_single(args):
    genre = (args.genres or "").strip()
    row = {
        "budget": args.budget,
        "popularity": args.popularity,
        "runtime": args.runtime,
        "vote_average": args.vote_average,   # None → 训练集中位数补齐
        "vote_count": args.vote_count,       # None → 训练集中位数补齐
        "language": args.language,
        "status": args.status,
        "main_genre": genre,
        "main_country": "",
        "year": args.year,
        "month": args.release_month,
        "n_genres": 1 if genre else None,
        "cast_size": args.cast_size,
        "is_collection": None,
        # n_keywords / n_countries / n_companies / n_languages 不给 → 中位数补齐
    }
    df = pd.DataFrame([row])
    pred, meta = predict_frame(df)
    result = build_result(float(pred[0]), meta, args.model)
    imputed = []
    if not args.popularity:
        imputed.append("热度 popularity")
    if not args.vote_average:
        imputed.append("评分均值 vote_average")
    if not args.vote_count:
        imputed.append("评分人数 vote_count")
    if not args.cast_size:
        imputed.append("演员规模 cast_size")
    if not args.year:
        imputed.append("上映年份 year")
    if not genre:
        imputed.append("类型 main_genre")
    if not args.release_month:
        imputed.append("上映月份 month")
    result["imputedFields"] = imputed
    result["note"] = "未提供的字段按训练集中位数补齐；未提供票房记录类信息时预测不确定性更大" if imputed else ""
    print(json.dumps(result, ensure_ascii=False))


def run_batch(args):
    if not os.path.exists(args.batch):
        raise FileNotFoundError(f"批量预测输入文件不存在: {args.batch}")
    t0 = time.time()
    df = pd.read_csv(args.batch, low_memory=False)
    if args.limit and args.limit > 0:
        df = df.head(int(args.limit)).copy()
    n = len(df)
    if n == 0:
        raise ValueError("批量预测输入为空")

    preds = []
    step = 200
    for start in range(0, n, step):
        part = df.iloc[start:start + step]
        p, meta = predict_frame(part)
        preds.extend([float(v) for v in p])
        if start + step < n:
            print(f"[进度] {min(start + step, n)}/{n}", file=sys.stderr, flush=True)

    ids = df["id"].tolist() if "id" in df.columns else list(range(n))
    out_path = args.out or os.path.join(SCRIPT_DIR, "batch_predictions.jsonl")
    with open(out_path, "w", encoding="utf-8") as f:
        for mid, lr in zip(ids, preds):
            f.write(json.dumps({"movieId": int(mid), "logRevenue": round(lr, 4),
                                "prediction": int(round(10 ** lr))}, ensure_ascii=False) + "\n")

    seconds = round(time.time() - t0, 2)
    print(json.dumps({
        "ok": True,
        "model": meta.get("best", "best_model"),
        "total": n,
        "seconds": seconds,
        "out": out_path,
        "avgRevenue": int(round(float(np.mean([10 ** p for p in preds])))),
        "minRevenue": int(round(float(10 ** min(preds)))),
        "maxRevenue": int(round(float(10 ** max(preds)))),
    }, ensure_ascii=False))


def build_parser():
    p = argparse.ArgumentParser(description="票房预测推理服务（新数据集 + 最佳模型）")
    p.add_argument("--model", default="best", help="兼容参数：在线预测固定使用最佳模型")
    p.add_argument("--budget", type=float, default=None)
    p.add_argument("--popularity", type=float, default=None)
    p.add_argument("--runtime", type=float, default=None)
    p.add_argument("--language", default="en")
    p.add_argument("--status", default="Released")
    p.add_argument("--genres", default="")
    p.add_argument("--release-month", type=int, default=None)
    p.add_argument("--year", type=float, default=None)
    p.add_argument("--vote-average", type=float, default=None)
    p.add_argument("--vote-count", type=float, default=None)
    p.add_argument("--cast-size", type=float, default=None)
    p.add_argument("--batch", default=None, help="批量预测输入 CSV（如 data/processed/test_clean.csv）")
    p.add_argument("--limit", type=int, default=1000)
    p.add_argument("--out", default=None, help="批量预测结果输出路径（JSONL）")
    return p


def main():
    args = build_parser().parse_args()
    try:
        if args.batch:
            run_batch(args)
        else:
            if args.budget is None or args.budget < 0:
                raise ValueError("请填写有效的预算（非负数）")
            if args.runtime is None or args.runtime <= 0:
                raise ValueError("请填写有效的时长（分钟）")
            run_single(args)
    except Exception as e:  # 统一返回可读错误，最后一行仍是 JSON
        print(json.dumps({"error": f"票房预测失败: {e}"}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
