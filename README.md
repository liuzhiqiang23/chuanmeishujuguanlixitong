# movie-system

#### 介绍

随着电影产业数字化发展，TMDB（电影数据库）与 MovieLens（电影评分网站）等平台积累了海量电影元数据与用户行为数据，而传统的人工运营推荐方式效率低、颗粒度粗，难以满足用户个性化观影需求。基于数据挖掘与机器学习的内容分析、票房预测与个性化推荐，已成为传媒数据应用的核心环节。
本项目要求学生从零构建一套完整的电影数据分析与推荐系统，涵盖数据清洗、特征工程、EDA 可视化、票房预测建模、个性化推荐算法、后端 API、前端界面与数据库设计，并实现 Java 后端与 Python 算法引擎的跨语言调用，模拟企业级开发全流程。

#### 软件架构

系统按企业级开发规范组织，各需求对应的底层算法模块相互独立、共享同一份数据集与清洗产物：

```text
movie-system/                          # 系统根目录（整个目录拷贝到任何机器即可部署，零外部依赖）
├── .venv/                             # Python 3.13 虚拟环境（算法依赖已装好；不可用时可运行 setup_venv.cmd 重建）
├── data/                              # 统一数据集目录（工程唯一数据根，各算法模块共享）
│   ├── train.csv                      # 票房预测训练数据（含票房标签，5000 部）
│   ├── test.csv                       # 票房预测测试数据（待预测，5000 部，无票房列）
│   ├── new_source/                    # Kaggle The Movies Dataset 原始下载件（不入库，可删）
│   ├── make_new_dataset.py            # 数据集抽样脚本：三表合并去重 → 固定种子 42 抽 5000+5000
│   └── processed/                     # 清洗与特征工程产物（preprocess.py 生成）
├── algorithm/                         # Python 算法引擎（不含数据，统一从 data/ 读取）
│   ├── FeatureEDA/                    #   需求一：数据分析与特征可视化
│   │   ├── preprocess.py              #     数据清洗与特征工程（共享流水线）
│   │   ├── eda.py                     #     EDA 唯一图脚本：一次生成 21 张图（fig01~fig14 + 7 张网页图）
│   │   └── figures/                   #     EDA 输出图（后端 /eda/** 挂载，无需 Python 在线）
│   ├── boxoffice_prediction/          #   需求二：电影票房预测
│   │   ├── train_all.py               #     8 种算法一键对比训练（metrics.json + 对比图 + 最佳模型）
│   │   ├── predict_api.py             #     在线推理服务（单片 / 批量，供后端 ProcessBuilder 调用）
│   │   └── metrics.json               #     各算法评估指标（RMSE / MAE / R²）
│   └── movie_recommendation/          #   需求三：智能推荐（内容相似 + 类型热门）
│       └── recommend_api.py           #     推荐服务（加权余弦相似度，磁盘缓存加速）
├── docs/                              # 作业分层文档（需求分析 / 概要设计 / 详细设计 / 审查 / 联调测试记录）
├── sql/                               # 数据库建库 / 修复 / 数据导入脚本
├── backend/                           # Spring Boot 后端（内嵌编译好的前端页面，端口 8000）
├── frontend/                          # Vue 前端源码（构建产物位于 backend/src/main/resources/static/admin）
├── requirements.txt                   # Python 依赖清单
├── setup_venv.cmd                     # 新机器一键重建 Python 虚拟环境
├── start_all.cmd                      # ★ 一键启动：环境自检 → 重启后端 → 打开浏览器（详见《用户手册.md》）
├── restart_backend.cmd                # 仅重启后端（杀 8000 端口旧进程 → 后台启动 → 健康检查）
├── 用户手册.md                        # ★ 环境 / 一键启动 / 全新部署 / 功能说明 / 算法 / 数据库 / FAQ
└── 项目结构.md                        # 目录总览、数据流、配置一览、八步作业与提交对照
```

**数据目录规范（重要）**

- 工程内**只有 `data/` 一个数据根**，任何算法模块下都不再自带 `data` 目录（历史重复副本已清理）；
- 算法脚本统一用「自身文件位置」推导系统根目录后再拼接数据路径（`SYSTEM_ROOT/data/...`），
  不依赖当前工作目录，因此在任意目录下执行脚本都能正确读到数据；
