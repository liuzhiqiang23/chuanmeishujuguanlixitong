# -*- coding: utf-8 -*-
"""
探索性数据分析（EDA）与特征可视化
==================================
输入：原始 train.csv（含票房 revenue），复用 preprocess 清洗流水线
输出：algorithm/FeatureEDA/figures/ 下 21 张分析图（PNG）
      —— fig01~fig14 为多维度分析图，另有 7 张固定文件名图供网页「特征探索分析」引用

运行：
    python algorithm/FeatureEDA/eda.py

图形清单：
    fig01 票房收入分布（原值 vs 对数）
    fig02 制作预算分布
    fig03 预算-票房 相关关系
    fig04 每年上映电影数量趋势
    fig05 年度总票房与平均票房趋势
    fig06 Top 电影类型（电影数量）
    fig07 主要类型票房对比（箱线图）
    fig08 主要制作国分析（数量与平均票房）
    fig09 Top 制作公司（总票房）
    fig10 Top 导演（平均票房）
    fig11 流行度与票房的关系
    fig12 电影时长分析（分布与票房）
    fig13 上映月份的季节性票房规律
    fig14 Top 关键词
"""
import os
import sys

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

sys.stdout.reconfigure(encoding="utf-8")

import seaborn as sns

from preprocess import build_data, DATA_DIR

# ---------------------------------------------------------------------------
# 全局配置
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))    # .../algorithm/FeatureEDA
FIG_DIR = os.path.join(SCRIPT_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 110
plt.rcParams["savefig.dpi"] = 160
plt.rcParams["figure.facecolor"] = "white"

# 统一的类型配色（取自 tab20）
PALETTE = plt.get_cmap("tab20").colors

# 图形序号
_FIG_NO = 0


def next_fig(name: str) -> str:
    """自动递增文件名：fig01_xxx.png"""
    global _FIG_NO
    _FIG_NO += 1
    return os.path.join(FIG_DIR, f"fig{_FIG_NO:02d}_{name}.png")


def annotate_bar(ax, fmt="{:.0f}", fontsize=9, offset=0.3, **kw):
    """在横向/纵向条形上标注数值；fmt 可为格式化串或 callable"""
    bars = ax.patches
    text = (lambda v: fmt(v)) if callable(fmt) else (lambda v: fmt.format(v))
    # 横向条形图（barh）时，条的宽度 > 高度；据此区分方向
    if len(bars) and bars[0].get_width() > bars[0].get_height():
        for b in bars:
            ax.annotate(text(b.get_width()),
                        xy=(b.get_width(), b.get_y() + b.get_height() / 2),
                        xytext=(offset, 0), textcoords="offset points",
                        va="center", ha="left", fontsize=fontsize, **kw)
    else:
        for b in bars:
            ax.annotate(text(b.get_height()),
                        xy=(b.get_x() + b.get_width() / 2, b.get_height()),
                        xytext=(0, offset), textcoords="offset points",
                        ha="center", va="bottom", fontsize=fontsize, **kw)


def corr(x, y, method="pearson"):
    return pd.Series(x).corr(pd.Series(y), method=method)


def money_fmt(x, pos=None):
    """1e6 -> 1亿, 1e7 -> 10亿? 用亿/千万中文单位。统一用 '1.2亿' 风格做格式化"""
    if x >= 1e8:
        return f"{x / 1e8:.1f}亿"
    if x >= 1e4:
        return f"{x / 1e4:.0f}万"
    return f"{x:.0f}"


# ---------------------------------------------------------------------------
# 1. 票房收入分布
# ---------------------------------------------------------------------------
def fig01_revenue_distribution(df):
    rev = df["revenue"]
    f, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    ax = axes[0]
    ax.hist(rev, bins=60, color=PALETTE[0], alpha=0.85, edgecolor="white")
    ax.axvline(rev.mean(), color="crimson", ls="--", lw=1.5, label=f"均值 {rev.mean() / 1e8:.2f}亿")
    ax.axvline(rev.median(), color="darkorange", ls="--", lw=1.5, label=f"中位数 {rev.median() / 1e4:.0f}万")
    ax.set_title("票房收入分布（原始尺度，严重右偏）")
    ax.set_xlabel("票房 revenue（美元）")
    ax.set_ylabel("电影数量")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(money_fmt))
    ax.legend()

    ax = axes[1]
    logr = np.log10(rev)
    ax.hist(logr, bins=60, color=PALETTE[1], alpha=0.85, edgecolor="white", density=True)
    logr.plot.kde(ax=ax, color="crimson", lw=2, label="KDE 密度曲线")
    ax.axvline(logr.mean(), color="darkorange", ls="--", lw=1.5,
               label=f"log10 均值 {logr.mean():.2f}（≈{10 ** logr.mean() / 1e6:.0f} 百万美元）")
    ax.set_title("票房收入分布（log10 对数尺度，近似正态）")
    ax.set_xlabel("log10(票房 revenue)")
    ax.set_ylabel("密度")
    ax.legend()

    f.suptitle("图1 票房收入分布：长尾分布，建模/可视化需对数变换", fontsize=13, y=1.02)
    f.tight_layout()
    f.savefig(next_fig("revenue_distribution"), bbox_inches="tight")
    plt.close(f)
    print(f"[fig01] revenue 均值={rev.mean() / 1e8:.2f}亿  中位数={rev.median() / 1e4:.0f}万  "
          f"max={rev.max() / 1e8:.1f}亿  偏度={rev.skew():.1f}")


