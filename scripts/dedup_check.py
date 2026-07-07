#!/usr/bin/env python3
"""dedup_check.py — 日报文章去重检测

读取 daily-data.js，对比指定日期的文章与新标题的相似度，
防止同一新闻事件在不同日期重复出现。

用法：
  python3 scripts/dedup_check.py                     # 默认对比昨天 vs 今天
  python3 scripts/dedup_check.py --check 2026.06.27  # 指定日期
  python3 scripts/dedup_check.py --list               # 列出所有日期及篇数

配置：通过环境变量 PROJECT_DIR 指定项目路径
"""

import json, re, sys, subprocess, tempfile, os
from datetime import datetime, timedelta

PROJECT_DIR = os.getenv("PROJECT_DIR", ".")
JS_FILE = f"{PROJECT_DIR}/daily-data.js"

# 停用词
STOP_WORDS = set("""
的 了 在 是 与 和 或 从 被 让 将 已 为 会 又 不 要
这 那 一 个 有 上 下 中 都 来 去 就 也 还 把 给 对
向 到 用 以 而 所 能 可 但 该 此 却 则 于 之 其 它
她 他 并 及 未 没 更 最 很 太 多 少 仅 只 仅 还 不过
""".split())

# 同义实体映射
SYNONYM_MAP = [
    ("赫库兰尼姆古卷", ["赫库兰尼姆", "古卷", "Scroll Prize", "scrollprize", "纸莎草", "碳化古卷"]),
    ("苹果M7/M6芯片", ["M6", "M7", "M7系列", "M6芯片", "M7芯片", "Mac芯片", "苹果跳过"]),
    ("Patronus AI融资", ["Patronus", "AI安全评测", "压力测试"]),
    ("General Intuition游戏训练", ["General Intuition", "视频游戏训练"]),
    ("Anthropic Claude蚕食ChatGPT", ["Anthropic Claude付费", "蚕食ChatGPT"]),
    ("OpenKnowledge笔记工具", ["OpenKnowledge", "AI优先的笔记", "取代Obsidian"]),
    ("模型路由", ["模型路由", "智能路由", "WorkWeave", "Router"]),
    ("小米MiMo-Code", ["MiMo", "MiMo-Code", "小米开源", "协同进化"]),
    ("Omnigent多模型编排", ["Omnigent", "统一编排", "元训练"]),
    ("Superlog可观测性", ["Superlog", "可观测性", "自愈", "日志诊断"]),
    ("人味儿写作", ["人味儿", "Renwei", "人类温度"]),
    ("Liquid AI小模型", ["Liquid", "LFM", "230M", "最小模型"]),
    ("CoffeeBench多Agent", ["CoffeeBench", "咖啡经济", "多Agent协作"]),
    ("DeepMind百万Agent", ["DeepMind数百", "数百万Agent", "Agent互动"]),
    ("GPT-5.6 Sol", ["GPT-5.6", "Sol", "下一代模型"]),
    ("开源宣言", ["开源宣言", "捍卫", "联合宣言"]),
    ("AI破解安全挑战", ["破解AI", "2000人破解", "安全挑战", "注入攻击"]),
]


def entity_match(titles_a, titles_b):
    for entity_name, identifiers in SYNONYM_MAP:
        a_hits = sum(1 for ident in identifiers if ident.lower() in titles_a.lower())
        b_hits = sum(1 for ident in identifiers if ident.lower() in titles_b.lower())
        if a_hits >= 1 and b_hits >= 1:
            return True, entity_name
    return False, None


