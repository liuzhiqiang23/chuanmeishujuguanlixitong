# 进度日志（会话记录）

> 给后续对话：本文件是**按时间顺序的会话日志**；要看「现在该做什么」读 `task_plan.md`，要看「事实与证据」读 `findings.md`。

## 会话：2026-09-23（八步作业收尾 → 小程序改版 → 支付合规调研）

### 阶段 1：第七步 联调与调试 —— complete
- 动作：写 `tools/verify_all.py`（17 项接口验收）与 `tools/verify_inference_consistency.py`（训练/推理一致性）；浏览器走查 4 个新增页面；产出 `docs/06_系统联调与测试记录.md` + `docs/screenshots/`
- 关键结果：**17/17 通过**；一致性 RMSE 0.3436 / R² 0.9328 / 相关系数 0.9732 / 平均偏差 −0.0138；单片预测未命中缓存 3.7s、命中 8ms；推荐 0.06s；批量 20 条 2.8s
- 提交：`690b9e4d`

### 阶段 2：第八步 一键启动 + 用户手册 —— complete
- 动作：`start_all.cmd`（环境自检→重启后端→开浏览器→打印账号）、`用户手册.md`（10 节）、刷新 `项目结构.md`/`本次改动说明.md`/`README.md`
- 修正：`restart_backend.cmd` 的等待循环 `timeout`→`ping`（`timeout` 在 stdin 被重定向时不等待，链式调用会误判失败）；README 的 Python 版本改为实测 3.13
- 实测：真机跑通——环境自检全 OK、后端 30s 起来、`/admin/index.html=200`、`/api/wx/member/plans code=1`
- 提交：`31f2c757`；推送 Gitee + GitHub（GitHub 修 remote 用户名连字符问题 + 快进 `main`）

### 阶段 3：小程序 UI 改版 —— complete
- 用户要求：「还是用之前那个小海报那版，但是界面颜色跟科幻版一样」
- 动作：`app.wxss` 海报 140×200 缩略图 + `.video-item` 回到 flex 横向行；首页/分类/搜索三页 image `mode` 回 `aspectFill`；科幻配色不动
- 追加要求：「底部的三个文字再显眼一点」→ ①列表项底部观影券/价格/删除 放大加亮（28/38/28rpx + 辉光）②tabBar 三个标签提亮（未选中 `#6B7699`→`#A8BEDC`、背景 `#0C1128`→`#131A3A`）+ 6 个霓虹线性图标（`tools/make_tabbar_icons.py` 生成，含 `member` 星形/`home` 房子/`mine` 人形，选中态带辉光）
- 核实：改动后的 wxml 与「小海报那版」逐字节一致（`git diff 119a341d^`），app.wxss 仅多三行按钮样式
- 提交：`db264244`

### 阶段 4：上线体验版 —— complete
- 用户要求：「可以，上线体验版」
- 动作：用开发者工具 CLI 上传 → 版本号 **20260923**，包体 107.5KB，appid `wx0ce243dae842cc7e`；后台已挂「体验版」标签（用户确认）
- 提交：`db264244`；推送 Gitee + GitHub（两边 master 与 GitHub main 均为 `db264244`）

### 阶段 5：支付合规调研 + 后台核查 —— complete（结论见 findings.md）
- 起因：体验版就位后，用户问个人虚拟支付文档；随后让登录后台核查
- 动作：搜索官方文档与 2026-09 媒体资料；用内置浏览器登录小程序后台（用户扫码）→ 只读核查：首页发布流程、设置→基本设置、支付与交易→虚拟支付、版本管理→1.0.4 驳回详情、微信认证页、小程序成长计划
- 关键发现：
  - 主体=**个人**（柳**）、类目=**工具 > 信息查询**、认证=**未认证**、备案=**管局审核中**
  - 1.0.4 驳回原文：违反《常见拒绝情形3.2》——「涉及提现、支付等交易行为，个人主体尚未开放支付能力，建议申请企业主体小程序」
  - 虚拟支付页三条件：未认证（红）/ 企业事业单位（黑）/ 缺陷（红）
  - 矛盾点：主体是个人，虚拟支付页却显示「企业事业单位」→ 需认证后复验（用户自己提出质疑「不是认证类型不符合吗」，我修正了此前"认证+备案就能开"的乐观推断）
  - 全仓搜索：小程序/后端**无**提现、余额、钱包功能