# ---------------------------------------------------------------------------
# 2. 预算分布
# ---------------------------------------------------------------------------
def fig02_budget_distribution(df):
    valid = df["budget"].dropna()
    zero_n = df["budget"].isna().sum()
    f, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    ax = axes[0]
    logb = np.log10(valid)
    ax.hist(logb, bins=50, color=PALETTE[2], alpha=0.85, edgecolor="white", density=True)
    logb.plot.kde(ax=ax, color="crimson", lw=2)
    ax.set_title(f"有效预算的 log10 分布（n={len(valid)}）")
    ax.set_xlabel("log10(预算 budget)")
    ax.set_ylabel("密度")

    ax = axes[1]
    lbl = ["预算缺失\n(budget=0)", "有效预算"]
    vals = [zero_n, len(valid)]
    bars = ax.bar(lbl, vals, color=[PALETTE[3], PALETTE[2]], alpha=0.9, width=0.55)
    for b, v in zip(bars, vals):
        ax.annotate(f"{v} ({v / len(df) * 100:.1f}%)",
                    xy=(b.get_x() + b.get_width() / 2, v), xytext=(0, 3),
                    textcoords="offset points", ha="center", fontsize=11)
    ax.set_title("预算披露情况")
    ax.set_ylabel("电影数量")
    ax.set_ylim(0, max(vals) * 1.15)

    f.suptitle("图2 制作预算分布：预算集中于中低档，且 27% 电影预算未知", fontsize=13, y=1.02)
    f.tight_layout()
    f.savefig(next_fig("budget_distribution"), bbox_inches="tight")
    plt.close(f)
    print(f"[fig02] 预算有效 {len(valid)} 部（中位数 {10 ** logb.median() / 1e6:.0f} 百万美元），缺失 {zero_n} 部")


# ---------------------------------------------------------------------------
# 3. 预算-票房散点
# ---------------------------------------------------------------------------
def fig03_budget_revenue(df):
    d = df.dropna(subset=["budget", "revenue"])
    d = d[(d["revenue"] > 0)]
    x, y = np.log10(d["budget"]), np.log10(d["revenue"])
    r_p = corr(x, y, "pearson")
    r_s = corr(x, y, "spearman")

    fig, ax = plt.subplots(figsize=(9.5, 7))
    hb = ax.hexbin(x, y, gridsize=42, cmap="YlOrRd", mincnt=1, alpha=0.9)
    cb = fig.colorbar(hb, ax=ax, pad=0.01)
    cb.set_label("电影数量")
    # 回归线
    k = np.polyfit(x, y, 1)
    xs = np.linspace(x.min(), x.max(), 100)
    ax.plot(xs, np.polyval(k, xs), "b-", lw=2, label="线性拟合")
    ax.plot([], [])  # placeholder
    ax.set_xlabel("log10(预算 budget)")
    ax.set_ylabel("log10(票房 revenue)")
    ax.set_title(f"预算 vs 票房（对数尺度）\nPearson r={r_p:.3f} | Spearman ρ={r_s:.3f}")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(next_fig("budget_revenue_scatter"), bbox_inches="tight")
    plt.close(fig)
    print(f"[fig03] 有效样本 {len(d)}，Pearson={r_p:.3f}，Spearman={r_s:.3f}：高预算总体上带来高票房，但方差很大（存在叫好不叫座）")


