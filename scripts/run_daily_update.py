#!/usr/bin/env python3
"""run_daily_update.py — 日报更新编排脚本

执行顺序：
  1. 前置检查（class名、卡片数量、node语法）
  2. 从 daily-data.js 提取最新日期文章
  3. 插入 daily.html（正确 entry-* 格式）
  4. 修复 body 引号
  5. 修复多行body（JS语法修正）
  6. 重建 daily-data-home.js（首页JS）
  7. JS 语法门禁
  8. 卡片数量验证
  9. 打印 git 命令

配置：通过环境变量 PROJECT_DIR 指定项目路径（不含末尾斜杠）
      echo "PROJECT_DIR=/path/to/your/project" > .env

依赖：Python 3, Node.js (用于JS语法验证)
"""

import json, re, subprocess, sys, os, shutil

PROJECT_DIR = os.getenv("PROJECT_DIR", ".")
JS_FILE = f"{PROJECT_DIR}/daily-data.js"
HTML_FILE = f"{PROJECT_DIR}/daily.html"
HOME_JS_FILE = f"{PROJECT_DIR}/daily-data-home.js"
SCRIPTS_DIR = f"{PROJECT_DIR}/scripts"

def die(msg):
    print(f"❌ {msg}")
    sys.exit(1)

def ok(msg):
    print(f"✅ {msg}")

# ═══════════════════════════════
# PRE-CHECK 1: 文件存在
# ═══════════════════════════════
for f in [JS_FILE, HTML_FILE]:
    if not os.path.isfile(f):
        die(f"文件不存在: {f}")
ok("PRE-CHECK 1: 文件存在")

# ═══════════════════════════════
# PRE-CHECK 2: 卡片使用 entry-* 类名
# ═══════════════════════════════
with open(HTML_FILE, "r", encoding="utf-8") as f:
    html_content = f.read()

bad_patterns = ["daily-date", "daily-title", "daily-tag", "daily-summary", "daily-meta"]
found_bad = [p for p in bad_patterns if p in html_content and p not in ["daily-entry", "daily-entry-new"]]
if found_bad:
    die(f"HTML 中仍有错误 class 名: {found_bad}")
ok("PRE-CHECK 2: 无 daily-* 错误类名")

# ═══════════════════════════════
# PRE-CHECK 3: JS 语法
# ═══════════════════════════════
js_path = JS_FILE.replace("\\", "/")
r = subprocess.run(["node", "-e",
    f"const fs=require('fs'); try {{ eval(fs.readFileSync('{js_path}','utf-8')); console.log('JS OK:',articles.length); }} catch(e) {{ console.log('JS SYNTAX ERROR:',e.message); process.exit(1); }}"
], capture_output=True, text=True, timeout=15)
if r.returncode != 0:
    die(f"JS 语法错误 — {r.stderr.strip() or r.stdout.strip()}")
ok(f"PRE-CHECK 3: JS 语法通过 ({r.stdout.strip()})")

# ═══════════════════════════════
# STEP 1: 提取最新日期文章
# ═══════════════════════════════
with open(JS_FILE, "r", encoding="utf-8") as f:
    js_content = f.read()

pos = js_content.find("var articles = [")
if pos < 0:
    die("找不到 var articles = [ 在 daily-data.js 中")

article_pattern = re.compile(
    r'\{[^}]*?date:\s*"([^"]+)"[^}]*?tag:\s*"([^"]+)"[^}]*?title:\s*"([^"]+)"[^}]*?body:\s*"((?:[^"\\]|\\.)*)"[^}]*?\}',
    re.DOTALL
)
all_articles = article_pattern.findall(js_content)
print(f"📄 读取到 {len(all_articles)} 篇文章")

if not all_articles:
    die("没有文章数据")

dates = sorted(set(a[0] for a in all_articles))
latest_date = dates[-1]
new_articles = [a for a in all_articles if a[0] == latest_date]
print(f"📅 最新日期: {latest_date} ({len(new_articles)} 篇)")

# ═══════════════════════════════
# STEP 2: 防重复检查
# ═══════════════════════════════
existing_count = html_content.count(f'entry-date">{latest_date}</div>')
print(f"🔍 daily.html 中已有 {latest_date} 的卡片: {existing_count} 篇")

if existing_count >= len(new_articles) * 0.5:
    print(f"✅ 最新日期卡片已存在（{existing_count}篇），跳过插入")
