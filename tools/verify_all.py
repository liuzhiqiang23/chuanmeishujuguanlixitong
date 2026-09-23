# -*- coding: utf-8 -*-
"""
第七步 联调验收脚本：一次性跑通「前端 → 后端 → 算法」全部接口。

用法（后端已启动在 8000 端口）：
    .venv\\Scripts\\python.exe tools/verify_all.py

输出：逐项 PASS/FAIL 的验收表 + 关键证据，可直接贴进《系统联调与测试记录》。
"""
import json
import sys
import time

import requests

BASE = "http://127.0.0.1:8000"
ADMIN_USER = "柳志强"
ADMIN_PASS = "200306"

results = []


def check(name, method, path, resp, ok_extra=None, evidence=None, expect_code=1):
    """记录一次调用结果。expect_code: 业务 code；None 表示只看 HTTP 2xx/3xx"""
    try:
        body = resp.json()
    except ValueError:
        body = {}
    code = body.get("code")
    http_ok = 200 <= resp.status_code < 400
    code_ok = True if expect_code is None else (code == expect_code)
    passed = http_ok and code_ok
    if ok_extra is not None:
        try:
            passed = passed and bool(ok_extra(body))
        except Exception:
            passed = False
    results.append({
        "name": name,
        "call": "%s %s" % (method, path),
        "http": resp.status_code,
        "code": code,
        "pass": passed,
        "evidence": evidence(body) if callable(evidence) else (evidence or ""),
        "message": body.get("message", ""),
    })
    mark = "PASS" if passed else "FAIL"
    print("[%s] %-28s %s %s -> HTTP %s code=%s %s"
          % (mark, name, method, path, resp.status_code, code, body.get("message", "")))
    return body