# ---------------------------------------------------------------------------
# 4. 每年上映数量
# ---------------------------------------------------------------------------
def fig04_movies_by_year(df):
    d = df.dropna(subset=["year"]).copy()
    yearly = d.groupby("year").size()

    fig, ax = plt.subplots(figsize=(13, 5.5))
    ax.bar(yearly.index, yearly.values, color=PALETTE[4], width=0.8, label="每年上映数量")
    # 5 年移动平均
    ma = yearly.rolling(5, center=True).mean()
    ax.plot(ma.index, ma.values, "crimson", lw=2.5, marker="o", ms=4, label="5年移动平均")
    ax.set_title("每年上映电影数量（1976–2026，样本内）")
    ax.set_xlabel("年份")
    ax.set_ylabel("上映数量（部）")
    ax.grid(axis="y", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(next_fig("movies_by_year"), bbox_inches="tight")
    plt.close(fig)
    print(f"[fig04] 年均上映 {yearly.mean():.0f} 部；数量快速增长阶段大致为 1995–2020")


# ---------------------------------------------------------------------------
# 5. 年度总票房与平均票房
# ---------------------------------------------------------------------------
def fig05_revenue_trend_by_year(df):
    d = df.dropna(subset=["year"]).copy()
    g = d.groupby("year")["revenue"].agg(total="sum", mean="mean", count="size")
    g = g[g["count"] >= 5]  # 早期样本太少时剔除

    fig, ax = plt.subplots(figsize=(13, 6))
    ax.bar(g.index, g["total"] / 1e8, color=PALETTE[5], alpha=0.85, width=0.8, label="年度总票房（亿美元）")
    ax.set_ylabel("年度总票房（亿美元）")
    ax.set_xlabel("年份")

    ax2 = ax.twinx()
    ax2.plot(g.index, g["mean"] / 1e6, "darkgreen", lw=2.5, marker="s", ms=4, label="平均单片票房（百万美元）")
    ax2.set_ylabel("平均单片票房（百万美元）")
    ax2.grid(alpha=0.25)

    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left")
    ax.set_title("年度总票房与单片平均票房走势")
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(next_fig("revenue_trend_by_year"), bbox_inches="tight")
    plt.close(fig)
    print(f"[fig05] 单片平均票房近十年约 {g['mean'].tail(8).mean() / 1e6:.0f} 百万美元")


# ---------------------------------------------------------------------------
# 6. Top 类型（多标签展开计数）
# ---------------------------------------------------------------------------
def fig06_top_genres(df):
    from collections import Counter
    cnt = Counter()
    for lst in df["genres_list"]:
        cnt.update(lst)
    top = pd.Series(cnt).sort_values(ascending=False).head(15)

    fig, ax = plt.subplots(figsize=(11, 6.5))
    top.iloc[::-1].plot.barh(ax=ax, color=PALETTE[0], alpha=0.9)
    annotate_bar(ax, offset=-28, color="white", fontsize=10)
    ax.set_title("出现次数最多的 15 个电影类型（一部电影可属于多个类型）")
    ax.set_xlabel("电影数量（部）")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(next_fig("top_genres_count"), bbox_inches="tight")
    plt.close(fig)
    print(f"[fig06] Top3 类型: {', '.join(top.index[:3])}")


# ---------------------------------------------------------------------------
# 7. 主要类型票房对比（箱线图）
# ---------------------------------------------------------------------------
def fig07_genre_box_revenue(df):
    d = df[df["main_genre"] != "Unknown"].dropna(subset=["revenue"]).copy()
    vc = d["main_genre"].value_counts()
    keep = vc[vc >= 30].index  # 样本量足够才比较
    d = d[d["main_genre"].isin(keep)]
    d["log_rev"] = np.log10(d["revenue"])
    order = d.groupby("main_genre")["log_rev"].median().sort_values().index

    fig, ax = plt.subplots(figsize=(12, 7.5))
    data = [d.loc[d["main_genre"] == g, "log_rev"].values for g in order]
    bp = ax.boxplot(data, tick_labels=order, vert=False, patch_artist=True, widths=0.65,
                    medianprops=dict(color="crimson", lw=2), flierprops=dict(markersize=2.5, alpha=0.35))
    for patch, i in zip(bp["boxes"], range(len(order))):
        patch.set_facecolor(PALETTE[i % len(PALETTE)])
        patch.set_alpha(0.75)
    ax.set_title("主要类型电影的票房分布（log10 票房，仅展示样本量≥30 的类型）")
    ax.set_xlabel("票房 revenue（美元）")

    def log_ticks(v, p):
        actual = 10 ** v
        if actual >= 1e8:
            return f"{actual / 1e8:.0f}亿"
        if actual >= 1e6:
            return f"{actual / 1e6:.0f}百万"
        return f"{actual / 1e4:.0f}万"

    ax.xaxis.set_major_locator(mticker.FixedLocator([5, 6, 7, 8, 9]))
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(log_ticks))
    fig.tight_layout()
    fig.savefig(next_fig("genre_revenue_box"), bbox_inches="tight")
    plt.close(fig)
    print(f"[fig07] 中位票房最高的类型: {order[-1]}（10^{d[d['main_genre']==order[-1]]['log_rev'].median():.2f}）")