- 产出：虚拟支付接入改造清单（见 findings.md §6，含 `OrderServiceImpl.doCreate()` / `createMemberOrder()` 两处已有注释的改造锚点）
- 未做：没有点「开通」「提交审核」「去认证」、没有扫备案验证码，**未改任何后台设置**

### 阶段 6：备案短信核验 —— complete（用户操作）
- 用户完成工信部短信核验；后台状态仍为「管局审核中」（正常，等待管局审核 1–20 工作日）
- 后续：备案通过后状态变「已备案」，是发布线上版本的前置条件；**不解决版本审核问题**

## 会话：2026-09-24（作业合规复核 + 残留清理 + 远端归位）

### 阶段 1：对照 `项目记录.txt` 逐条复核 —— complete
- 动作：按老师给的 8 步要求逐条实测（不凭记忆），核对数据/算法/数据库/文档/提交
- 结果：**18 项里 16 项完全满足**，2 项待处理（origin 推送权限、第三步.2 人工审核留痕）
- 复核要点与实测值见下方「测试结果」；两处 ⚠️ 的处理见阶段 2、阶段 3
- 细节修正：`data/train.csv`、`test.csv` 用物理行数会数成 5007，**必须用 CSV 解析器按记录数**（文本字段含换行）→ 实为 5000 条

### 阶段 2：清理电影系统残留文件 —— complete
- 依据：用户选择执行「清理残留文件」一项（作业口径：算法/数据中只保留新项目相关文件）
- 删除 10 个文件（提交 `6d5de071`）：
  - 8 个海报/中文资料维护脚本：`backfill_chinese_names`、`backfill_chinese_overviews`、`backfill_posters`、`download_posters`、`fetch_current_posters`、`fill_posters_from_douban`、`make_placeholder_posters`、`verify_and_fill_posters`
  - `sql/vidio_mangage_db.sql`（旧库原始 DDL，旧库已删）、`sql/movie_analysis_schema.sql`（被取代的早期草稿）
- **保留并说明理由**：`data/sync_tmdb.py`（视频影片同步）、`data/git_ref_chain.py`（前端构建引用链检查）——与「海报/中文资料」无关，删了会丢工具能力
- 删除前已核查：全部文件均**已被 git 跟踪**（可从历史取回）；删除后全仓搜索无悬空引用；同步更新 `项目结构.md`
- 附带：`git add -A` 把四份记忆文件一并纳入同一提交，提交说明已补齐，避免"悄悄入库"

### 阶段 3：origin 远端归位 —— complete
- 原状：`origin` 指向 `git@gitee.com:wuying_0924/movie-system.git`（非本人仓库），`git push origin master` 报 `Permission denied (publickey)`，仍停在旧提交 `cf459af3`
- 处置：`git remote set-url origin https://gitee.com/liu-zhiqiang20030520/liuzhiqiangdegit.git` → `git push origin master` 成功
- 现状：`origin` 与 `gitee` 指向同一仓库（同一仓库两个名字，功能正常；如嫌重复可删其一）
- 同步：`github`（走 443）master + main 均已更新到 `6d5de071`

### 阶段 4：后端重启（附带）
- 复核时发现后端 8000 端口已停（curl 连接被拒）；因用户体验版依赖它，已用 `restart_backend.cmd` 后台拉起重启
- 说明：体验版对测试者可用需要本机后端在跑；本机关机/窗口关闭后需重新运行 `start_all.cmd`

### 未执行（用户本次明确不做的）
- 第三步.2「人工审核」的独立留痕文档（`docs/05` 里已有对第三步文档的逐项对照，但无单独文件）

## 提交记录（本仓库 master）
| 提交 | 内容 |
|---|---|
| `dc056f68` | 第一步.6 + 第三步.4：删除旧算法/旧数据集/旧 EDA 产物 |
| `df7c0861` | 第五步：需求规格说明书 + 系统详细设计 + 审查记录 |
| `cd90e0c3` | 第五步：Vue 前端四页面（影片库/票房预测/算法对比/智能推荐） |
| `0321f3f8` | 第六步：票房预测推理服务 + 智能推荐引擎 |
| `72ea459c` | 推理元数据 `feature_meta.json` 入库 |
| `940f0e81` | 第六步：数据集入库 + 框架表迁入 `movie_analytics_db` + 删旧库 |
| `a7665a70` | 第六步：后端接口（影片库/预测/推荐）+ 前后端打通 |
| `690b9e4d` | 第七步：联调验收 17/17 + 一致性校验 + 测试记录 |
| `31f2c757` | 第八步：一键启动脚本 + 用户手册 + 文档刷新 |
| `db264244` | 小程序：小海报布局 + tabBar 图标提亮（含体验版 20260923 上传） |
| `6d5de071` | 清理视频模块海报/中文资料脚本 + 过期 SQL；入库进度记忆文件（AGENTS/task_plan/findings/progress） |

