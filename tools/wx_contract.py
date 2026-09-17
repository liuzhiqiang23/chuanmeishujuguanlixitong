"""前后端字段契约校验。

小程序页面里写的字段名（{{item.videoName}} 之类）如果和接口返回对不上，
在开发者工具里才会白屏/显示 undefined，很费时间。这里把每个页面实际
读取的字段路径，逐个对到真实接口返回上，提前发现拼写/结构不一致。
"""
import json
import sys
import urllib.request

BASE = "http://127.0.0.1:8000"
FAIL = []


def call(path, body=None):
    data = json.dumps(body or {}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=data,
                                headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def need(obj, path, label):
    cur = obj
    for part in path.split("."):
        if isinstance(cur, list):
            if not cur:
                print("   [SKIP] %s（列表为空，测不到）" % label)
                return None
            cur = cur[0]
        if not isinstance(cur, dict) or part not in cur:
            print("   [FAIL] %s —— 缺字段 %s" % (label, path))
            FAIL.append("%s 缺 %s" % (label, path))
            return None
        cur = cur[part]
    print("   [OK ] %s  (%s = %s)" % (label, path, json.dumps(cur, ensure_ascii=False)[:60]))
    return cur


# 登录拿一个测试账号
login = call("/api/wx/login", {"code": "contract01", "nickName": "契约校验"})["response"]
uid = login["userId"]
print("== 登录 ==")
need(login, "userId", "app.js 登录")
need(login, "token", "app.js 登录")
need(login, "isMember", "app.js 登录")

print("== 首页 index ==")
vids = call("/api/admin/video/page/list", {"pageIndex": 1, "pageSize": 10})["response"]
need(vids, "total", "index 影片列表")
need(vids, "pageNum", "index 影片列表")
need(vids, "pages", "index 影片列表")
need(vids, "hasNextPage", "index 影片列表")
need(vids, "list.videoId", "index 影片列表")
need(vids, "list.videoName", "index 影片列表")
need(vids, "list.voteAverage", "index 影片列表")
need(vids, "list.popularity", "index 影片列表")

mem = call("/api/wx/member/info", {"userId": uid})["response"]
need(mem, "isMember", "index/member 会员信息")
need(mem, "expireTime", "index/member 会员信息")
need(mem, "discountRate", "index/member 会员信息")
need(mem, "plans", "member 套餐列表")
need(mem, "plans.months", "member 套餐列表")
need(mem, "plans.name", "member 套餐列表")
need(mem, "plans.price", "member 套餐列表")
need(mem, "plans.desc", "member 套餐列表")

coupons = call("/api/wx/coupon/list", {"userId": uid})["response"]
need(coupons, "id", "index 可领券")
need(coupons, "title", "index 可领券")
need(coupons, "amount", "index 可领券")
need(coupons, "threshold", "index 可领券")
need(coupons, "validDays", "index 可领券")

print("== 详情页 detail ==")
det = call("/api/admin/video/getVideoDetailByVideoId/157336")["response"]
need(det, "videoName", "detail 影片详情")
need(det, "originalTitle", "detail 影片详情")
need(det, "voteAverage", "detail 影片详情")
need(det, "popularity", "detail 影片详情")
need(det, "releaseDate", "detail 影片详情")
need(det, "overview", "detail 影片详情")

# 先领一张券，好让 preview 里有可用券
free = [c for c in coupons if float(c["threshold"]) == 0][0]
rec = call("/api/wx/coupon/receive", {"userId": uid, "couponId": free["id"]})["response"]
prev = call("/api/wx/order/preview", {"userId": uid, "videoId": 157336})["response"]
need(prev, "itemType", "confirm/detail 预览")
need(prev, "itemName", "confirm/detail 预览")
need(prev, "originalPrice", "confirm/detail 预览")
need(prev, "member", "confirm/detail 预览")
need(prev, "memberDiscount", "confirm/detail 预览")
need(prev, "priceAfterMember", "confirm/detail 预览")
need(prev, "bestCouponDiscount", "confirm/detail 预览")
need(prev, "usableCoupons", "confirm/detail 预览")
need(prev, "usableCoupons.id", "confirm 可用券")
need(prev, "usableCoupons.title", "confirm 可用券")
need(prev, "usableCoupons.amount", "confirm 可用券")
need(prev, "usableCoupons.threshold", "confirm 可用券")
need(prev, "usableCoupons.expireTime", "confirm 可用券")

print("== 下单 + 我的页 mine ==")
order = call("/api/wx/order/create", {"userId": uid, "videoId": 157336,
                                      "userCouponId": rec["id"]})["response"]
need(order, "orderNo", "confirm 下单")
need(order, "payAmount", "confirm 下单")
need(order, "discountAmount", "confirm 下单")

olist = call("/api/wx/order/list", {"userId": uid, "pageIndex": 1, "pageSize": 20})["response"]
need(olist, "total", "mine 订单列表")
need(olist, "list.orderNo", "mine 订单列表")
need(olist, "list.status", "mine 订单列表")
need(olist, "list.orderType", "mine 订单列表")
need(olist, "list.title", "mine 订单列表")
need(olist, "list.createTime", "mine 订单列表")
need(olist, "list.payAmount", "mine 订单列表")
need(olist, "list.discountAmount", "mine 订单列表")

mine = call("/api/wx/coupon/mine", {"userId": uid})["response"]
need(mine, "id", "mine 我的券")
need(mine, "title", "mine 我的券")
need(mine, "status", "mine 我的券")
need(mine, "expireTime", "mine 我的券")
need(mine, "threshold", "mine 我的券")
need(mine, "amount", "mine 我的券")

print()
if FAIL:
    print("契约不一致 %d 处：" % len(FAIL))
    for f in FAIL:
        print("  - " + f)
    sys.exit(1)
print("前后端字段契约全部对得上 ✅")
