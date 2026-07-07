#!/usr/bin/env python3
"""fix_body_quotes.py — 修复 daily-data.js 中 body 字段的 href 引号

将 href="URL"> 替换为 href='URL'>

配置：通过环境变量 PROJECT_DIR 指定项目路径
"""

import re, subprocess, os, sys

PROJECT_DIR = os.getenv("PROJECT_DIR", ".")
JS_FILE = f"{PROJECT_DIR}/daily-data.js"

with open(JS_FILE, "r", encoding="utf-8") as f:
    content = f.read()

content = re.sub(r"href='([^']+)\">", "href='\\1'>", content)

with open(JS_FILE, "w", encoding="utf-8") as f:
    f.write(content)

# 用 Node 验证语法
js_path = JS_FILE.replace("\\", "/")
result = subprocess.run(["node", "-e", f"""
const fs = require("fs");
const code = fs.readFileSync("{js_path}", "utf-8");
const start = code.indexOf("var articles");
const end = code.indexOf("}},") + 1;  // first article
const test = code.substring(0, end) + "];";
try {{
    eval(test);
    console.log("VALID:", articles[0].title);
}} catch(e) {{
    console.log("ERROR:", e.message);
}}
"""], capture_output=True, text=True, timeout=10)
print(result.stdout.strip() or result.stderr.strip()[:200])
