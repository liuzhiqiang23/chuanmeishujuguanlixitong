# -*- coding: utf-8 -*-
"""
推理一致性校验：把训练集样本回灌给在线推理脚本，比较预测值与真实票房。

用途：验证「离线训练 → 在线推理」两端特征处理完全一致（同一份 feature_meta.json、
同一套编码规则），避免训练/推理特征错位导致线上预测失真。

用法：
    .venv\\Scripts\\python.exe tools/verify_inference_consistency.py [样本数，默认 500]

注意：样本取自训练集，属于**样本内**拟合（in-sample），指标优于离线验证集是正常的，
本脚本关注的是「相关性极高 + 无系统性偏移」，而不是模型泛化能力。
"""
import json
import os
import subprocess
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(ROOT, ".venv", "Scripts", "python.exe")
SCRIPT = os.path.join(ROOT, "algorithm", "boxoffice_prediction", "predict_api.py")
CSV = os.path.join(ROOT, "data", "processed", "train_clean.csv")
OUT = os.path.join(ROOT, "tools", "_consistency.jsonl")


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 500

    cmd = [PY, SCRIPT, "--batch", CSV, "--limit", str(limit), "--out", OUT]
    print("运行:", " ".join(os.path.basename(c) if os.path.isabs(c) else c for c in cmd))
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=300)
    if proc.returncode != 0:
        print(proc.stdout[-800:])
        print(proc.stderr[-800:])
        return 1
    summary = json.loads(proc.stdout.strip().splitlines()[-1])
    print("批量推理:", summary)

    pred = {}
    with open(OUT, encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            pred[int(row["movieId"])] = float(row["logRevenue"])

    df = pd.read_csv(CSV, low_memory=False).head(limit)
    df = df[df["id"].isin(pred.keys())].copy()
    df["pred_log"] = df["id"].map(pred)
    df = df.dropna(subset=["log_revenue", "pred_log"])

    y, p = df["log_revenue"].to_numpy(), df["pred_log"].to_numpy()
    rmse = float(np.sqrt(np.mean((y - p) ** 2)))
    mae = float(np.mean(np.abs(y - p)))
    ss_res, ss_tot = float(np.sum((y - p) ** 2)), float(np.sum((y - y.mean()) ** 2))
    r2 = 1 - ss_res / ss_tot
    corr = float(np.corrcoef(y, p)[0, 1])
    bias = float(np.mean(p - y))

    print("\n样本内一致性（n=%d）" % len(df))
    print("  RMSE = %.4f   MAE = %.4f   R² = %.4f" % (rmse, mae, r2))
    print("  预测/真实相关系数 = %.4f   平均偏差(预测-真实) = %+.4f" % (corr, bias))
    print("  → log10 尺度上 0.1 的偏差≈票房相差 %.0f%%" % ((10 ** 0.1 - 1) * 100))

    ok = corr > 0.9 and abs(bias) < 0.15
    print("\n判定：%s（相关性>0.9 且无系统性偏移）" % ("PASS" if ok else "FAIL"))
    json.dump({"n": len(df), "rmse": round(rmse, 4), "mae": round(mae, 4),
               "r2": round(r2, 4), "corr": round(corr, 4), "bias": round(bias, 4),
               "pass": ok},
              open(os.path.join(ROOT, "tools", "verify_consistency_result.json"), "w",
                   encoding="utf-8"), ensure_ascii=False, indent=2)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
