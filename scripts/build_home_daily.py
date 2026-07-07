#!/usr/bin/env python3
"""build_home_daily.py — 从 daily-data.js 提取最新5篇文章，生成首页轻量版JS

配置：通过环境变量 PROJECT_DIR 指定项目路径
"""

import json, re, os, sys

PROJECT_DIR = os.getenv("PROJECT_DIR", ".")
BASE_JS = f"{PROJECT_DIR}/daily-data.js"
OUT_JS = f"{PROJECT_DIR}/daily-data-home.js"

# 读取 daily-data.js
with open(BASE_JS, "r", encoding="utf-8") as f:
    content = f.read()

# 找到 var articles = [ 开始位置
start_marker = "var articles = ["
pos = content.find(start_marker)
if pos < 0:
    print("ERROR: articles marker not found")
    sys.exit(1)

# 提取前5篇
full_array_part = content[pos + len(start_marker):]

brace_count = 0
article_count = 0
first5_end = 0
in_string = False
escape = False

for i, ch in enumerate(full_array_part):
    if escape:
        escape = False
        continue
    if ch == "\\":
        escape = True
        continue
    if ch == '"' and not escape:
        in_string = not in_string
        continue
    if in_string:
        continue
    if ch == "{":
        brace_count += 1
    elif ch == "}":
        brace_count -= 1
        if brace_count == 0:
            article_count += 1
            if article_count == 5:
                first5_end = i + 1
                break

if first5_end == 0:
    print(f"ERROR: 找到了 {article_count} 篇文章，不足5篇")
    sys.exit(1)

first5_text = full_array_part[:first5_end].rstrip().rstrip(",")

js_out = f"""// ══════ 首页日报数据 ══════
var articles = [
{first5_text}
];

var currentIdx = 0;

function renderArticle(idx) {{
  var a = articles[idx];
  var dcDate = document.getElementById('dcDate');
  var dcTag = document.getElementById('dcTag');
  var dcTitle = document.getElementById('dcTitle');
  var dcBody = document.getElementById('dcBody');
  if (!dcDate || !a) return;
  dcDate.textContent = a.date;
  dcTag.textContent = a.tag;
  dcTitle.textContent = a.title;
  dcBody.innerHTML = a.body;
  var nextIdx = (idx + 1) % articles.length;
  var next = articles[nextIdx];
  document.getElementById('dnTag').textContent = next.tag;
  document.getElementById('dnTitle').textContent = next.title;
}}

function nextArticle() {{
  currentIdx = (currentIdx + 1) % articles.length;
  renderArticle(currentIdx);
}}

function prevArticle() {{
  currentIdx = (currentIdx - 1 + articles.length) % articles.length;
  renderArticle(currentIdx);
}}

if (document.readyState === 'complete' || document.readyState === 'interactive') {{
  renderArticle(0);
}} else {{
  document.addEventListener('DOMContentLoaded', function() {{ renderArticle(0); }});
}}
"""

with open(OUT_JS, "w", encoding="utf-8") as f:
    f.write(js_out)

print(f"✅ {OUT_JS}: {len(js_out)} chars, {os.path.getsize(OUT_JS) // 1024} KB")