def main():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json", "request-ajax": "true"})

    # ---------- 1. 登录（Cookie 会话）----------
    r = s.post(BASE + "/api/user/login",
               data=json.dumps({"userName": ADMIN_USER, "password": ADMIN_PASS,
                                "remember": True}).encode("utf-8"))
    check("管理员登录", "POST", "/api/user/login", r,
          evidence=lambda b: "cookie=%s" % (",".join(s.cookies.keys()) or "无"))

    # ---------- 2. 影片库：统计 / 分页 / 详情 ----------
    r = s.get(BASE + "/api/movie/stats")
    check("影片库统计", "GET", "/api/movie/stats", r,
          ok_extra=lambda b: b.get("response", {}).get("total") == 10000,
          evidence=lambda b: "total=%s withRevenue=%s 年份=%s 类型=%s"
                             % (b["response"]["total"], b["response"]["withRevenue"],
                                b["response"]["yearRange"],
                                b["response"]["genreTop"][0]))

    r = s.post(BASE + "/api/movie/page",
               data=json.dumps({"pageIndex": 1, "pageSize": 5, "sortBy": "popularity"}).encode("utf-8"))
    check("影片分页（按热度）", "POST", "/api/movie/page", r,
          ok_extra=lambda b: len(b.get("response", {}).get("list", [])) == 5,
          evidence=lambda b: "total=%s 首条=%s(热度%.1f)"
                             % (b["response"]["total"], b["response"]["list"][0]["title"],
                                b["response"]["list"][0].get("popularity") or 0))

    r = s.post(BASE + "/api/movie/page",
               data=json.dumps({"pageIndex": 1, "pageSize": 3, "genre": "Animation",
                                "sortBy": "voteAverage"}).encode("utf-8"))
    check("影片筛选（类型=Animation）", "POST", "/api/movie/page", r,
          ok_extra=lambda b: 0 < (b.get("response", {}).get("total") or 0) < 10000,
          evidence=lambda b: "命中 %s 部（列表显示主类型 mainGenre），如 %s"
                             % (b["response"]["total"],
                                [m["title"] for m in b["response"]["list"]][:3][::-1]))

    r = s.get(BASE + "/api/movie/detail/862")
    check("影片详情（Toy Story）", "GET", "/api/movie/detail/862", r,
          ok_extra=lambda b: b.get("response", {}).get("title") == "Toy Story",
          evidence=lambda b: "%s (%s) 类型=%s 导演=%s 主演=%s 公司=%s 关键词=%s"
                             % (b["response"]["title"], b["response"].get("year"),
                                b["response"].get("genres"), b["response"].get("director"),
                                len(b["response"].get("cast") or []),
                                len(b["response"].get("companies") or []),
                                len(b["response"].get("keywords") or [])))

    # ---------- 3. 票房预测：单片 / 算法对比 / 日志 ----------
    payload = {"model": "best", "budget": 30000000, "popularity": 45.0, "runtime": 100,
               "language": "en", "status": "Released", "genres": "Animation|Comedy",
               "releaseMonth": 6, "year": 2010, "voteAverage": 6.8, "voteCount": 1200}
    r = s.post(BASE + "/api/predict", data=json.dumps(payload).encode("utf-8"))
    check("单片预测（全字段）", "POST", "/api/predict", r,
          ok_extra=lambda b: (b.get("response", {}).get("prediction") or 0) > 0,
          evidence=lambda b: "模型=%s 预测=%s 区间=%s 插补=%s"
                             % (b["response"].get("model"),
                                b["response"].get("prediction"),
                                b["response"].get("range"),
                                b["response"].get("imputedFields")))

    payload2 = {"budget": 237000000, "runtime": 162}  # 故意缺字段，验证中位数插补
    r = s.post(BASE + "/api/predict", data=json.dumps(payload2).encode("utf-8"))
    check("单片预测（缺字段插补）", "POST", "/api/predict", r,
          ok_extra=lambda b: bool(b.get("response", {}).get("imputedFields")),
          evidence=lambda b: "预测=%s 插补字段=%s"
                             % (b["response"].get("prediction"),
                                b["response"].get("imputedFields")))

    def _best_row(b):
        key = b["response"]["best"].split()[0]
        for row in b["response"]["algorithms"]:
            if row["name"].startswith(key):
                return row
        return b["response"]["algorithms"][0]

    t0 = time.time()
    r = s.get(BASE + "/api/predict/algo-compare")
    dt = time.time() - t0
    check("8 算法对比", "GET", "/api/predict/algo-compare", r,
          ok_extra=lambda b: len(b.get("response", {}).get("algorithms", [])) == 8,
          evidence=lambda b: "最优=%s RMSE=%.4f R2=%.4f 训练/验证=%s/%s 特征=%s 耗时=%.2fs"
                             % (b["response"]["best"], _best_row(b)["rmse"], _best_row(b)["r2"],
                                b["response"]["ntrain"], b["response"]["nval"],
                                b["response"]["nfeatures"], dt))

    r = s.post(BASE + "/api/predict/logs",
               data=json.dumps({"pageIndex": 1, "pageSize": 5}).encode("utf-8"))
    check("预测日志分页", "POST", "/api/predict/logs", r,
          ok_extra=lambda b: len(b.get("response", {}).get("list", [])) > 0,
          evidence=lambda b: "日志总数=%s 最新=%s %s(%s)"
                             % (b["response"]["total"],
                                b["response"]["list"][0].get("createdAt"),
                                b["response"]["list"][0].get("movieTitle"),
                                b["response"]["list"][0].get("modelName")))

    # ---------- 4. 智能推荐：相似影片 / 类型热门 ----------
    r = s.post(BASE + "/api/recommend",
               data=json.dumps({"strategy": "similar", "movieId": 862, "topN": 5}).encode("utf-8"))
    check("相似影片推荐（种子=Toy Story）", "POST", "/api/recommend", r,
          ok_extra=lambda b: len(b.get("response", {}).get("items", [])) == 5,
          evidence=lambda b: "种子=%s Top1=%s 相似度=%.2f%% 耗时=%.2fs 理由=%s"
                             % (b["response"]["seed"]["title"],
                                b["response"]["items"][0]["title"],
                                (b["response"]["items"][0]["score"] or 0) * 100,
                                b["response"]["seconds"],
                                "；".join(b["response"]["items"][0]["reasons"][:2])))

    r = s.post(BASE + "/api/recommend",
               data=json.dumps({"strategy": "genre_hot", "genre": "Animation", "topN": 5}).encode("utf-8"))
    check("类型热门推荐（Animation）", "POST", "/api/recommend", r,
          ok_extra=lambda b: len(b.get("response", {}).get("items", [])) == 5,
          evidence=lambda b: "Top3=%s 耗时=%.2fs"
                             % ([m["title"] for m in b["response"]["items"][:3]],
                                b["response"]["seconds"]))

    r = s.post(BASE + "/api/recommend",
               data=json.dumps({"strategy": "similar", "movieId": 862, "topN": 5,
                                "userId": 1}).encode("utf-8"))
    check("相似推荐（叠加站内评分）", "POST", "/api/recommend", r,
          ok_extra=lambda b: len(b.get("response", {}).get("items", [])) == 5,
          evidence=lambda b: "Top1=%s 理由=%s"
                             % (b["response"]["items"][0]["title"],
                                (b["response"]["items"][0].get("reasons") or [""])[0]))

    # ---------- 5. 批量预测（算法批处理 + 落库）----------
    t0 = time.time()
    r = s.post(BASE + "/api/predict/batch", data=json.dumps({"limit": 20}).encode("utf-8"))
    dt = time.time() - t0
    check("批量预测（20 部测试集影片）", "POST", "/api/predict/batch", r,
          ok_extra=lambda b: (b.get("response", {}).get("total") or 0) == 20
                             and (b.get("response", {}).get("logRows") or 0) == 20,
          evidence=lambda b: "预测=%s 条，落库=%s 条，用时 %ss（含起进程）；预测均值=%s 美元，区间 %s~%s"
                             % (b["response"]["total"], b["response"]["logRows"],
                                b["response"]["seconds"], b["response"]["avgRevenue"],
                                b["response"]["minRevenue"], b["response"]["maxRevenue"]))

    # ---------- 6. 旧框架功能回归（视频/商城/EDA 图/管理端页面）----------
    r = s.post(BASE + "/api/admin/video/page/list",
               data=json.dumps({"pageIndex": 1, "pageSize": 3}).encode("utf-8"))
    check("视频管理回归", "POST", "/api/admin/video/page/list", r,
          evidence=lambda b: "视频总数=%s" % (b.get("response", {}).get("total")))

    eda_imgs = ["fig01_revenue_distribution.png", "fig07_genre_revenue_box.png",
                "corre.png"]
    ok_imgs, sizes = 0, []
    for name in eda_imgs:
        rr = s.get("%s/eda/%s" % (BASE, name))
        ctype = rr.headers.get("Content-Type", "")
        if rr.status_code == 200 and "image" in ctype and len(rr.content) > 1000:
            ok_imgs += 1
            sizes.append("%s %.0fKB" % (name, len(rr.content) / 1024.0))
    fake = requests.Response()
    fake.status_code = 200
    fake._content = json.dumps({"code": 1 if ok_imgs == len(eda_imgs) else 0}).encode()
    check("EDA 图静态映射（21 张中抽测 %d 张）" % len(eda_imgs), "GET", "/eda/*.png", fake,
          evidence="; ".join(sizes))

    r = s.get(BASE + "/algo-figures/algo_comparison.png")
    check("算法对比图", "GET", "/algo-figures/algo_comparison.png", r, expect_code=None,
          evidence=lambda b: "HTTP %s Content-Type=%s %.0fKB"
                             % (r.status_code, r.headers.get("Content-Type"),
                                len(r.content) / 1024.0))

    r = s.get(BASE + "/admin")
    check("管理端页面", "GET", "/admin", r, expect_code=None,
          evidence=lambda b: "HTTP %s" % r.status_code)

    # ---------- 汇总 ----------
    ok = sum(1 for x in results if x["pass"])
    print("\n" + "=" * 78)
    print("验收结果：%d/%d 通过" % (ok, len(results)))
    print("=" * 78)
    print("| # | 验收项 | 调用 | HTTP | code | 结果 | 关键证据 |")
    print("|---|--------|------|------|------|------|----------|")
    for i, x in enumerate(results, 1):
        print("| %d | %s | `%s` | %s | %s | %s | %s |"
              % (i, x["name"], x["call"], x["http"], x["code"],
                 "✅" if x["pass"] else "❌", x["evidence"]))

    with open("tools/verify_all_result.json", "w", encoding="utf-8") as f:
        json.dump({"passed": ok, "total": len(results), "items": results},
                  f, ensure_ascii=False, indent=2)
    print("\n明细已写入 tools/verify_all_result.json")
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