# ---------------------------------------------------------------------------
# 8. 主要制作国
# ---------------------------------------------------------------------------
def fig08_country_analysis(df):
    d = df[df["main_country"] != "Unknown"].dropna(subset=["revenue"]).copy()
    g = d.groupby("main_country")["revenue"].agg(count="size", mean="mean", median="median")
    top = g[g["count"] >= 20].sort_values("count", ascending=False).head(12)

    fig, axes = plt.subplots(1, 2, figsize=(15, 6.5))
    ax = axes[0]
    top["count"].iloc[::-1].plot.barh(ax=ax, color=PALETTE[3], alpha=0.9)
    annotate_bar(ax, offset=-26, color="white", fontsize=9)
    ax.set_title("主要制作国：电影数量 Top12（样本量≥20）")
    ax.set_xlabel("电影数量")
    ax.grid(axis="x", alpha=0.3)

    ax = axes[1]
    top.sort_values("mean")["mean"].plot.barh(ax=ax, color=PALETTE[2], alpha=0.9)
    annotate_bar(ax, fmt=lambda x: f"{x / 1e8:.2f}亿" if x >= 1e8 else f"{x / 1e6:.0f}百万",
                 offset=-70, color="white", fontsize=9)
    ax.set_title("主要制作国：平均单片票房（美元）")
    ax.set_xlabel("平均票房（美元）")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(money_fmt))
    ax.grid(axis="x", alpha=0.3)

    fig.suptitle("图8 美国主导制作数量；非英语市场单片票房均值可更高（样本异质性）", fontsize=12, y=1.0)
    fig.tight_layout()
    fig.savefig(next_fig("country_analysis"), bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 9. Top 制作公司（总票房）
# ---------------------------------------------------------------------------
def fig09_top_companies(df):
    rows = []
    for lst, rev in zip(df["companies_list"], df["revenue"]):
        for c in lst:
            rows.append((c, rev))
    comp = pd.DataFrame(rows, columns=["company", "revenue"])
    g = comp.groupby("company")["revenue"].agg(total="sum", count="size")
    top = g.sort_values("total", ascending=False).head(15)

    fig, ax = plt.subplots(figsize=(11.5, 7))
    top["total"].iloc[::-1].plot.barh(ax=ax, color=PALETTE[1], alpha=0.9)
    for i, (idx, row) in enumerate(top.iloc[::-1].iterrows()):
        ax.annotate(f"{money_fmt(row['total'])}  (n={int(row['count'])})",
                    xy=(row["total"], i), xytext=(4, 0), textcoords="offset points",
                    va="center", fontsize=9.5)
    ax.set_title("累计票房最高的 15 家制作公司（联合制片将票房计入各家）")
    ax.set_xlabel("累计总票房（美元）")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(money_fmt))
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(next_fig("top_companies"), bbox_inches="tight")
    plt.close(fig)
    print(f"[fig09] 累计票房冠军公司: {top.index[0]}")


