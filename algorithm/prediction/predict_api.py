# -*- coding: utf-8 -*-
"""
predict_api.py
================
票房预测命令行封装：把 Movie-Analysis-master 的票房预测模型封装成 CLI，
供 Java 后端通过 ProcessBuilder 调用（与 recommend_api.py 同一契约风格）。

特征与 LightGBM.py 完全一致：
    original_language / budget / popularity / runtime / status  ->  revenue(票房)

模型按 --model 训练并缓存到 model_cache/predict_<model>.joblib：
    - 首次调用自动训练并缓存（lightgbm 约 10~30 秒，随机森林/线性回归更快）；
    - 之后直接加载缓存，秒级返回。

用法:
    # 单条预测（首次会自动训练）
    python predict_api.py --model lgbm --budget 150000000 --popularity 20 --runtime 120 --language en --status Released

    # 仅预训练指定模型（建议部署后先跑一次预热，避免首次请求等待训练）
    python predict_api.py --train --model lgbm

成功输出（单行 JSON）:
    {"model": "lgbm", "prediction": 123456789.0, "currency": "USD",
     "trained_now": false, "cache_file": "...",
     "metrics": {"rmse": ..., "mae": ..., "r2": ...}}

失败输出（单行 JSON，退出码非 0）:
    {"model": "...", "error": "...", "trace": "..."}
"""

import argparse
import json
import os
import sys
import traceback
import warnings

warnings.filterwarnings("ignore")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

BASE = os.path.dirname(os.path.abspath(__file__))
SYSTEM_ROOT = os.path.dirname(os.path.dirname(BASE))  # 系统工程根目录 movie-system/
TRAIN_CSV = os.path.join(SYSTEM_ROOT, "data", "train.csv")
CACHE_DIR = os.path.join(BASE, "model_cache")

# 与 LightGBM.py 保持一致：数值列用中位数填充，类别列用众数填充
NUMERIC_COLS = ["budget", "popularity", "runtime"]
CAT_COLS = ["original_language", "status"]
# 模型实际使用的特征（类别列做编码后与数值列拼接，顺序与 LightGBM.py 一致）
FEATURE_NAMES = ["budget", "popularity", "runtime",
                 "original_language_code", "status_code"]


