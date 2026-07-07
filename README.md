# Agent Daily Pipeline · 🤖 AI Agent 自动跑日报

[![Live Demo](https://img.shields.io/badge/👀_在线效果-agthub.tech-FF6B6B)](https://www.agthub.tech/daily)

> **搭建一次，以后每天对你的 Agent 说一句「跑日报」。**
>
> 抓数据、写文章、排版、部署网站 —— Agent 全部自动完成。
> **你唯一要做的是：看一眼，说「OK」。**

---

## 为什么这个项目值得你关注

传统的日报系统长这样：

```
你每天：起床 → 刷网页找新闻 → 手动复制 → 排版 → 写文章 → 部署 → 累死
```

这个项目长这样：

```
你每天：对你的 AI Agent 说「跑日报」→ 等 10 秒 → 看一眼 →「OK，发吧」
                                       ↑
                         Agent 帮你做完所有苦力活
```

**这不是概念。** 这个系统的日报从 2026 年 6 月开始，每天自动更新，已经跑了 49 期、400+ 篇文章——全都是一个人（没错，就一个人）用 Agent 自动维护的，每天花的时间不到 1 分钟。

---

## 👀 实例展示：正在跑的线上效果

这套系统已经在以下三个产品中生产运行。**它们不是 demo，是每天在线上跑的真东西：**

| 产品 | 你能看到什么 |
|------|------------|
| [**agthub.tech**](https://www.agthub.tech/daily) | Agent Hub 中文站 → 日报页面，Agent 每天自动更新内容 |
| [**openclawal.cn**](https://openclawal.cn) | OpenClaw 中文社区 → Agent 开源工具的门户网站 |
| **微信公众号：阿茅的数字大厦** | 日报内容同步发布到微信 → 公众号生态也覆盖了 |

> 三个产品均由**同一个人 + AI Agent** 每日自动运营。数据抓取 → AI 撰写 → 多平台同步（网站 + 公众号），全部无人值守。
>
> 想知道「Agent 自动化跑日报」长什么样？👇
> **去看看 [agthub.tech/daily](https://www.agthub.tech/daily) ，再关注公众号「阿茅的数字大厦」，感受一下每天 0 人工维护的真实效果。**

---

## 一句话就能跑：配合 Hermes Agent

这个项目是专为 **Hermes Agent** 设计的。装好配套 skill 后：

```bash
# 安装 skill
hermes skill install ran666888/agent-daily-installer

# 然后对你的 Agent 说👇
```

> **「跑日报」**

Agent 就会自动执行：
```
📡 抓取 Hacker News / TechCrunch / arXiv / Hugging Face / GitHub Trending
   ↓
🤖 AI 生成 18+ 篇文章
   ↓
📝 编排到日报页面
   ↓
🚀 自动部署到 Vercel
   ↓
✅ 通知你「搞定了，看一眼」
```

**你什么都不用做。Agent 干完活通知你，你看一眼说 OK 就行。**

> 💡 没有 Hermes Agent？也可以手动跑——下面有步骤。

---

## 还想更进一步？配合公众号自动发布

日报写好之后，想同步发到微信公众号？

搭配另一个开源项目 **[Agent WeChat Publisher](https://github.com/ran666888/agent-wechat-publisher)** 使用：

```bash
# 你的 Agent 现在会说👇
「跑日报」→ 更新网站 ✅
「发公众号日报」→ 自动发到微信 ✅
```

两个项目打通后，**你只需要对 Agent 说一句话，网站和公众号就全部更新好了。**

---

## 工作流程

```
┌─────────────────────────────────────────────────┐
│          你对 Agent 说「跑日报」                    │
└──────────────────────┬──────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│  Step 1: 自动抓取数据                           │
│  Hacker News · TechCrunch · arXiv              │
│  Hugging Face · GitHub Trending                 │
│  所有源都是免费的，无需 API Key                    │
└──────────────────────┬──────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│  Step 2: AI 自动撰写文章                        │
│  18+ 篇原创 AI Agent 新闻                      │
│  自动去重，避免和昨天重复                        │
└──────────────────────┬──────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│  Step 3: 编排到日报页                            │
│  插入卡片 → 重建首页JS → 语法验证                │
│  有问题自动卡住，不部署坏的                      │
└──────────────────────┬──────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│  Step 4: 自动部署                               │
│  git push → Vercel 自动构建 → CF 清缓存          │
│  🎉 日报上线！                                   │
└─────────────────────────────────────────────────┘
```

---

## 快速上手（手动模式）

不想用 Agent？手动跑也只需要 4 步：

### 1. 克隆

```bash
git clone https://github.com/ran666888/agent-daily-pipeline.git
cd agent-daily-pipeline
```

### 2. 配置

```bash
cp .env.example .env
# 编辑 .env，填入 PROJECT_DIR
```

### 3. 抓取测试

```bash
python3 fetch_news.py
```

### 4. 运行

```bash
export PROJECT_DIR=$(pwd)
python3 scripts/run_daily_update.py
```

更多细节见下方「项目结构」和「自定义」章节。

---

## 数据源

| 源 | 内容 | 需要 API Key？ |
|----|------|---------------|
| Hacker News | AI Agent 相关讨论和项目 | ❌ 免费 |
| TechCrunch AI | AI 行业最新报道 | ❌ 免费 |
| arXiv | AI Agent 学术论文 | ❌ 免费 |
| Hugging Face Daily Papers | 每日热门论文 | ❌ 免费 |
| GitHub Trending | 新创建的 AI Agent 项目 | ❌ 免费（有速率限制） |

所有数据源完全免费，**0 元启动**。

---

## 项目结构

```
agent-daily-pipeline/
├── fetch_news.py              # 多源数据抓取（5个源）
├── daily.html                 # 日报展示页模板
├── vercel.json                # Vercel 部署配置
├── scripts/
│   ├── run_daily_update.py    # 编排脚本（验证→插卡片→部署）
│   ├── build_home_daily.py    # 首页JS重建
│   ├── fix_body_quotes.py     # JS 引号修复
│   └── dedup_check.py         # 文章去重检测
├── .env.example               # 环境变量模板
└── README.md
```

---

## 许可证

MIT