- 目录划分：`data/` 放票房预测数据集、抽样脚本与共享清洗产物 `processed/`；旧版 TMDB/MovieLens 数据目录已于换数据集作业中清理。


#### 部署教程（整个目录拷贝到新机器即可，零外部代码依赖）

> 本工程已自包含：算法代码、数据集、EDA 输出图、前端页面、Python 虚拟环境全部收编在
> `movie-system` 目录内；`backend/src/main/resources/application-dev.yml` 中 Python 与 EDA
> 相关路径均为「相对 backend 目录」的相对路径，因此拷贝到任何盘符 / 目录都**无需改配置**。

**目标机器环境要求（基础软件，与外部代码无关）**

| 软件   | 版本            | 用途                         |
| ------ | --------------- | ---------------------------- |
| JDK    | 17+（21/26 亦可） | 后端                        |
| Maven  | 3.9+            | 后端构建                     |
| MySQL  | 8.x             | 数据库（库名 movie_analytics_db，含新项目 15 张表 + 框架 19 张表）|
| Redis  | 5+（127.0.0.1:6379，默认无密码） | 会话缓存 |
| Python | 3.10~3.12（仅在重建虚拟环境时需要） | 算法引擎 |

**部署步骤**

1. 拷贝整个 `movie-system` 文件夹到目标机器（路径随意，推荐纯英文路径）。
2. 启动 MySQL 与 Redis 服务。
3. 初始化数据库（建库建表，Windows 在 mysql bin 目录或配好 PATH 后执行；详见《用户手册.md》§4.2）：
   ```bash
   # ① 新项目 15 张表
   mysql -uroot -p123456 < sql/movie_analytics_db.sql
   # ② 框架 19 张表 + 演示数据（用户/影片/商城/日志）
   mysql -uroot -p123456 movie_analytics_db < sql/backup_vidio_mangage_db_20260922.sql
   # ③ 新数据集入库（10000 部影片及关联表，约 40 秒）
   .venv\Scripts\python.exe sql/import_movie_dataset.py
   ```
4. Python 虚拟环境：本包已随带 `.venv`（Python 3.13）。若换机器后不可用
   （例如目标机未安装同路径 Python 3.13），在 `movie-system` 根目录**双击 `setup_venv.cmd`** 即可自动重建。
5. 启动后端（工作目录必须是 `backend`）：
   - 命令行：`cd backend && mvn spring-boot:run`
   - 或打包后运行：`mvn clean package` 后 `java -jar target/mediaAnalysisSystem-3.0.3.jar`
   - IDE：用 IDE 打开 `backend`（Maven 工程），运行主类 `com.alvis.media.MediaApplication`（已附 `.vscode/launch.json`）
6. 浏览器访问 `http://localhost:8000/admin`，登录 `admin / 123456`。

#### 服务启停与重启（Windows / PowerShell）

> **懒人版**：双击项目根目录的 **`restart_backend.cmd`** 即可一次完成
> 「检查中间件 → 查进程 → 杀进程 → 启动 → 等待端口 → 健康检查」（下面各条命令即该脚本内部使用的等价手动命令，
> 需要逐步排查时可照抄单条执行）。脚本会以最小化窗口常驻后端，日志写入项目根 `_boot.log`。
>
> 前端页面由后端一并托管（`/admin`），**日常使用只需启停后端一个进程**；
> 只有在改前端源码做开发调试时才需要另开 `cd frontend && npm run dev`（端口 8002，已代理到 8000）。

**0. 前置中间件自检**（后端启动依赖 MySQL 与 Redis，二者没起来会启动失败）

```powershell
netstat -ano | findstr :3306 | findstr LISTENING   # MySQL，应有输出
netstat -ano | findstr :6379 | findstr LISTENING   # Redis，应有输出
```

**1. 检查当前后端进程**（后端端口 8000，输出最后一列即 PID）

```powershell
netstat -ano | findstr :8000 | findstr LISTENING
# 例：TCP  0.0.0.0:8000  0.0.0.0:0  LISTENING  21836   → PID 为 21836
tasklist /FI "PID eq 21836"                    # 可选：确认该 PID 是 java.exe
```

**2. 停止后端**

