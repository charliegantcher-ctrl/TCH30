#!/usr/bin/env python3
"""Re-render the Claude TCH30 page from an existing site_data.json plus news.json,
without recomputing the index. Used by the weekly news refresh.

Usage: python3 render.py site_data.json [news.json] > writes index.html
"""
import json, sys, os

data = json.load(open(sys.argv[1]))
news_path = sys.argv[2] if len(sys.argv) > 2 else "news.json"
if os.path.exists(news_path):
    data["news"] = json.load(open(news_path))
page = open("template.html").read().replace("/*__DATA__*/null", json.dumps(data).replace("</", "<\\/"))
open("index.html", "w").write(page)
n = len((data.get("news") or {}).get("items", []))
print(f"rendered index.html with {len(data['top'])} members and {n} news stories")
