---
name: agent-daily-installer
description: 安装并配置 agent-daily-pipeline 日报系统。克隆仓库 → 配 .env → 跑日报。当用户说「跑日报」「装日报」「部署日报」时使用。
---

# Agent Daily Installer

这个 skill 帮你安装和运行 **agent-daily-pipeline**——一套自动抓取 AI 新闻、生成文章、部署到 Vercel 的日报系统。

## 前置检查

在开始之前，确认以下工具可用：

```bash
# Python 3.10+
python3 --version

# Node.js（用于 JS 语法验证）
node --version

# Git
git --version
```

## 安装步骤

### Step 1: 克隆仓库

```bash
git clone https://github.com/ran666888/agent-daily-pipeline.git
cd agent-daily-pipeline
```

### Step 2: 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，填入你的配置：

```env
PROJECT_DIR=/home/user/agent-daily-pipeline
```

### Step 3: 测试抓取

```bash
python3 fetch_news.py
```

确认能看到各数据源的输出。

### Step 4: 准备日报数据

首次使用需要从零开始填充 `daily-data.js`。手动创建初始数据集，或从已有的数据仓库迁移。

### Step 5: 运行编排

```bash
export PROJECT_DIR=$(pwd)
python3 scripts/run_daily_update.py
```

## 日常使用

当用户说「跑日报」时：

```bash
cd /path/to/agent-daily-pipeline

# 1. 抓取最新数据
python3 fetch_news.py > /tmp/raw_news.txt

# 2. （可选）用 AI 生成文章
#    根据原始数据生成 18+ 篇新文章，插入 daily-data.js

# 3. 运行编排（验证+插卡片+重建首页JS）
python3 scripts/run_daily_update.py

# 4. 提交并部署
git add daily-data.js daily-data-home.js daily.html
git commit -m "📰 日报 YYYY.MM.DD: N篇"
git push origin main
```

## 常见问题

### 数据源报错

某些源（如 arXiv、HF Daily Papers）偶尔超时或暂时不可用。这些跳过不影响整体流程。

### JS 语法错误

`daily-data.js` 出现 JS 语法错误时：
1. 运行 `python3 scripts/fix_body_quotes.py` 修复引号
2. 重新运行编排脚本

### Cloudflare 清缓存

如果使用了 Cloudflare CDN，部署后需要清缓存：
```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache" \
  -H "X-Auth-Email: {email}" \
  -H "X-Auth-Key: {key}" \
  -H "Content-Type: application/json" \
  -d '{"purge_everything": true}'
```

## 关联资源

- 代码仓库：https://github.com/ran666888/agent-daily-pipeline
- 线上演示：https://www.agthub.tech/daily （活案例，每天都在跑）
