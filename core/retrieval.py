"""Offline lexical retrieval over local curriculum knowledge."""
from .arabic import normalize, tokens

class Retriever:
    def __init__(self, documents=None):
        self.documents = documents or []
        self.index = []
        for doc in self.documents:
            text = normalize(doc.get("title", "") + " " + doc.get("content", ""))
            self.index.append((set(tokens(text)), doc))

    def search(self, query, limit=5):
        q = set(tokens(query))
        if not q:
            return []
        scored = []
        for words, doc in self.index:
            overlap = len(q & words)
            if overlap:
                score = overlap / max(1, len(q))
                scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [{**doc, "score": round(score, 3)} for score, doc in scored[:limit]]