## 仓库与远端状态（记录时）
- 本地 `master` = `6d5de071`，工作区干净
- **`origin`**（2026-09-24 重指向本人仓库）：`https://gitee.com/liu-zhiqiang20030520/liuzhiqiangdegit` → master = `6d5de071`（原指向 `wuying_0924/movie-system`，本机密钥无权限）
- Gitee（`gitee` 远端，与 origin 同一仓库）：master = `6d5de071`
- GitHub：`https://github.com/liuzhiqiang23/chuanmeishujuguanlixitong` → master = main = `6d5de071`（remote 走 443）
- 注意：`task_plan.md` / `findings.md` / `progress.md` 与 `AGENTS.md` 是本轮新增的**记忆文件**，已随提交 `6d5de071` 入库（其他机器拉代码即可看到进度）

## 测试结果（最近一次全量）
| 测试 | 输入 | 预期 | 实际 | 状态 |
|---|---|---|---|---|
| 作业合规复核（2026-09-24） | 对照 `项目记录.txt` 18 项要求逐条实测 | 全部满足 | **16 项满足**；2 项待处理（origin 推送→已解决；第三步.2 留痕→未做） | ⚠️ |
| 抽样文件记录数 | CSV 解析器计数 | 各 5000 | train 5000×25、test 5000×24 | ✅ |
| 新项目表数量 | `information_schema` | ≥8 | 34（15 新项目 + 19 框架） | ✅ |
| 旧库是否删除 | `SHOW DATABASES` | 不存在 | 不存在（备份件保留） | ✅ |
| 算法数量 | `metrics.json` | ≥6 | 8 | ✅ |
| 清理后悬空引用 | 全仓 grep 被删文件名 | 0 | 0 | ✅ |
| 接口验收 | `tools/verify_all.py` | 全通过 | 17/17 | ✅ |
| 训练/推理一致性 | 500 条训练样本回灌 | 相关系数>0.9 | 0.9732，偏差 −0.0138 | ✅ |
| 小程序上传 | `cli.bat upload -v 20260923` | 上传成功 | 107.5KB，已挂体验版 | ✅ |
| 一键启动 | `start_all.cmd` 真机 | 后端起来 + 健康检查通过 | 30s 起来，200 / code=1 | ✅ |

## 错误日志
| 时间 | 错误 | 尝试 | 解决 |
|---|---|---|---|
| 09-23 | `restart_backend.cmd` 等待循环不等待（stdin 重定向） | 1 | `timeout` → `ping -n` |
| 09-23 | GitHub push 22 端口被重置 | 1 | 改走 `ssh.github.com:443` |
| 09-23 | 后台菜单项点击超时（折叠菜单遮挡） | 1 | 用已验证 href 直接导航 |
| 09-23 | 后台正文在 iframe，快照读不到 | 1 | `evaluate` 读 iframe 文本 / 截图 |
| 09-23 | 记忆文件里 GitHub 仓库名敲错（漏 a） | 1 | 已修正为 `chuanmeishujuguanlixitong` |

## 五问重启检查
| 问题 | 答案 |
|------|------|
| 我在哪里？ | 阶段 4（微信认证未做），阶段 3（备案等管局）并行中 |
| 我要去哪里？ | 认证 → 复验虚拟支付页 → 开通/改代码，或走演示态上线 |
| 目标是什么？ | 见 `task_plan.md` 目标声明 |
| 我学到了什么？ | 见 `findings.md`（后台原文、驳回原因、改造锚点、环境坑） |
| 我做了什么？ | 见本文件上方各阶段 |

## 2026-09-29 会话：AI 客服上线
- 新增：sql/ai_chat.sql（t_chat_faq/t_chat_log）、后端 /api/wx/chat（ChatServiceImpl 三步 RAG + 兜底）、小程序 pages/chat 聊天页 + 我的页入口、GLM_API_KEY 进 local_env.cmd
- 测试：四题回归（会员价格/流浪地球/星际穿越/天气）全部符合预期；glm-4-flash 耗时 1.3~5s
- 提交：74b28185 → gitee master
- 另：ai-video-pipeline 新增 auto_edit.py（BGM 节拍+素材打分自动选段建稿，仿剪映一键成片），详见该目录 findings.md

