# movie-system 小程序端（会员 / 优惠券 / 订单）

> 注：仓库里的后端域名、服务器 IP、小程序 AppID 均为**占位符**，运行前请改成你自己的（见 `app.js` 的 `API_BASES` 与 `project.config.json` 的 `appid`）。

原生微信小程序（WXML + WXSS + JS），复用 movie-system 已有的 Spring Boot 后端。
**不新建商品表**：影片本身就是商品，会员套餐写在代码常量里。

## 这个闭环做了什么

```
登录(wx.login → openid → 免注册建号)
   ↓
领券(新人券/满20减5/满30减10)          ← 每人每张限领 1 次
   ↓
选影片 → 确认订单(算价：原价 → 会员 8 折 → 券抵扣 → 实付)
   ↓
下单(订单落库 + 券核销挂到订单上)
   ↓
我的：订单列表 / 我的券 / 会员卡
   ↓
取消订单 → 券退回未使用
```

价格规则（后端 `OrderServiceImpl` 里，前端不自己算钱）：

| 项目 | 规则 |
| --- | --- |
| 影片单价 | 评分 ≥8.5 → 12 元；≥7.5 → 9 元；其余 6 元 |
| 会员折扣 | 有效会员买影片 **8 折**（买会员套餐本身不再打折，否则套娃） |
| 优惠券 | 满减券，在会员价基础上再抵扣，实付不会小于 0 |
| 券门槛 | 未达门槛会被后端拒绝：「订单金额没到门槛，这张券要满 X 元才能用」 |

## 怎么跑起来

1. **先启动后端**（8000 端口）：

   ```
   D:\movie-system\restart_backend.cmd
   ```

2. **建表**（只需执行一次）：

   ```
   mysql -uroot vidio_mangage_db < D:\movie-system\sql\wx_shop.sql
   ```

   它会建 5 张表（t_coupon / t_user_coupon / t_member / t_order / t_order_item）、
   塞 3 张种子券，并把 `t_user.wx_open_id` 从 `varchar(0)` 修成 `varchar(64)`
   （原来是零长度，存不下 openid，微信登录根本用不了）。

3. **导入项目**：微信开发者工具 → 导入项目 → 选 `D:\movie-system\miniprogram`，
   AppID 填你自己的，或者直接选「测试号」。

4. **勾上「不校验合法域名」**：详情 → 本地设置 →
   ✅ 不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书。
   不勾会连不上 `http://127.0.0.1:8000`（后端是明文 HTTP，没有域名和证书）。

5. 编译后应该能看到首页：会员状态条 + 领券中心 + 热门影片列表。

> **真机预览**要把 `app.js` 里的 `API_BASE` 改成电脑的局域网 IP
> （`ipconfig` 看 WLAN 的 IPv4），手机和电脑要在同一个 WiFi 下。

## 接口清单

后端全部是 `POST + JSON`，返回 `{code, message, response}`，**`code === 1` 才是成功**。

| 用途 | 接口 |
| --- | --- |
| 登录（换 openid + 免注册建号） | `POST /api/wx/login`　`{code, nickName}` |
| 会员信息 / 套餐 | `POST /api/wx/member/info`、`POST /api/wx/member/plans` |
| 开通 / 续费 | `POST /api/wx/member/open`　`{months, userCouponId?}` |
| 可领券 / 领券 / 我的券 | `POST /api/wx/coupon/list`、`/coupon/receive`、`/coupon/mine` |
| 确认订单算价 | `POST /api/wx/order/preview`　`{videoId}` 或 `{months}` |
| 下单 / 订单列表 / 详情 / 取消 | `POST /api/wx/order/create`、`/order/list`、`/order/detail`、`/order/cancel` |
| 影片列表 / 详情（复用后台接口） | `POST /api/admin/video/page/list`、`/api/admin/video/getVideoDetailByVideoId/{id}` |
| 海报 | `GET /posters/{videoId}.jpg` |

## 验证后端（不用打开开发者工具）

`tools/` 下有两个 Python 脚本，直接打真实接口：

```bash
python tools/wx_check.py check001      # 全链路：登录→领券→算价→下单→用券→开会员→取消退券
python tools/wx_contract.py            # 前后端字段契约：页面读的每个字段是否真的存在
```

两个脚本都用新 code 登录（会创建一个测试账号），可以反复跑。

## 上线前必须解决的事（现在都是演示态）

1. **登录身份是假的**：演示版把 `userId` 放在请求体里传，后端也放行了整组
   `/api/wx/**`（见 `application.yml` 的 `wx.security-ignore-urls`）。
   正式做法：`/api/wx/login` 拿到 openid 后发一个 token，其余接口校验 token，
   服务端从 token 解析用户——**不能信客户端传来的 userId**。
   代码里对应位置都写了注释。
2. **没有真支付**：下单直接置为「已支付」。要接微信支付得改成
   下单落待支付 → 统一下单拿 prepay_id → 支付回调验签 → 再置已支付。
   另外微信支付**必须是企业主体**，个人小程序开不了。
3. **域名**：小程序上线后不允许请求 IP/HTTP，必须有 ICP 备案的 HTTPS 域名并在
   后台配 request 合法域名。图片同理，海报不能直接对内网 IP 取。
4. **类目与内容**：影视内容属于敏感类目，有用户生成内容还要接内容安全检测。
5. **配置里的微信凭据要换**：`application.yml` 里的 `wx.appid` / `wx.secret`
   是模板里带过来的明文凭据，**不是你自己的**，上线前务必换掉并从仓库里清掉。
