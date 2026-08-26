"""Import local curriculum text into knowledge.json without any server."""
import json, os
from .arabic import normalize

def ingest_text(path, out_path):
    with open(path, encoding="utf-8") as f: text = f.read()
    title = os.path.splitext(os.path.basename(path))[0]
    doc = {"title": title, "content": text, "normalized": normalize(text)}
    try:
        with open(out_path, encoding="utf-8") as f: data = json.load(f)
    except (OSError, ValueError): data = []
    data = [d for d in data if d.get("title") != title]
    data.append(doc)
    with open(out_path, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)
    return doc