## 2026-09-29 补：新体验版上传
- 用户反馈手机看不到 AI 客服 → 原因：手机跑的是旧体验版包（20260923），新功能只在本地代码
- 已做：app.js 探活 IP 42.214→128.214（WLAN 地址变了）；CLI 上传开发版本 **20260929**（114KB，含 chat 页），commit 9ce8cf2b 推送
- 待用户：mp 后台版本管理页（浏览器窗口已打开，显示扫码二维码）→ 微信扫码 → 对 20260929 点「选为体验版」
- 手机使用前提：与电脑同一 WiFi；电脑后端保持运行（restart_backend.cmd）

## 2026-09-29 会话二：AI 客服上云 + 客服浮窗
- **云端部署（服务器 <服务器IP>）**：服务器原本还是 9/18 旧 jar + 旧库 vidio_mangage_db，这次整体迁移：
  - 建新库 movie_analytics_db：本地导出 15 张影片数据表 + t_chat_faq/t_chat_log（gzip 4.7MB，SFTP 上传，工具 ~/.zcode/workspace/default/tools/ssh_put.py）
  - 19 张运营表从 vidio_mangage_db 原位复制（CREATE LIKE + INSERT SELECT，632 用户零丢失）→ 跑 fix_schema.sql 补列 → 应用账号 GRANT 新库权限
  - movie.env 追加 GLM_API_KEY；旧 jar 备份为 run/app.jar.sep18，新 jar 就位重启
  - 外网实测：/api/wx/category/list 正常；/api/wx/chat source=glm、3.7s、会员价格回答正确 ✅
- **客服浮窗**：新组件 components/float-chat（右下角霓虹胶囊+呼吸灯），接入首页/分类/详情三页；上传体验版 **20260929.2**（118KB），体验版标签已自动跟随
- **打包坑（重要）**：src/main/resources/static/posters 里 437MB 海报会被打进 jar；且 mvn 资源拷贝是增量的，挪走源目录后 target/classes 仍残留 → 打部署包前 `rm -rf target/classes/static/posters` 再 package（jar 从 529MB 回到 86MB）。服务器海报走 nginx /posters/，jar 本来就不需要
- 本地约束解除：AI 客服现在不依赖"电脑开机+同 WiFi"，走 movie.jszzbinfo.cn 全网可用

## 2026-09-29 会话三：客服"治胡说"
- 用户实测吐槽答非所问。查 t_chat_log 定位三类垃圾引用：问"你好"→拖回《你好呀！亲爱的伦敦》；问"会员多少钱"→《我们到底知道多少》；问"漫威宇宙"→《宇宙追缉令》等一堆"宇宙"片当答案报给用户
- 修复三处（commit f6e69efa）：① candidatesOf ngram 下限 2→3 字；② 噪词表补寒暄词（你好/谢谢/再见/你是谁…）与 相关/系列/有哪些；③ system prompt 新规：列举影片只许罗列资料命中的，资料外常识补充必须声明"不一定在库里"
- 数据补强：t_chat_faq 新增 #11 漫威片单（keywords 漫威|漫威宇宙|超级英雄|marvel|复仇者…，片单来自 t_video_info 实查 15 部），本地+服务器+sql/ai_chat.sql 三处同步
- 回归（云端+本地双路）：你好→refs 干净；漫威宇宙→FAQ#11 报真片单；会员多少钱→无垃圾引用；星际穿越→照常
- 经验：系列/关键词类问题（"漫威有哪些"）片名检索天然答不了，走 FAQ 补知识是正解；以后片库变化记得同步 FAQ#11 片单

## 2026-10-06 会话四：GitHub 净化复核（ZCode）
- 用户让 Codex 扫描修复 GitHub 四仓库漏洞，ZCode 事后逐项复核（详见 findings.md「GitHub 净化复核」节）
- 结论：GitHub 端重建净化历史属实且基本干净（敏感文件确认未进新历史）；残留 3 个低危文件；GitHub 版缺 9-29 AI 客服；**Gitee 公开镜像仍是全套脏历史=当前真实泄漏点**；TMDB key/DB 口令未轮换
- 红线已写入 findings：本地历史≠GitHub 净化历史（无共同祖先），禁止 push github；Gitee 待清洗
- 本地只做了 git fetch github + 只读核查；findings/task_plan 的未提交改动是 9-29 会话遗留，与本次复核记录一并由本 commit 收录