def _stdout_reconfigure():
    """Windows 管道下统一 UTF-8 输出，Java 端按 UTF-8 解码。"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def load_and_prepare():
    """读取 data/train.csv 并做与 LightGBM.py 相同的预处理，返回特征矩阵与编码元数据。"""
    df = pd.read_csv(TRAIN_CSV)
    df = df[CAT_COLS + NUMERIC_COLS + ["revenue"]].copy()

    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        median = df[col].median()
        # 注意：不要用 df[col].fillna(..., inplace=True)（链式赋值可能不生效）
        df[col] = df[col].fillna(0.0 if pd.isna(median) else median)
    for col in CAT_COLS:
        df[col] = df[col].fillna(df[col].mode()[0]).astype(str)

    lang_codes = {v: i for i, v in enumerate(df["original_language"].unique())}
    status_codes = {v: i for i, v in enumerate(df["status"].unique())}
    df["original_language_code"] = df["original_language"].map(lang_codes)
    df["status_code"] = df["status"].map(status_codes)

    meta = {
        "lang_codes": lang_codes,
        "status_codes": status_codes,
        "lang_mode": str(df["original_language"].mode()[0]),
        "status_mode": str(df["status"].mode()[0]),
    }
    X = df[FEATURE_NAMES]
    y = df["revenue"].astype(float)
    # 训练前最终兜底：杜绝 NaN 进入 sklearn 模型（LightGBM 可容忍，LR/RF 不行）
    X = X.fillna(X.median()).fillna(0.0)
    return X, y, meta


def build_model(name, X_train, y_train):
    """按名称构建并训练模型（仅训练集拟合）。"""
    if name == "lgbm":
        import lightgbm as lgb
        params = {
            "objective": "regression",
            "metric": "rmse",
            "boosting_type": "gbdt",
            "learning_rate": 0.05,
            "num_leaves": 31,
            "feature_fraction": 0.8,
            "bagging_fraction": 0.8,
            "bagging_freq": 5,
            "verbose": -1,
        }
        model = lgb.train(params, lgb.Dataset(X_train, label=y_train), num_boost_round=500)
    elif name == "rf":
        from sklearn.ensemble import RandomForestRegressor
        model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)
    elif name == "lr":
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        model.fit(X_train, y_train)
    elif name == "knn":
        # 对应 KNN.py：K 近邻回归
        from sklearn.neighbors import KNeighborsRegressor
        model = KNeighborsRegressor(n_neighbors=5, weights="distance", n_jobs=-1)
        model.fit(X_train, y_train)
    elif name == "svm":
        # 对应 SVM.py：支持向量回归
        from sklearn.svm import SVR
        model = SVR(kernel="rbf", C=10.0, gamma="scale", epsilon=0.1)
        model.fit(X_train, y_train)
    elif name == "dt":
        # 对应 DecisionTree.py：决策树回归
        from sklearn.tree import DecisionTreeRegressor
        model = DecisionTreeRegressor(random_state=42)
        model.fit(X_train, y_train)
    else:
        raise ValueError("unknown model: %s" % name)
    return model


def calc_metrics(model, X_test, y_test):
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    pred = model.predict(X_test)
    return {
        "rmse": float(np.sqrt(mean_squared_error(y_test, pred))),
        "mae": float(mean_absolute_error(y_test, pred)),
        "r2": float(r2_score(y_test, pred)),
    }


def cache_path(name):
    return os.path.join(CACHE_DIR, "predict_%s.joblib" % name)


def train_and_cache(name):
    """训练 + 测试集评估 + 缓存到 model_cache。"""
    import joblib
    from sklearn.model_selection import train_test_split

    X, y, meta = load_and_prepare()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    model = build_model(name, X_train, y_train)
    met = calc_metrics(model, X_test, y_test)

    os.makedirs(CACHE_DIR, exist_ok=True)
    bundle = {
        "model": model,
        "metrics": met,
        "feature_names": FEATURE_NAMES,
        "meta": meta,
    }
    joblib.dump(bundle, cache_path(name))
    return met


def load_or_train(name):
    """优先加载缓存，不存在则训练。返回 (bundle, trained_now)。"""
    import joblib
    path = cache_path(name)
    if os.path.exists(path):
        return joblib.load(path), False
    train_and_cache(name)
    return joblib.load(path), True


def _encode(codes, value, mode_value):
    s = str(value)
    if s in codes:
        return codes[s]
    # 训练集中未出现过的取值：回退到训练集众数类别
    return codes[mode_value]


def predict(name, budget, popularity, runtime, language, status):
    bundle, trained_now = load_or_train(name)
    model = bundle["model"]
    meta = bundle["meta"]

    lang_code = _encode(meta["lang_codes"], language, meta["lang_mode"])
    status_code = _encode(meta["status_codes"], status, meta["status_mode"])

    row = pd.DataFrame([{
        "budget": float(budget),
        "popularity": float(popularity),
        "runtime": float(runtime),
        "original_language_code": lang_code,
        "status_code": status_code,
    }])[FEATURE_NAMES]

    pred = float(model.predict(row)[0])
    return pred, trained_now, bundle["metrics"], cache_path(name)


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)


def main():
    model_name = None
    try:
        parser = _Parser(prog="predict_api.py")
        parser.add_argument("--model", default="lgbm",
                            choices=["lr", "knn", "svm", "dt", "rf", "lgbm"])
        parser.add_argument("--budget", type=float, default=100000000.0, help="预算（美元）")
        parser.add_argument("--popularity", type=float, default=10.0, help="热度 popularity")
        parser.add_argument("--runtime", type=int, default=100, help="时长（分钟）")
        parser.add_argument("--language", default="en", help="原始语言代码，如 en/zh/ja")
        parser.add_argument("--status", default="Released", help="状态，如 Released/Rumored")
        parser.add_argument("--train", action="store_true", help="仅训练并缓存模型后退出")
        args = parser.parse_args()

        model_name = args.model
        if args.train:
            met = train_and_cache(model_name)
            print(json.dumps({
                "model": model_name,
                "trained": True,
                "cache_file": cache_path(model_name),
                "metrics": met,
            }, ensure_ascii=False))
            sys.exit(0)

        pred, trained_now, met, cfile = predict(
            model_name, args.budget, args.popularity, args.runtime,
            args.language, args.status,
        )
        print(json.dumps({
            "model": model_name,
            "prediction": pred,
            "currency": "USD",
            "trained_now": trained_now,
            "cache_file": cfile,
            "metrics": met,
        }, ensure_ascii=False))
        sys.exit(0)
    except BaseException as exc:  # noqa: BLE001 - 统一转成契约 JSON
        if isinstance(exc, SystemExit) and exc.code == 0:
            raise
        print(json.dumps({
            "model": model_name,
            "error": str(exc),
            "trace": traceback.format_exc(),
        }, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    _stdout_reconfigure()
    main()