```powershell
taskkill /PID 21836 /F                          # 按 PID 强杀（把 21836 换成实际 PID）
Stop-Process -Id 21836 -Force                   # 等价的 PowerShell 写法

# 免查 PID：直接按端口杀掉占用 8000 的进程
$p = (Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue).OwningProcess
if ($p) { Stop-Process -Id $p -Force }
```

**3. 启动后端**（工作目录必须是 `backend`）

```powershell
cd backend
mvn -q -Dmaven.test.skip=true compile spring-boot:run   # 前台运行，Ctrl+C 结束

# 后台运行（关掉窗口也不中断，日志写入项目根目录 _boot.log）
# -Xmx512m：限制后端 JVM 堆上限，避免与 IDE/MySQL/Redis 抢内存导致 JVM native OOM（hs_err_pid*.log）
Start-Process cmd.exe -ArgumentList '/c','cd /d backend && mvn -q -Dmaven.test.skip=true compile spring-boot:run -Dspring-boot.run.jvmArguments=-Xmx512m 1> ..\_boot.log 2>&1' -WindowStyle Hidden
```

> **为什么要加 `-Dmaven.test.skip=true`**：`spring-boot:run` 会先执行 `test-compile`，而 `src/test`
> 下残留 JUnit4 写法（`@RunWith`、`org.junit.Test`），Spring Boot 3.5 的 `spring-boot-starter-test`
> 只带 JUnit5，会在编译测试源码时直接报错中断。因此启动与打包统一跳过测试编译。

**4. 健康检查**

```powershell
# 4.1 端口探针（能连通即已监听）
$c = New-Object Net.Sockets.TcpClient; $c.Connect('127.0.0.1',8000); $c.Close(); echo 'port 8000 OK'

# 4.2 页面可用性（返回 200）
(Invoke-WebRequest -Uri 'http://127.0.0.1:8000/admin/index.html' -UseBasicParsing).StatusCode

# 4.3 算法链路（返回 1 说明 Python 引擎调用正常）
#     用 Invoke-RestMethod 而不是 curl.exe：PowerShell 会把 curl 参数里的双引号吞掉，导致 JSON 解析失败
(Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/recommend' -Method Post -ContentType 'application/json' -Body '{"algo":"demographic","top":3}').code

# 4.4 查看运行日志
Get-Content _boot.log -Tail 30
```

**5. 一键重启（推荐日常使用）**：杀掉旧进程 → 重新启动 → 轮询等待端口 → 自动健康检查

```powershell
$old = netstat -ano | findstr ':8000' | findstr LISTENING | ForEach-Object { ($_ -split '\s+')[-1] }
foreach ($o in ($old | Select-Object -Unique)) { if ($o) { taskkill /PID $o /F } }
Start-Sleep -Seconds 2
Start-Process cmd.exe -ArgumentList '/c','cd /d backend && mvn -q -Dmaven.test.skip=true compile spring-boot:run -Dspring-boot.run.jvmArguments=-Xmx512m 1> ..\_boot.log 2>&1' -WindowStyle Hidden
for ($i=0; $i -lt 120; $i++) {
  Start-Sleep -Seconds 3
  try { $c = New-Object Net.Sockets.TcpClient; $c.Connect('127.0.0.1',8000); $c.Close()
        Write-Output "BACKEND UP after $(($i+1)*3)s"; break } catch {}
}
(Invoke-WebRequest -Uri 'http://127.0.0.1:8000/admin/index.html' -UseBasicParsing).StatusCode
```

> 若启动失败（端口一直不通），看日志：`Get-Content _boot.log -Tail 40`；
> 常见原因：MySQL/Redis 未启动、`8000` 端口被其他程序占用、Maven/JDK 未加入 PATH。

**改了前端源码后如何生效**

后端托管的是 `backend/src/main/resources/static/admin/` 下的**构建产物**，直接改 `frontend/src` 不会生效，
必须重新构建并拷贝后再重启后端。

**一键构建部署（推荐）**：直接运行项目根目录下的 `build_frontend.cmd`，脚本内部依次执行
「`npm run build` 构建 → `robocopy /MIR` 镜像同步产物到后端静态目录 → 提示浏览器刷新」；
第一个参数为 `-restart` 时同步完顺带调用 `restart_backend.cmd` 重启后端，第二个参数为 `-nopause`
时跳过脚本末尾的暂停，供脚本链式调用或自动化使用：

