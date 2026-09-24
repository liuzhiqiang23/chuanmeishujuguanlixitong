# AGENTS.md（项目级上下文入口）

**项目**：电影票房预测与智能推荐系统（`D:\movie-system`）—— Spring Boot 3.5 后端（端口 8000，包 `com.alvis.media`）+ Vue3 管理后台 + MySQL `movie_analytics_db` + Python 算法引擎；另含微信小程序端「阿强观影」（appid `wx0ce243dae842cc7e`）。

## 开工先读这几份（进度记忆，跨会话续接用）

| 文件 | 内容 | 什么时候读 |
|---|---|---|
| `task_plan.md` | 阶段计划 + 当前阶段 + 待决问题 | **每次开始工作前**（看"现在该做什么"） |
| `findings.md` | 事实证据（后台原文、驳回原因、改造锚点、环境坑） | 做判断/写代码前 |
| `progress.md` | 会话日志 + 提交记录 + 测试结果 | 想了解"之前做到哪了" |
| `docs/01`~`docs/06` | 作业交付文档（需求/设计/审查/联调测试） | 写报告或核对需求时 |
| `用户手册.md`、`项目结构.md` | 使用说明与目录/配置速查 | 部署、排障时 |

阶段完成或产生新发现后，**请顺手更新这三份记忆文件**（状态、发现、下一步），这样下一个会话不用重新摸底。

## 硬约束（违反会造成数据或账号风险）

- `local_env.cmd`（DB 口令 + RSA 密钥对）**永不入库、永不外发**；密钥类配置一律走它 + `application-dev.yml`
- `.claude/`、`.vscode/` 是本地 AI/编辑器配置，**不要删除**
- `*.cmd` 必须**纯 ASCII + CRLF**（含中文或 LF 会让 cmd.exe 解析错乱）
- 微信账号侧操作（认证、扫码、开通虚拟支付、提交审核）**只做只读核查，不代替用户点确认**
- 大文件（模型、数据集、海报、内网穿透二进制）不入库，已在 `.gitignore`

## 常用命令

```bash
# 启动（一键：环境自检 → 重启后端 → 开浏览器）
start_all.cmd                     # 仅重启后端用 restart_backend.cmd

# 自检
.venv\Scripts\python.exe tools/verify_all.py                  # 17 项接口验收
.venv\Scripts\python.exe tools/verify_inference_consistency.py 500

# 小程序上传（微信开发者工具 CLI）
"D:\微信开发者工具\cli.bat" upload --project D:\movie-system\miniprogram -v <版本号> -d "<备注>"

# 推送（GitHub 走 443，22 端口在本网络被重置）
git push gitee master && git push github master
```