# ---------------------------------------------------------------------------
# 10. Top 导演（平均票房，要求≥5部）
# ---------------------------------------------------------------------------
def fig10_top_directors(df):
    d = df.dropna(subset=["director", "revenue"]).copy()
    g = d.groupby("director")["revenue"].agg(count="size", mean="mean")
    g = g[g["count"] >= 5]
    top = g.sort_values("mean", ascending=False).head(12)

    fig, ax = plt.subplots(figsize=(11.5, 7))
    top["mean"].iloc[::-1].plot.barh(ax=ax, color=PALETTE[5], alpha=0.9)
    for i, (idx, row) in enumerate(top.iloc[::-1].iterrows()):
        ax.annotate(f"{money_fmt(row['mean'])}  (n={int(row['count'])})",
                    xy=(row["mean"], i), xytext=(4, 0), textcoords="offset points",
                    va="center", fontsize=9.5)
    ax.set_title("平均票房最高的 12 位导演（样本内至少执导 5 部）")
    ax.set_xlabel("平均单片票房（美元）")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(money_fmt))
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(next_fig("top_directors"), bbox_inches="tight")
    plt.close(fig)
    print(f"[fig10] Top 导演: {', '.join(top.index[:5])}")


# ---------------------------------------------------------------------------
# 11. 流行度与票房
# ---------------------------------------------------------------------------
def fig11_popularity_revenue(df):
    d = df[(df["popularity"] > 0) & (df["revenue"] > 0)].copy()
    x, y = np.log10(d["popularity"]), np.log10(d["revenue"])
    r_p = corr(x, y, "pearson")
    r_s = corr(x, y, "spearman")

    fig, ax = plt.subplots(figsize=(9.5, 7))
    ax.scatter(x, y, s=14, alpha=0.5, color=PALETTE[6], edgecolors="none")
    k = np.polyfit(x, y, 1)
    xs = np.linspace(x.min(), x.max(), 100)
    ax.plot(xs, np.polyval(k, xs), "crimson", lw=2, label="线性拟合")
    ax.set_xlabel("log10(popularity 热度)")
    ax.set_ylabel("log10(票房 revenue)")
    ax.set_title(f"热度(popularity)与票房的关系\nPearson r={r_p:.3f} | Spearman ρ={r_s:.3f}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(next_fig("popularity_revenue"), bbox_inches="tight")
    plt.close(fig)
    print(f"[fig11] popularity 与 revenue 相关（Pearson={r_p:.3f}）—— TMDB 热度对票房有较强指示性")


# ---------------------------------------------------------------------------
# 12. 时长分析
# ---------------------------------------------------------------------------
def fig12_runtime_analysis(df):
    d = df.dropna(subset=["runtime", "revenue"]).copy()
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    ax = axes[0]
    ax.hist(d["runtime"], bins=40, color=PALETTE[7], alpha=0.85, edgecolor="white")
    ax.axvline(d["runtime"].mean(), color="crimson", ls="--", lw=1.5, label=f"均值 {d['runtime'].mean():.0f} 分钟")
    ax.axvline(d["runtime"].median(), color="darkorange", ls="--", lw=1.5, label=f"中位数 {d['runtime'].median():.0f} 分钟")
    ax.set_title("电影时长分布")
    ax.set_xlabel("时长 runtime（分钟）")
    ax.set_ylabel("电影数量")
    ax.legend()

    ax = axes[1]
    bins = [0, 90, 105, 120, 135, 150, np.inf]
    labels = ["<90", "90–105", "105–120", "120–135", "135–150", ">150"]
    d["rt_bin"] = pd.cut(d["runtime"], bins=bins, labels=labels, right=False)
    g = d.groupby("rt_bin", observed=True).agg(mean_rev=("revenue", "mean"),
                                               count=("revenue", "size"))
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(g))]
    g["mean_rev"].plot.bar(ax=ax, color=colors, alpha=0.9, width=0.6)
    for i, (idx, row) in enumerate(g.iterrows()):
        ax.annotate(f"{row['mean_rev'] / 1e7:.1f}千万\n(n={int(row['count'])})",
                    xy=(i, row["mean_rev"]), xytext=(0, 3), textcoords="offset points",
                    ha="center", fontsize=9)
    ax.set_title("时长分箱 vs 平均票房")
    ax.set_xlabel("时长区间（分钟）")
    ax.set_ylabel("平均票房（美元）")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(money_fmt))

    fig.suptitle("图12 片长集中 90–120 分钟；长片（120–150 分钟）平均票房更高", fontsize=12, y=1.02)
    fig.tight_layout()
    fig.savefig(next_fig("runtime_analysis"), bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 13. 上映月份季节性
# ---------------------------------------------------------------------------
def fig13_release_month(df):
    d = df.dropna(subset=["month", "revenue"]).copy()
    g = d.groupby("month")["revenue"].agg(mean="mean", count="size")
    month_names = ["1月", "2月", "3月", "4月", "5月", "6月",
                   "7月", "8月", "9月", "10月", "11月", "12月"]

    fig, ax = plt.subplots(figsize=(13, 6))
    ax.bar(month_names, g["count"].values, color=PALETTE[8], alpha=0.85, label="上映数量（部）")
    ax.set_ylabel("上映数量（部）", color=PALETTE[8])
    ax2 = ax.twinx()
    ax2.plot(month_names, g["mean"].values / 1e8, "crimson", marker="o", lw=2.5,
             label="平均票房（亿美元）")
    ax2.set_ylabel("平均单片票房（亿美元）", color="crimson")
    ax2.grid(alpha=0.25)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left")
    ax.set_title("上映月份的季节效应：暑期档(6–8月)与圣诞档(11–12月)票房更高")
    fig.tight_layout()
    fig.savefig(next_fig("release_month"), bbox_inches="tight")
    plt.close(fig)
    best = int(g["mean"].idxmax())
    print(f"[fig13] 单片平均票房最高的月份: {best}月（{g['mean'].max() / 1e8:.2f}亿）")


# ---------------------------------------------------------------------------
# 14. Top 关键词
# ---------------------------------------------------------------------------
def fig14_top_keywords(df):
    from collections import Counter
    cnt = Counter()
    for lst in df["keywords_list"]:
        cnt.update(lst)
    top = pd.Series(cnt).sort_values(ascending=False).head(20)

    fig, ax = plt.subplots(figsize=(11, 7.5))
    top.iloc[::-1].plot.barh(ax=ax, color=PALETTE[1], alpha=0.9)
    annotate_bar(ax, offset=-30, color="white", fontsize=9.5)
    ax.set_title("出现频率最高的 20 个电影关键词")
    ax.set_xlabel("出现次数")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(next_fig("top_keywords"), bbox_inches="tight")
    plt.close(fig)
    print(f"[fig14] Top5 关键词: {', '.join(top.index[:5])}")


# ---------------------------------------------------------------------------
# 15~21. 单特征 / 相关性图
#        说明：原 single_feature_visual.py 的绘图内容已合并到本脚本，
#        使用原始 data/train.csv 并外链上映规模(theatrical)与热度(popularity2)；
#        这 7 张采用**固定文件名**（前端「特征探索分析」页面按文件名引用），
#        因此不走 next_fig 序号，改用 fixed_fig 以便统一计数。
# ---------------------------------------------------------------------------

# 原始数据里 budget/revenue 的明显异常值人工核对修正（沿用原脚本核对结果）
# 注：原脚本对 test 的 budget 修正未参与任何绘图，此处不再保留
_SF_BUDGET_FIX = {
    90: 30000000, 118: 60000000, 149: 18000000, 464: 20000000, 470: 13000000,
    513: 1100000, 797: 8000000, 819: 90000000, 850: 1500000, 1007: 2,
    1112: 7500000, 1131: 4300000, 1359: 10000000, 1542: 1, 1570: 15800000,
    1571: 4000000, 1714: 46000000, 1721: 17500000, 1885: 12, 2091: 10,
    2268: 17500000, 2491: 6, 2602: 31000000, 2612: 15000000, 2696: 10000000,
    2801: 10000000, 335: 2, 348: 12, 640: 6, 696: 1, 1199: 5,
    1282: 9, 1347: 1, 1755: 2, 1801: 5, 1918: 592, 2033: 4,
    2118: 344, 2252: 130, 2256: 1,
}
_SF_REVENUE_FIX = {16: 192864, 313: 12000000, 451: 12000000, 1865: 25000000}


def fixed_fig(name: str) -> str:
    """固定文件名（供前端页面按名引用），同样计入生成总数"""
    global _FIG_NO
    _FIG_NO += 1
    return os.path.join(FIG_DIR, name)


def load_single_feature_data():
    """加载单特征图所需的 train：合并上映规模 theatrical 与热度 popularity2"""
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"))
    for i, v in _SF_REVENUE_FIX.items():
        train.loc[train["id"] == i, "revenue"] = v
    for i, v in _SF_BUDGET_FIX.items():
        train.loc[train["id"] == i, "budget"] = v

    # 上映国家表：提供各片的上映规模 theatrical
    release_dates = pd.read_csv(
        os.path.join(DATA_DIR, "prediction", "release_dates_per_country.csv"))
    release_dates["id"] = range(1, len(release_dates) + 1)
    release_dates.drop(["original_title", "title"], axis=1, inplace=True)
    train = pd.merge(train, release_dates, how="left", on=["id"])

    # 附加特征表：提供 popularity2（TMDB 热度）与 rating
    extra = pd.read_csv(
        os.path.join(DATA_DIR, "prediction", "TrainAdditionalFeatures.csv"))[
        ["imdb_id", "popularity2", "rating"]]
    train = pd.merge(train, extra, how="left", on=["imdb_id"])
    return train


def fig15_revenue_budget(df):
    fig = plt.figure(figsize=(9, 5))
    plt.scatter(df["budget"], df["revenue"], c=["green"], marker="o")
    plt.grid()
    plt.xlabel("budget", fontsize=10)
    plt.ylabel("revenue", fontsize=10)
    plt.title("Link between revenue and budget", fontsize=10)
    plt.savefig(fixed_fig("revenue_budget.png"))
    plt.close(fig)
    print(f"[fig15] 票房~预算 相关系数={corr(df['budget'], df['revenue']):.3f}")


def fig16_revenue_popularity(df):
    fig = plt.figure(figsize=(9, 5))
    plt.scatter(df["popularity2"], df["revenue"], c=["green"], marker="o")
    plt.grid()
    plt.xlabel("popularity", fontsize=10)
    plt.ylabel("revenue", fontsize=10)
    plt.title("Link between popularity and revenue", fontsize=10)
    plt.savefig(fixed_fig("revenue_popularity.png"))
    plt.close(fig)
    print(f"[fig16] 票房~热度 相关系数={corr(df['popularity2'], df['revenue']):.3f}")


def fig17_revenue_theatrical(df):
    fig = plt.figure(figsize=(9, 5))
    plt.scatter(df["theatrical"], df["revenue"], c=["green"], marker="o")
    plt.grid()
    plt.xlabel("theatrical", fontsize=10)
    plt.ylabel("revenue", fontsize=10)
    plt.title("Link between theatrical and revenue", fontsize=10)
    plt.savefig(fixed_fig("revenue_theatrical.png"))
    plt.close(fig)
    print(f"[fig17] 票房~上映规模 相关系数={corr(df['theatrical'], df['revenue']):.3f}")


def fig18_revenue_language(df):
    top_lang = df["original_language"].value_counts()[:10].index.values
    g1 = sns.boxenplot(x="original_language", y="revenue",
                       data=df[df["original_language"].isin(top_lang)])
    g1.set_title("Revenue by original language's movies", fontsize=20)
    g1.set_xticklabels(g1.get_xticklabels(), rotation=45)
    g1.set_xlabel("Original language", fontsize=18)
    g1.set_ylabel("Revenue", fontsize=18)
    plt.savefig(fixed_fig("revenue_language.png"), bbox_inches="tight")
    plt.close()
    print("[fig18] 不同语种电影票房分布")


def fig19_budget_recent_year(df):
    top_years = df["release_year"].value_counts()[:5].index.values
    (sns.FacetGrid(df[df["release_year"].isin(top_years)],
                   hue="release_year", height=5, aspect=2)
     .map(sns.kdeplot, "budget", fill=True)
     .add_legend())
    plt.title("Budget by all years")
    plt.savefig(fixed_fig("budget_recent_year.png"), bbox_inches="tight")
    plt.close()
    print(f"[fig19] 主要年份预算分布: {sorted(top_years)}")


def fig20_revenue_year(df):
    plt.figure(figsize=(12, 5))
    ax = sns.histplot(np.log1p(df["revenue"]), bins=40, kde=True)
    ax.set_xlabel("Revenue", fontsize=15)
    ax.set_ylabel("Distribuition", fontsize=15)
    ax.set_title("Distribuition of Revenue", fontsize=20)
    plt.savefig(fixed_fig("revenue_year.png"), bbox_inches="tight")
    plt.close()
    print("[fig20] 票房分布直方图（log1p 归一）")


def fig21_corre(df):
    col = ["revenue", "budget", "popularity2", "theatrical", "runtime",
           "id", "release_year"]
    plt.subplots(figsize=(14, 10))
    sns.heatmap(df[col].corr(), xticklabels=col, yticklabels=col,
                linewidths=.5, cmap="Reds")
    plt.savefig(fixed_fig("corre.png"), bbox_inches="tight")
    plt.close()
    print("[fig21] 特征相关性热力图")


# ---------------------------------------------------------------------------
def main():
    print("正在加载/清洗数据 ...")
    train, _ = build_data()
    print(f"EDA 样本: train {train.shape}\n")

    # 有效票房/剔除异常便于各图分析
    train_valid = train[train["revenue"] > 0].copy()

    fig01_revenue_distribution(train_valid)
    fig02_budget_distribution(train_valid)
    fig03_budget_revenue(train_valid)
    fig04_movies_by_year(train)
    fig05_revenue_trend_by_year(train)
    fig06_top_genres(train)
    fig07_genre_box_revenue(train)
    fig08_country_analysis(train)
    fig09_top_companies(train)
    fig10_top_directors(train)
    fig11_popularity_revenue(train_valid)
    fig12_runtime_analysis(train_valid)
    fig13_release_month(train_valid)
    fig14_top_keywords(train)

    # 15~21：单特征 / 相关性图（固定文件名，供网页「特征探索分析」引用）
    print("\n正在加载单特征图所需数据 ...")
    sf_train = load_single_feature_data()
    fig15_revenue_budget(sf_train)
    fig16_revenue_popularity(sf_train)
    fig17_revenue_theatrical(sf_train)
    fig18_revenue_language(sf_train)
    fig19_budget_recent_year(sf_train)
    fig20_revenue_year(sf_train)
    fig21_corre(sf_train)

    print(f"\n共生成 {_FIG_NO} 张图，保存目录: {FIG_DIR}")


if __name__ == "__main__":
    main()
