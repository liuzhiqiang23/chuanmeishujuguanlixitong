# 关键发现与证据（D:\movie-system / 微信小程序「阿强观影」）

> 本文件记录**核查得到的事实与原文引用**（含后台页面文字、官方文档/媒体报道结论）。
> 外部来源内容一律只写在这里，不写进 `task_plan.md`。
> 记录时间：2026-09-23（除标注外均为当天在微信后台实测所见）

## 1. 小程序账号事实（微信后台实测）

| 项目 | 值 | 来源 |
|---|---|---|
| 小程序名称 / 简介 | 阿强观影 / 分享电影资料 | 设置 → 基本设置 |
| **appid** | `wx0ce243dae842cc7e` | 项目配置 + 后台 |
| **主体信息** | **个人**（姓名显示为「柳**」） | 设置 → 基本设置 |
| **服务类目** | **工具 > 信息查询**（仅 1 个类目） | 设置 → 基本设置 |
| 微信认证 | **未认证**（认证主体类型：未认证） | 设置 → 基本设置、管理 → 微信认证 |
| 小程序备案 | **管局审核中**（短信核验已完成） | 首页「小程序开发与发布流程」 |
| 线上版本 | 尚未提交线上版本 | 管理 → 版本管理 |
| 审核版本 | 1.0.4 → **审核不通过**（2026-09-22 14:31:58 提交） | 管理 → 版本管理 |
| 开发版本 | **20260923**（2026-09-23 20:27:38 提交，已挂「体验版」标签） | 管理 → 版本管理 |
| 开发者 | SICKLE | 版本管理 |

## 2. 虚拟支付开通条件页（后台原文逐字）

进「支付与交易 → 虚拟支付」，页面正文（从 DOM 读取，非读图）：

```
虚拟支付
前往认证
开通条件
· 主体类型为已认证的小程序（当前状态： 未认证 ）        ← 红字，未满足
· 小程序类型符合要求（当前状态： 企业 事业单位 ）        ← 黑字
· 小程序主体信息完备（当前状态： 缺陷 ）                ← 红字，未满足
功能介绍
· 开通此功能后，开发者可在小程序内提供虚拟物品购买的服务
· 支持线上结算、分账、提现
· 平台将收取技术服务费用
```

**关键对照证据（同类页面在别人账号上的显示）：**

| 账号形态 | 该行显示 | 来源 |
|---|---|---|
| 企业账号 | 小程序类型符合要求（**企业事业单位**），另两项「已认证/完备」 | 第三方部署文档站转贴的后台截图 |
| 个人认证账号 | 小程序类型符合要求（**个人**），另两项「已认证/完备」 | 2026-09-02 帖子《好消息，个人认证小程序可以接入支付功能了》 |

→ 推断：该行是按账号类型渲染的**当前值**，不是「只允许企业」的硬要求。
→ **未解矛盾**：本账号主体是「个人」，这页却显示「企业事业单位」；页面自己又承认「主体信息完备（缺陷）」。可能原因：①主体信息未补齐导致类型字段取不到真实值；②该模块只对企业/个体户开放，个人通道另有入口。**认证完成后必须复验**。

## 3. 1.0.4 版本审核驳回原文（后台「查看详情」页逐字）

```
版本审核修改指引
失败原因1
审核失败原因：存在平台未允许的服务内容，违反《微信小程序平台运营规范常见拒绝情形3.2》
详情描述：你好，你的小程序服务涉及提现、支付等交易行为，个人主体尚未开放支付能力，建议申请企业主体小程序。
截图：（两张小程序页面缩略图）
修改指引：提现交易服务修改指引说明
```

**已核实**：小程序端（`miniprogram/`）与后端 Java（`backend/src/main/java/`）全仓搜索 `提现/余额/钱包/withdraw/balance` → **0 命中**，即产品里没有提现功能；「提现」属平台模板措辞，真正触发点是「个人主体卖虚拟商品」（会员卡、观影券）。

