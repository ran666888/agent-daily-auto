#!/usr/bin/env python3
"""agent-daily-pipeline: fetch_news.py

多源数据抓取 — 从 HN/TechCrunch/arXiv/HF Daily Papers/GitHub Trending
抓取最新 AI Agent 相关新闻和技术动态。

使用：
    python3 fetch_news.py

配置：
    NEWS_LIMIT=10 python3 fetch_news.py   # 每源最多10条
"""

import urllib.request, json, sys, os

UA = "Mozilla/5.0 (compatible; DailyBot/1.0; +https://github.com/ran666888/agent-daily-pipeline)"
TO = 20

def fetch_hn(query, hits=10):
    url = f"https://hn.algolia.com/api/v1/search_by_date?query={query}&tags=story&hitsPerPage={hits}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    data = json.loads(urllib.request.urlopen(req, timeout=TO).read())
    r = []
    for h in data.get("hits", []):
        r.append({"date": h.get("created_at","")[:10], "title": h.get("title",""),
                  "url": h.get("url","") or f"https://news.ycombinator.com/item?id={h.get('objectID','')}",
                  "points": h.get("points","?"), "author": h.get("author",""), "source": "Hacker News"})
    return r

def fetch_tc(limit=10):
    try:
        import xml.etree.ElementTree as ET
        raw = urllib.request.urlopen(urllib.request.Request("https://techcrunch.com/category/artificial-intelligence/feed/", headers={"User-Agent": UA}), timeout=TO).read()
        r = []
        for it in ET.fromstring(raw).findall(".//item")[:limit]:
            r.append({"date": it.findtext("pubDate","")[:16], "title": it.findtext("title",""), "url": it.findtext("link",""), "source": "TechCrunch AI"})
        return r
    except: return []

def fetch_arxiv(limit=10):
    try:
        import xml.etree.ElementTree as ET
        raw = urllib.request.urlopen(urllib.request.Request(f"http://export.arxiv.org/api/query?search_query=all:AI+AND+all:agent&start=0&max_results={limit}", headers={"User-Agent": UA}), timeout=TO).read()
        ns = {"a":"http://www.w3.org/2005/Atom"}
        r = []
        for e in ET.fromstring(raw).findall("a:entry", ns):
            t = e.find("a:title", ns); l = e.find("a:id", ns); p = e.find("a:published", ns)
            r.append({"date": p.text[:10] if p is not None else "", "title": (t.text or "").replace("\n"," ").strip() if t is not None else "", "url": l.text if l is not None else "", "source": "arXiv"})
        return r
    except: return []

def fetch_hf(limit=10):
    try:
        url = "https://huggingface.co/api/daily_papers"
        data = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=TO).read())
        return [{"date": (p.get("publishedAt","")[:10]) if p.get("publishedAt") else "", "title": p.get("title",""), "url": f"https://huggingface.co/papers/{p.get('id','')}", "source": "Hugging Face"} for p in data[:limit]]
    except: return []

def fetch_gh(limit=10):
    try:
        from datetime import datetime, timedelta
        since = (datetime.now()-timedelta(3)).strftime("%Y-%m-%d")
        data = json.loads(urllib.request.urlopen(urllib.request.Request(f"https://api.github.com/search/repositories?q=AI+agent+created:%3E{since}&sort=created&order=desc&per_page={limit}", headers={"User-Agent": UA, "Accept": "application/vnd.github.v3+json"}), timeout=TO).read())
        return [{"date": r.get("created_at","")[:10], "title": r.get("description",r.get("full_name","")), "url": r.get("html_url",""), "source": f"GitHub: {r.get('full_name','')}"} for r in data.get("items",[])]
    except: return []

SOURCES = [
    ("Hacker News (AI)", lambda: fetch_hn("AI+agent+coding", 6)),
    ("TechCrunch AI", fetch_tc),
    ("arXiv (AI Agent)", fetch_arxiv),
    ("Hugging Face Daily", fetch_hf),
    ("GitHub Trending", fetch_gh),
]

if __name__ == "__main__":
    limit = int(os.getenv("NEWS_LIMIT", 6))
    for name, fn in SOURCES:
        print(f"\n{'='*60}\n📡 {name}\n{'='*60}")
        for item in (fn() or []):
            print(f"[{item['date']}] {item['title']}\n  URL: {item['url']}\n")