def parse_articles():
    """用 Node.js 解析 daily-data.js"""
    js_path = JS_FILE.replace("\\", "/")
    js_script = f"""
const fs = require('fs');
eval(fs.readFileSync('{js_path}', 'utf-8'));
var out = [];
articles.forEach(function(a) {{
    out.push({{date: a.date, title: a.title, tag: a.tag}});
}});
console.log(JSON.stringify(out));
"""
    tmp = tempfile.NamedTemporaryFile(suffix=".js", mode="w", delete=False, encoding="utf-8")
    tmp.write(js_script)
    tmp_path = tmp.name
    tmp.close()
    try:
        result = subprocess.run(["node", tmp_path], capture_output=True, text=True, timeout=10)
        os.unlink(tmp_path)
        if result.returncode != 0:
            print(f"❌ Node 解析失败: {result.stderr[:200]}", file=sys.stderr)
            sys.exit(2)
        return json.loads(result.stdout.strip())
    except Exception as e:
        print(f"❌ 解析异常: {e}", file=sys.stderr)
        os.unlink(tmp_path)
        sys.exit(2)


def extract_keywords(title):
    cleaned = re.sub(r'[：:，。！？、；\\(\\)（）「」【】""''【】『』〈〉《》★\\-\\–\\—]', " ", title)
    words = cleaned.split()
    return [w for w in words if w not in STOP_WORDS and len(w) >= 2]


def keyword_overlap(kw_a, kw_b):
    set_a = set(w.lower() for w in kw_a)
    set_b = set(w.lower() for w in kw_b)
    if not set_a or not set_b:
        return 0
    return len(set_a & set_b) / max(len(set_a), len(set_b))


def check_duplicates(check_date=None):
    articles = parse_articles()
    by_date = {}
    for a in articles:
        by_date.setdefault(a["date"], []).append(a)

    if check_date:
        today = check_date
    else:
        dates = sorted(by_date.keys())
        today = dates[-1] if dates else datetime.now().strftime("%Y.%m.%d")

    if "." in today:
        parts = today.split(".")
        dt = datetime(int(parts[0]), int(parts[1]), int(parts[2]))
    else:
        dt = datetime.now()
    yesterday = (dt - timedelta(days=1)).strftime("%Y.%m.%d")

    if yesterday not in by_date or today not in by_date:
        print(f"ℹ️ 缺少 {yesterday} 或 {today} 的数据，跳过去重")
        return True

    today_articles = by_date[today]
    yesterday_articles = by_date[yesterday]

    print(f"📅 今日 ({today}): {len(today_articles)} 篇")
    print(f"📅 昨日 ({yesterday}): {len(yesterday_articles)} 篇\n")

    duplicates = []
    for ta in today_articles:
        kw_today = extract_keywords(ta["title"])
        best_score = 0
        best_match = None
        for ya in yesterday_articles:
            score = keyword_overlap(kw_today, extract_keywords(ya["title"]))
            is_entity, entity_name = entity_match(ta["title"], ya["title"])
            if is_entity:
                score = max(score, 0.7)
            if score > best_score:
                best_score = score
                best_match = ya["title"]

        if best_score >= 0.5:
            duplicates.append((ta["title"], best_match, best_score))

    if duplicates:
        print(f"⚠️ 发现 {len(duplicates)} 个潜在重复:\n")
        for dt, dm, score in duplicates:
            print(f"  {'🔴' if score >= 0.6 else '🟡'} [{score:.0%}] 今日: {dt}")
            print(f"           昨日: {dm}\n")
        print("❌ 需要重新选题")
        return False
    else:
        print("✅ 今日文章与昨日无显著重复")
        return True


def list_dates():
    articles = parse_articles()
    by_date = {}
    for a in articles:
        by_date.setdefault(a["date"], []).append(a)
    print("📊 daily-data.js 日期统计:\n")
    for d in sorted(by_date.keys()):
        print(f"  {d}: {len(by_date[d])} 篇")


if __name__ == "__main__":
    if "--list" in sys.argv:
        list_dates()
        sys.exit(0)
    elif "--check" in sys.argv:
        idx = sys.argv.index("--check")
        date = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None
        ok = check_duplicates(date)
    else:
        ok = check_duplicates()
    sys.exit(0 if ok else 1)
