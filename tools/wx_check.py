"""movie-system 小程序商城接口的全链路验证：登录→领券→算价→下单→用券→开会员→取消退券。

用 urllib 而不是 curl：Git Bash 里 curl 发中文会按 GBK 编码，后端报
"Invalid UTF-8 start byte"，那是测试工具的问题，不是接口的问题。
"""
import json
import sys
import urllib.request

API = "http://127.0.0.1:8000/api/wx"
FAIL = []


def call(path, body=None, label=""):
    data = json.dumps(body or {}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(API + path, data=data,
                                headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        out = json.loads(resp.read().decode("utf-8"))
    r = out.get("response")
    brief = json.dumps(r, ensure_ascii=False)
    print("== %-28s code=%s  %s" % (label or path, out.get("code"), out.get("message")))
    print("   %s" % (brief[:460] if len(brief) > 460 else brief))
    return out


def expect(cond, what):
    print("   [%s] %s" % ("OK " if cond else "FAIL", what))
    if not cond:
        FAIL.append(what)


# 1. 登录（首次会用 openid 免注册建号）
login = call("/login", {"code": sys.argv[1] if len(sys.argv) > 1 else "check001", "nickName": "微信测试用户"}, "1 登录")
uid = login["response"]["userId"]
expect(login.get("code") == 1 and uid, "登录拿到 userId=%s" % uid)

# 2. 可领券
lst = call("/coupon/list", {"userId": uid}, "2 可领券列表")
coupons = lst["response"]
expect(len(coupons) == 3, "有 3 张可领券")
free_id = [c for c in coupons if float(c["threshold"]) == 0][0]["id"]

# 3. 领券
rec = call("/coupon/receive", {"userId": uid, "couponId": free_id}, "3 领无门槛券")
expect(rec.get("code") == 1, "领券成功")
uc_id = rec["response"]["id"]

# 3b. 重复领应该被拦住
dup = call("/coupon/receive", {"userId": uid, "couponId": free_id}, "3b 重复领同一张")
expect(dup.get("code") != 1, "重复领被拒绝：%s" % dup.get("message"))

# 4. 我的券
mine = call("/coupon/mine", {"userId": uid}, "4 我的券")
expect(len(mine["response"]) == 1, "我的券里有 1 张")

# 5. 确认订单（星际穿越 157336，评分 8.487 → 12 元档）
VID = 157336
prev = call("/order/preview", {"userId": uid, "videoId": VID}, "5 确认订单预览(非会员)")
p = prev["response"]
expect(float(p["originalPrice"]) == 9.00, "原价 9.00（评分 8.487 落在 >=7.5 档）")
expect(p["member"] is False, "还不是会员")
expect(len(p["usableCoupons"]) == 1, "这张单能用 1 张券（无门槛券）")

# 6. 下单用券
order = call("/order/create", {"userId": uid, "videoId": VID, "userCouponId": uc_id}, "6 下单(用无门槛券)")
o = order["response"]
expect(order.get("code") == 1, "下单成功 orderNo=%s" % o.get("orderNo"))
expect(float(o["discountAmount"]) == 3.00, "优惠 3.00（券）")
expect(float(o["payAmount"]) == 6.00, "实付 6.00（9-3）")
order_no = o["orderNo"]

# 7. 券已核销
mine2 = call("/coupon/mine", {"userId": uid, "status": 1}, "7 已使用的券")
expect(len(mine2["response"]) == 1 and mine2["response"][0]["orderNo"] == order_no,
       "券状态变成已使用并挂在订单 %s 上" % order_no)

# 8. 订单列表
olist = call("/order/list", {"userId": uid, "pageIndex": 1, "pageSize": 5}, "8 我的订单")
expect(olist["response"]["total"] == 1, "订单总数 1")

# 9. 开通会员（月卡 15 元）
mem = call("/member/open", {"userId": uid, "months": 1}, "9 开通月卡")
expect(mem.get("code") == 1, "开卡成功，到期 %s" % mem["response"]["expireTime"])
expect(float(mem["response"]["payAmount"]) == 15.00, "实付 15.00")

# 10. 会员信息
info = call("/member/info", {"userId": uid}, "10 会员信息")
expect(info["response"]["isMember"] is True, "已是会员")
expect(float(info["response"]["discountRate"]) == 0.8, "折扣率 0.8")

# 11. 会员价预览：12 * 0.8 = 9.6
prev2 = call("/order/preview", {"userId": uid, "videoId": VID}, "11 预览(会员价)")
p2 = prev2["response"]
expect(float(p2["priceAfterMember"]) == 7.20, "会员价 7.20（9 的 8 折）")
expect(float(p2["memberDiscount"]) == 1.80, "会员省 1.80")

# 12. 门槛校验：先用 9.60 元的单去用「满20减5」应该被拒
rec5 = call("/coupon/receive", {"userId": uid,
                                "couponId": [c for c in coupons if float(c["threshold"]) == 20][0]["id"]},
            "12 领满20减5券")
uc5 = rec5["response"]["id"]
bad = call("/order/create", {"userId": uid, "videoId": VID, "userCouponId": uc5}, "12b 用未达门槛的券")
expect(bad.get("code") != 1, "门槛校验生效：%s" % bad.get("message"))

# 13. 取消订单应该把券退回来
cancel = call("/order/cancel", {"userId": uid, "orderNo": order_no}, "13 取消影片订单")
expect(cancel.get("code") == 1, "取消成功")
back = call("/coupon/mine", {"userId": uid, "status": 0}, "13b 券退回来了吗")
titles = [c["title"] for c in back["response"]]
expect(any("新人" in t for t in titles), "无门槛券已退回未使用：%s" % titles)

# 14. 会员订单不允许取消
mno = mem["response"]["orderNo"]
mc = call("/order/cancel", {"userId": uid, "orderNo": mno}, "14 取消会员订单")
expect(mc.get("code") != 1, "会员订单被拒绝取消：%s" % mc.get("message"))

print()
print("================ 总结 ================")
if FAIL:
    print("有 %d 项没通过：" % len(FAIL))
    for f in FAIL:
        print("  - " + f)
    sys.exit(1)
print("全部通过 ✅   测试账号 userId=%s" % uid)
