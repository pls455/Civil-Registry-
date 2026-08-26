"""Prepare local curriculum JSON/TXT into JSONL instruction data.
Run offline. Input files belong in data/raw/ and should be owned/licensed by you.
"""
import json, pathlib, random, re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "training.jsonl"

TEMPLATES = [
    ("اشرح درس {title} بطريقة مبسطة.", "{content}"),
    ("لخص {title} لطالب مدرسة.", "{content}"),
    ("ما أهم فكرة في {title}؟", "{content}"),
    ("اعطني مراجعة سريعة عن {title}.", "{content}"),
]

def read_docs():
    docs=[]
    for p in RAW.rglob("*") if RAW.exists() else []:
        if p.suffix.lower()==".txt":
            text=p.read_text(encoding="utf-8", errors="ignore").strip()
            if text: docs.append({"title":p.stem,"content":text})
        elif p.suffix.lower()==".json":
            try:
                x=json.loads(p.read_text(encoding="utf-8"))
                docs.extend(x if isinstance(x,list) else [x])
            except Exception: pass
    return [d for d in docs if d.get("content")]

def build():
    random.seed(42); OUT.parent.mkdir(parents=True, exist_ok=True)
    rows=[]
    for d in read_docs():
        title=str(d.get("title","درس")); content=re.sub(r"\s+"," ",str(d["content"])).strip()
        for q,a in TEMPLATES: rows.append({"instruction":q.format(title=title),"response":a.format(content=content),"subject":d.get("subject","")})
    random.shuffle(rows)
    with OUT.open("w",encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r,ensure_ascii=False)+"\n")
    print(f"created {len(rows)} examples -> {OUT}")

if __name__=="__main__": build()