## 4. 个人虚拟支付的公开条件（媒体/文档转述，来源不完全一致）

- 主体：**个人主体**，开发者持有效居民身份证
- 类目：**服务类目必须包含「工具」**（本账号满足：工具 > 信息查询）
- 前提：**已完成小程序认证 + 备案**
- 额度：**月收款限额 10 万元**
- 认证费用：个人认证约 **30 元/年**
- 费率：Android 等终端约 **1%**（另有来源写 0.6%），**iOS 约 12%**（含苹果佣金）；结算 T+3 —— **数字各来源有出入，开通时以后台说明为准**
- 模式：仅支持**道具直购**（会员/数字权益），不引入代币充值
- 官方文档入口标题为《虚拟支付：企业、个体户》；个人版条件见上述转述，**未能在官方文档页正文中直接读到**（微信文档站前端渲染，抓取只得到导航）

## 5. 虚拟支付技术要点（用于后续接入，均以开通后官方接入指引为准）

- 前端 API：`wx.requestVirtualPayment`，需基础库 **2.19.2+**
- 参数：`mode`（支付类型）、`env`（0 正式 / 1 沙箱）、**`signData`（字符串，必须原样透传，前端不得再 `JSON.stringify`）**、`paySig`（支付签名）、`signature`（用户态签名）
- 道具直购的 `signData` 字段：`offerId / buyQuantity / env / currencyType:"CNY" / productId`；**不能带 `platform` 字段**；JSON key 顺序固定
- 服务端：用虚拟支付密钥算两个签名；调 `api.weixin.qq.com/xpay/*`（如 `/xpay/query_order`、`/xpay/query_user_balance`、`/xpay/currency_pay`）
- 回调：`xpay_goods_deliver_notify`（道具发货）、`xpay_coin_pay_notify`（代币扣减）
- 坑：paySig 拼串缺 `&` 分隔符；offerId 类型；signData key 顺序；**沙箱环境不发回调**；道具创建后有同步延迟；错误码如 `-15005`
- 与传统 JSAPI 支付完全独立：不同商户号、不同签名算法、不同回调

## 6. 虚拟支付接入改造清单（本项目落地路径）

**数据库（`movie_analytics_db`）**
- `t_order` 现有：`order_no / user_id / order_type(1影片观影券 2会员套餐) / title / total_amount / discount_amount / pay_amount / user_coupon_id / status(0待支付 1已支付 2已取消) / create_time / pay_time`
- 需补列：`pay_channel`、`offer_id`、`product_id`、`wx_order_id`、`notify_time`、`refund_status`、`refund_time`
- 新增 `t_pay_notify_log`（回调原文 + 验签结果 + 处理结果），回调可能重发，必须幂等

**后端（Spring Boot，包 `com.alvis.media`）**
| 位置 | 现状 | 改成 |
|---|---|---|
| `service/impl/OrderServiceImpl.doCreate()` | 已有注释「演示版：落库即视为支付成功。接微信支付时这里要改成 STATUS_UNPAID」→ 现为 `setStatus(STATUS_PAID)` | 落 `STATUS_UNPAID`，`pay_time` 留空 |
| `service/impl/OrderServiceImpl.createMemberOrder()` | 已有注释「正式接支付时，开卡要挪到支付成功回调里」→ 现直接调 `memberService.openOrRenew()` | 删除该调用，抽成 `MemberService.grant(orderNo)` 供回调复用 |
| `POST /api/wx/member/open` | 前端点一下直接给权益 | 废弃或改内部调用 |
| `POST /api/wx/order/cancel` | — | 仅允许取消未支付订单 |
- 新增 `controller/wx/WxPayController`（`/api/wx/pay`）：`/prepare`（组装 signData + 算 paySig/signature）、`/notify`（验签 + 幂等 + 置已支付 + 发货）、`/query`（轮询/查单）
- 新增 `VirtualPaySignService`（签名封装）
- 配置：`system.virtualpay.offerId / appKey / env`，值走 `local_env.cmd` + `application-dev.yml`，**密钥不入库**

