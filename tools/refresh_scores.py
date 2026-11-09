#!/usr/bin/env python3
"""Copy updated scores from companies.json into an existing site_data JSON (weekly news refresh).

Usage: python3 refresh_scores.py companies.json site_data_claude.json ../site_data.json
Only score, score_parts, score_rank and why change; members, weights and the index value stay as they are.
"""
import json, sys
comp = {c["ticker"]: c for c in json.load(open(sys.argv[1]))}
for path in sys.argv[2:]:
    d = json.load(open(path))
    for c in d["top"] + d["others"]:
        src = comp.get(c["ticker"])
        if src:
            for k in ("score", "score_parts", "score_rank", "why"):
                if k in src:
                    c[k] = src[k]
    json.dump(d, open(path, "w"), indent=1)
    print("refreshed", path)