else:
    print(f"🔄 需要插入 {len(new_articles)} 篇新卡片")
    cards = []
    for a in new_articles:
        date_str, tag, title, body_str = a
        url_match = re.search(r'href=[\'"]([^\'"]+)[\'"]', body_str)
        article_url = url_match.group(1) if url_match else "#"
        body_stripped = body_str.replace("\\n", "\n").replace('\\"', '"')
        ps = re.findall(r"<p>(.*?)</p>", body_stripped, re.DOTALL)
        max_body_lines = 3
        body_lines_html = "".join(f"<p>{p.strip()}</p>" for p in ps[:max_body_lines])
        card = f"""      <!-- NEW: {date_str} -->
      <div class="daily-entry daily-entry-new">
        <div class="entry-date">{date_str}</div>
        <div class="entry-title"><a href="{article_url}">{title}</a></div>
        <div class="entry-meta"><span class="tag">{tag}</span></div>
        <div class="entry-summary">{body_lines_html}</div>
      </div>"""
        cards.append(card)

    grid_marker = '<div class="daily-grid">'
    grid_pos = html_content.find(grid_marker)
    if grid_pos < 0:
        die("找不到 <div class=\"daily-grid\">")
    insert_pos = grid_pos + len(grid_marker)
    html_content = html_content[:insert_pos] + "\n" + "\n".join(cards) + "\n" + html_content[insert_pos:]
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ daily.html: 插入了 {len(cards)} 篇卡片")

# ═══════════════════════════════
# STEP 4: 修复 body 引号
# ═══════════════════════════════
fix_script = f"{SCRIPTS_DIR}/fix_body_quotes.py"
if os.path.isfile(fix_script):
    print("🔄 运行 fix_body_quotes.py...")
    r = subprocess.run(["python3", fix_script], cwd=PROJECT_DIR, capture_output=True, text=True, timeout=30)
    print(r.stdout.strip())
    if r.returncode != 0:
        die(f"fix_body_quotes.py 失败: {r.stderr.strip()}")

# ═══════════════════════════════
# STEP 5: 重建 daily-data-home.js
# ═══════════════════════════════
build_script = f"{SCRIPTS_DIR}/build_home_daily.py"
if os.path.isfile(build_script):
    print("🔄 运行 build_home_daily.py...")
    r = subprocess.run(["python3", build_script], cwd=PROJECT_DIR, capture_output=True, text=True, timeout=30)
    print(r.stdout.strip())
    if r.returncode != 0:
        die(f"build_home_daily.py 失败: {r.stderr.strip()}")

# ═══════════════════════════════
# STEP 7: JS 语法门禁
# ═══════════════════════════════
print("🔄 JS 语法门禁...")
r = subprocess.run(["node", "-e",
    f"const fs=require('fs'); try {{ eval(fs.readFileSync('{js_path}','utf-8')); console.log('OK:',articles.length); }} catch(e) {{ console.log('ERROR:',e.message); process.exit(1); }}"
], capture_output=True, text=True, timeout=15)
if r.returncode != 0:
    die(f"JS 门禁失败: {r.stderr.strip() or r.stdout.strip()}")
print(f"✅ JS 门禁通过: {r.stdout.strip()}")

# ═══════════════════════════════
# STEP 8: 卡片门禁
# ═══════════════════════════════
with open(HTML_FILE, "r", encoding="utf-8") as f:
    final_html = f.read()
bad_remaining = [p for p in bad_patterns if p in final_html and p not in ["daily-entry", "daily-entry-new"]]
if bad_remaining:
    die(f"HTML 中仍有错误类名: {bad_remaining}")
entry_count = final_html.count("entry-date")
print(f"✅ 卡片门禁通过: {entry_count} 张卡片")

# ═══════════════════════════════
# STEP 9: 打印 git 命令
# ═══════════════════════════════
print()
print("=" * 60)
print("✅ 全部前置检查和更新完成。可以部署。")
print()
print("手动执行：")
print(f"  cd {PROJECT_DIR}")
print(f"  git add daily-data.js daily-data-home.js daily.html")
print(f"  git commit -m \"📰 日报 {latest_date}: {len(new_articles)}篇\"")
print(f"  git push origin master")
print()
print("部署后：")
print("  1. 清 CDN 缓存（如有）")
print("  2. curl 检查线上页面")
print("=" * 60)