```powershell
.\build_frontend.cmd              # 构建 + 镜像同步到 backend 静态目录
.\build_frontend.cmd -restart     # 同上，并在同步后一键重启后端
```

其中 `/MIR` 会删除后端产物里前端已不存在的旧哈希文件（手工 `Copy-Item` 只增不删，旧文件会越积越多），
保证两端严格一致；robocopy 退出码 `0-7` 均算成功，脚本按 `>=8` 判失败。等价的手工命令：

```powershell
cd frontend
npm run build                                    # 构建产物输出到 frontend/admin
Set-Location ..
robocopy 'frontend\admin' 'backend\src\main\resources\static\admin' /MIR /NFL /NDL /NJH /NJS /NP
.\restart_backend.cmd                            # 重启后端加载新产物
```

**逐步排查用（手工三步）**：

```powershell
cd frontend
npm run build                                    # 构建产物输出到 frontend/admin
Copy-Item -Force 'admin\*' '..\backend\src\main\resources\static\admin\' -Recurse
Set-Location ..
.\restart_backend.cmd                            # 重启后端加载新产物
```

> `index.html` 已配置 `no-store` 不缓存、`js/css` 带内容哈希可长缓存，重启后浏览器强制刷新
> （`Ctrl+F5`）即可看到新版本。

#### 使用说明

**网页功能**
- 数据管理 / 用户分析 / 特征探索分析（EDA 页面）：后端把 `algorithm/FeatureEDA/figures/`
  下的 PNG 经 `/eda/**` 直接静态挂到页面，**无需 Python 在线运行**，刷新页面即可看到最新图。
- 推荐 / 票房预测页：后端按需调用 `.venv` 中的 Python 引擎（`../algorithm/...` 相对定位），
  首次调用稍慢（模型加载），之后正常。

**命令行（教师演示 / 重跑实验）**

```bash
# 全部在 movie-system 根目录执行即可（脚本内部基于自身位置定位数据）

# 1. 数据清洗与特征工程（生成 data/processed/*.csv，供三个算法模块共享）
.venv\Scripts\python.exe algorithm/FeatureEDA/preprocess.py

# 2. EDA 全量分析（一次生成 21 张图 → algorithm/FeatureEDA/figures/）
#    fig01~fig14 为多维度分析图，另 7 张固定名图为网页「特征探索分析」页面所用；
#    重跑后刷新网页（Ctrl+F5）即出新图。脚本基于自身位置定位数据与输出目录，任意目录执行均可。
.venv\Scripts\python.exe algorithm/FeatureEDA/eda.py

# 3. 多算法对比训练（8 种算法 → metrics.json + 算法对比图 + 最佳模型 joblib）
.venv\Scripts\python.exe algorithm/boxoffice_prediction/train_all.py
```

**注意事项**
- 视频上传（可选功能）：默认上传目录为本机 `D:\video\videoUpload`。目标机如无此目录请先创建，
  或修改 `frontend/src/views/video/upload.vue` 中 `Path.url`（约第 78 行）指向任意本机目录后重新构建前端。
- 数据库账号默认 `root / 123456`，如需修改请同步改 `backend/src/main/resources/application-dev.yml`。
- 只改 Java 后端：重启即可；改前端：需在 `frontend` 目录 `npm run build`，并把产物同步到
  `backend/src/main/resources/static/admin` 后重新打包。

#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request


#### 特技

1.  使用 Readme\_XXX.md 来支持不同的语言，例如 Readme\_en.md, Readme\_zh.md
2.  Gitee 官方博客 [blog.gitee.com](https://blog.gitee.com)
3.  你可以 [https://gitee.com/explore](https://gitee.com/explore) 这个地址来了解 Gitee 上的优秀开源项目
4.  [GVP](https://gitee.com/gvp) 全称是 Gitee 最有价值开源项目，是综合评定出的优秀开源项目
5.  Gitee 官方提供的使用手册 [https://gitee.com/help](https://gitee.com/help)
6.  Gitee 封面人物是一档用来展示 Gitee 会员风采的栏目 [https://gitee.com/gitee-stars/](https://gitee.com/gitee-stars/)
