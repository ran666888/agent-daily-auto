# 🤖 Agent Daily Pipeline

[![Live Demo](https://img.shields.io/badge/demo-agthub.tech-FF6B6B)](https://www.agthub.tech/daily)

> **一个人用 AI Agent 做的日报系统，每天自动更新。**
>
> 抓取 HN / TechCrunch / arXiv / Hugging Face / GitHub Trending → AI 生成文章 → 一键部署 Vercel。

---

## 这是什么

一个**完全开源的日报自动化系统**，每天自动：

1. 📡 从 5 个数据源抓取最新 AI Agent 新闻
2. 🤖 用 AI 撰写文章（可选 DeepSeek 等 API）
3. 📝 编排到 `daily-data.js` 数据仓库
4. 🚀 自动部署到 Vercel 静态站

**👉 [线上演示 → agthub.tech/daily](https://www.agthub.tech/daily)**

这个站从 2026 年 6 月开始，每天更新，已经跑了 49 期、400+ 篇文章——全都是一个人用 Agent 自动维护的，不用自己动手。

---

## 项目结构

```
agent-daily-pipeline/
├── fetch_news.py              ← 多源数据抓取（5个源）
├── daily.html                 ← 日报展示页模板
├── vercel.json                ← Vercel 部署配置
│
├── scripts/
│   ├── run_daily_update.py    ← 编排脚本（验证→插卡片→部署）
│   ├── build_home_daily.py    ← 首页JS重建
│   ├── fix_body_quotes.py     ← JS 引号修复
│   └── dedup_check.py         ← 文章去重检测
│
├── .env.example               ← 环境变量模板
└── README.md
```

---

## 快速上手

### 前置条件

- Python 3.10+
- Node.js（用于 JS 语法验证）
- 一个 Vercel 账号（免费）
- 一个 GitHub 账号（免费）

### 1. 克隆

```bash
git clone https://github.com/ran666888/agent-daily-pipeline.git
cd agent-daily-pipeline
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入你的配置
```

最小配置只需：
```env
PROJECT_DIR=/path/to/agent-daily-pipeline
```

### 3. 测试数据抓取

```bash
python3 fetch_news.py
```

会输出类似：
```
============================================================
📡 Hacker News (AI)
============================================================
[2026-07-07] Pi (Rust): High-performance AI coding agent CLI
  URL: https://github.com/example/pi
...
```

### 4. 准备日报数据

首次使用时，创建 `daily-data.js`：

```bash
# 从模板开始
cp daily-data.js.example daily-data.js
```

或者从已有数据集中拿到 `var articles = [...]` 数组直接使用。

### 5. 运行编排脚本

```bash
export PROJECT_DIR=$(pwd)
python3 scripts/run_daily_update.py
```

### 6. 部署到 Vercel

```bash
# 推送到 Git 仓库
git add .
git commit -m "📰 日报: 第一次部署"
git push

# Vercel 自动部署（或手动）
npx vercel --prod
```

---

## 数据源

| 源 | 内容 | 是否需要 API Key |
|---|---|---|
| Hacker News | AI Agent 相关讨论和项目 | ❌ 免费 |
| TechCrunch AI | AI 行业最新报道 | ❌ 免费 |
| arXiv | AI Agent 学术论文 | ❌ 免费 |
| Hugging Face Daily Papers | 每日热门论文 | ❌ 免费 |
| GitHub Trending | 新创建的 AI Agent 项目 | ❌ 免费（有速率限制） |

---

## 自定义

### 添加/删除数据源

编辑 `fetch_news.py` 中的 `SOURCES` 列表：

```python
SOURCES = [
    ("Hacker News (AI)", lambda: fetch_hn("AI+agent+coding", 6)),
    ("TechCrunch AI", fetch_tc),
    # 在这里添加或删除
]
```

### 修改日报样式

编辑 `daily.html` 中的 CSS（全部内联在 `<style>` 标签中）：

- 品牌色：默认法拉利红 `#D40000`，在 `:root{--red:#D40000}` 处修改
- 字体：默认 Apple 系统字体栈
- 卡片布局：搜索 `.daily-grid` 修改栅格

### 使用 AI 文章生成（可选）

在编排脚本中加入 AI 调用：
```python
# 调用 DeepSeek / OpenAI 等 API 生成文章
import requests
resp = requests.post("https://api.deepseek.com/v1/chat/completions",
    headers={"Authorization": f"Bearer {DEEPSEEK_KEY}"},
    json={"model": "deepseek-chat", "messages": [...]})
```

---

## 配合 Hermes Agent 使用

这个项目是专为 Hermes Agent 设计的。安装配套 skill 后，你只需要对你的 Agent 说：

> **「跑日报」**

Agent 就会自动完成：抓数据 → 生成文章 → 编排 → 部署。详见 `docs/hermes-integration.md`。

---

## Hermes Skill：agent-daily-installer

如果你想用 Hermes Agent 来自动管理这个日报系统，可以安装配套 skill：

```bash
# 用 Hermes CLI 安装
hermes skill install ran666888/agent-daily-installer
```

安装后，对你的 Agent 说「跑日报」即可自动执行整个流程。

---

## 设计思路

这个项目的核心哲学是：

1. **一个人 = 整个团队** — 用 Agent 替代 PM、编辑、运维的工作
2. **每天跑才是真本事** — 不是丢个 demo 就不管了，是真在线上跑
3. **所有代码可审查** — 脚本都放在这里，每一步都可以手动验证
4. **不依赖任何付费服务** — 数据源全免费，部署用 Vercel 免费版

> 从一个 22 岁待业青年的「一个人闲得慌」开始，到现在每天稳定更新——没什么牛逼的，就是每天跑。

---

## 许可证

MIT
