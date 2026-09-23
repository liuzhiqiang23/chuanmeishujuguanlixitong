# -*- coding: utf-8 -*-
"""
票房预测算法底座（新项目《电影票房预测与智能推荐系统》第三步核心）
================================================================
任务：对 log10(revenue) 做回归，横向对比 ≥6 种机器学习/深度学习算法
输入：data/processed/train_clean.csv（5000×48，preprocess.py 产物）
输出：metrics.json / figures/algo_comparison.png / models/best_model.joblib
约定：随机种子 42 全程固定，结果可复现
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SYSTEM_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))          # 项目根
DATA_PATH = os.path.join(SYSTEM_ROOT, "data", "processed", "train_clean.csv")
FIG_DIR = os.path.join(SCRIPT_DIR, "figures")
MODEL_DIR = os.path.join(SCRIPT_DIR, "models")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

SEED = 42
TARGET = "log_revenue"

# ---- 特征（与 docs/02_概要设计.md 3.2 一致）----
NUM_FEATURES = [
    "log_budget", "runtime", "log_popularity", "vote_average", "vote_count",
    "n_genres", "n_keywords", "n_countries", "n_companies", "n_languages",
    "cast_size", "is_collection", "is_english", "year", "month",
]
ONEHOT_GENRE = "main_genre"      # Top10 独热
ONEHOT_COUNTRY = "main_country"  # Top6 独热


def build_features(df: pd.DataFrame, meta_out: dict = None) -> pd.DataFrame:
    """从 train_clean 构造建模特征矩阵

    meta_out 非 None 时顺带回填在线推理所需的元数据（独热类别表、runtime 中位数），
    推理脚本据此重建完全一致的 34 维特征（见 docs/04_系统详细设计.md §4.2）。
    """
    X = pd.DataFrame(index=df.index)
    for c in NUM_FEATURES:
        X[c] = pd.to_numeric(df[c], errors="coerce")
    # 派生：评分人数对数、预算缺失指示
    X["log_vote_count"] = np.log1p(X["vote_count"].clip(lower=0))
    X["has_budget"] = X["log_budget"].notna().astype(int)
    X = X.drop(columns=["vote_count"])
    # 缺失处理：runtime 中位数、其余 0
    X["runtime"] = X["runtime"].fillna(X["runtime"].median())
    X = X.fillna(0)
    # 布尔转 int
    for c in ("is_collection", "is_english"):
        X[c] = X[c].astype(int)
    # 类别独热（长尾归 Other）
    for col, topn in ((ONEHOT_GENRE, 10), (ONEHOT_COUNTRY, 6)):
        top = df[col].value_counts().head(topn).index
        cat = df[col].where(df[col].isin(top), other="Other")
        dummies = pd.get_dummies(cat, prefix=col).astype(int)
        X = pd.concat([X, dummies], axis=1)
        if meta_out is not None:
            meta_out[f"{col}_categories"] = list(dummies.columns)
    if meta_out is not None:
        meta_out["runtime_median"] = float(X["runtime"].median())
        meta_out["year_median"] = float(pd.to_numeric(df["year"], errors="coerce").median())
        # 在线推理时"用户未提供的字段"用训练集中位数补齐（比填 0 更接近真实影片，
        # 填 0 会把新片推到特征空间最角落，导致预测系统性偏低）
        meta_out["defaults"] = {c: float(X[c].median()) for c in
                                ("vote_average", "log_vote_count", "log_popularity", "n_genres",
                                 "n_keywords", "n_countries", "n_companies", "n_languages", "cast_size")}
    return X


def build_models():
    """8 种算法注册表（需要标准化的用 Pipeline 封装）"""
    models = [
        ("LinearRegression 线性回归", LinearRegression()),
        ("DecisionTree 决策树", DecisionTreeRegressor(max_depth=12, random_state=SEED)),
        ("RandomForest 随机森林", RandomForestRegressor(n_estimators=300, n_jobs=-1, random_state=SEED)),
        ("GradientBoosting 梯度提升", GradientBoostingRegressor(n_estimators=200, learning_rate=0.06, random_state=SEED)),
        ("KNN K近邻(k=15)", Pipeline([("sc", StandardScaler()), ("m", KNeighborsRegressor(n_neighbors=15))])),
        ("SVR 支持向量回归(RBF)", Pipeline([("sc", StandardScaler()), ("m", SVR(kernel="rbf", C=10.0))])),
        ("MLP 多层感知机(深度学习)", Pipeline([("sc", StandardScaler()), ("m", MLPRegressor(hidden_layer_sizes=(128, 64), max_iter=500, early_stopping=True, random_state=SEED))])),
    ]
    try:
        from lightgbm import LGBMRegressor
        models.append(("LightGBM", LGBMRegressor(n_estimators=400, learning_rate=0.05, random_state=SEED, verbose=-1)))
    except ImportError:
        print("提示: 未安装 lightgbm，降级为 7 种算法（仍满足 ≥6 要求）")
    return models


def main():
    df = pd.read_csv(DATA_PATH, low_memory=False)
    df = df.dropna(subset=[TARGET]).copy()
    meta = {}
    X = build_features(df, meta)
    y = df[TARGET].astype(float)

    X_tr, X_va, y_tr, y_va = train_test_split(X, y, test_size=0.2, random_state=SEED)
    print(f"样本: 训练 {len(X_tr)} / 验证 {len(X_va)}，特征 {X.shape[1]} 维")

    results = []
    for name, model in build_models():
        t0 = time.time()
        model.fit(X_tr, y_tr)
        fit_s = time.time() - t0
        pred = model.predict(X_va)
        rmse = float(np.sqrt(mean_squared_error(y_va, pred)))
        mae = float(mean_absolute_error(y_va, pred))
        r2 = float(r2_score(y_va, pred))
        results.append({"name": name, "rmse": round(rmse, 4), "mae": round(mae, 4),
                        "r2": round(r2, 4), "fit_seconds": round(fit_s, 2)})
        print(f"[{name:28s}] RMSE={rmse:.4f}  MAE={mae:.4f}  R2={r2:.4f}  ({fit_s:.1f}s)")

    best = min(results, key=lambda r: r["rmse"])
    print(f"\n最佳模型: {best['name']} (RMSE={best['rmse']})")

    # ---- 持久化 ----
    metrics = {"task": "boxoffice_log_revenue_regression", "seed": SEED,
               "n_train": int(len(X_tr)), "n_val": int(len(X_va)),
               "n_features": int(X.shape[1]), "best": best["name"],
               "algorithms": results}
    with open(os.path.join(SCRIPT_DIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    best_entry = dict(build_models())[best["name"]]
    best_entry.fit(X, y)  # 全量重训最佳模型用于后续预测
    import joblib
    joblib.dump({"model": best_entry, "features": list(X.columns)},
                os.path.join(MODEL_DIR, "best_model.joblib"))

    # ---- 在线推理元数据（predict_api.py 必读：列顺序 + 独热类别表 + 中位数 + 指标）----
    meta.update({
        "columns": list(X.columns),
        "target": TARGET,
        "seed": SEED,
        "best": best["name"],
        "metrics": {"rmse": best["rmse"], "mae": best["mae"], "r2": best["r2"]},
        "numeric_features": list(NUM_FEATURES),
    })
    with open(os.path.join(MODEL_DIR, "feature_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"推理元数据: {os.path.join(MODEL_DIR, 'feature_meta.json')}")

    # ---- 对比图 ----
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    names = [r["name"].split(" ")[0] for r in results]
    rmse_v = [r["rmse"] for r in results]
    r2_v = [r["r2"] for r in results]
    colors = ["crimson" if r["name"] == best["name"] else "#4C72B0" for r in results]
    for ax, vals, title, better in ((axes[0], rmse_v, "RMSE（对数尺度，越低越好）", min),
                                    (axes[1], r2_v, "R²（越高越好）", max)):
        bars = ax.bar(names, vals, color=colors, alpha=0.9)
        for b, v in zip(bars, vals):
            ax.annotate(f"{v:.3f}", xy=(b.get_x() + b.get_width() / 2, v),
                        xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9)
        ax.set_title(title)
        ax.tick_params(axis="x", rotation=30)
        ax.grid(axis="y", alpha=0.3)
    fig.suptitle(f"8 种算法票房预测对比（最佳: {best['name']}）", fontsize=13)
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "algo_comparison.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"对比图: {out}")
    print(f"指标汇总: {os.path.join(SCRIPT_DIR, 'metrics.json')}")


def dump_meta_only():
    """只重建推理元数据（不重新训练）：元数据完全由训练集与既有 metrics.json 推导"""
    df = pd.read_csv(DATA_PATH, low_memory=False)
    df = df.dropna(subset=[TARGET]).copy()
    meta = {}
    X = build_features(df, meta)

    metrics, best = {}, ""
    metrics_path = os.path.join(SCRIPT_DIR, "metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path, encoding="utf-8") as f:
            m = json.load(f)
        best = m.get("best", "")
        entry = next((a for a in m.get("algorithms", []) if a["name"] == best), None)
        if entry:
            metrics = {"rmse": entry["rmse"], "mae": entry["mae"], "r2": entry["r2"]}

    meta.update({"columns": list(X.columns), "target": TARGET, "seed": SEED, "best": best,
                 "metrics": metrics, "numeric_features": list(NUM_FEATURES)})
    out = os.path.join(MODEL_DIR, "feature_meta.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"推理元数据已生成: {out}")
    print(f"  特征列 {len(meta['columns'])} 维 | 类型独热 {len(meta['main_genre_categories'])} 类 "
          f"| 国家独热 {len(meta['main_country_categories'])} 类 | runtime 中位数 {meta['runtime_median']}")


if __name__ == "__main__":
    if "--dump-meta" in sys.argv:
        dump_meta_only()
    else:
        main()