**小程序端**
| 文件 | 改动 |
|---|---|
| `miniprogram/pages/member/member.js` | `open()` 改为四步：`/api/wx/order/create` → `/api/wx/pay/prepare` → `wx.requestVirtualPayment` → 轮询 `/api/wx/pay/query` 到 `status=1` |
| `miniprogram/pages/confirm/confirm.js` | 提交订单同样走虚拟支付 |
| `miniprogram/pages/detail/detail.js` | 购买入口统一跳 confirm 页下单 |
| `miniprogram/pages/member/member.wxml:51` | **删**「演示版下单即支付成功，会员立即生效」 |
| `miniprogram/pages/confirm/confirm.wxml:64` | **删**「演示版下单即视为支付成功（不接微信支付）…」 |

**其它接口（现有，改造时注意回归）**：`/api/wx/member/plans|info`、`/api/wx/coupon/list|receive|mine|share/*`、`/api/wx/order/preview|create|list|detail|cancel`

## 7. 项目运行与环境事实（供后续会话直接用）

- 技术栈：Spring Boot 3.5（Undertow，**端口 8000**，包 `com.alvis.media`）+ Vue3/Vite 管理后台 + MySQL 8（库 **`movie_analytics_db`**，15 新项目表 + 19 框架表）+ Memurai/Redis 6379 + Python **3.13**（`.venv`）
- 管理端登录：`柳志强 / 200306`；演示账号 `student / 123456`
- 一键启动：双击 `start_all.cmd`（环境自检 → 重启后端 → 开浏览器）；只重启后端用 `restart_backend.cmd`
- MySQL 客户端：`D:\ruanjian\MySQL\bin\mysql.exe`，口令 `123456`
- 微信开发者工具 CLI：`D:\微信开发者工具\cli.bat`（`islogin` / `upload --project D:\movie-system\miniprogram -v <版本> -d "<备注>"`）
- 算法：`algorithm/boxoffice_prediction/train_all.py`（8 算法，最佳 RandomForest RMSE 0.875 / R² 0.591）、`predict_api.py`、`algorithm/movie_recommendation/recommend_api.py`
- 验收脚本：`tools/verify_all.py`（17 项接口验收）、`tools/verify_inference_consistency.py`（样本内 RMSE 0.3436 / 相关系数 0.9732）

## 8. 环境坑（已踩过，勿重复）

| 现象 | 原因/解法 |
|---|---|
| `git push github` → `Connection reset ... port 22` | 该网络重置 22 端口；remote 已改为 `ssh://git@ssh.github.com:443/liuzhiqiang23/chuanmeishujuguanlixitong.git`（正确仓库名是 `liuzhiqiang23`，**无连字符**） |
| TMDB 海报全显示「无海报」 | `image.tmdb.org` 被重置（主站可达）；环境问题，非代码缺陷 |
| `*.cmd` 报「'-' 不是内部或外部命令」 | 批处理必须**纯 ASCII + CRLF**，不要 `chcp 65001` |
| 脚本等待逻辑失效 | `timeout /t` 在 stdin 被重定向时不等待，用 `ping -n` |
| 后台点击菜单项超时 | 折叠菜单遮挡；用快照里已验证的 href 直接导航，或读 iframe `contentDocument` |

## 9. 安全/仓库约束（务必遵守）

- `local_env.cmd`（DB 口令 + RSA 密钥对）**永不入库、永不外发**；`data/tmdb_key.txt`、`data/new_source/`、`cloudflared.exe`、模型二进制、推荐缓存均已在 `.gitignore`
- `.claude/`、`.vscode/` 是本地 AI/编辑器配置，**不要删除**
- 涉及微信账号的操作（认证、扫码验证、开通虚拟支付、提交审核）**只查看不代操作**，一律由用户本人执行
