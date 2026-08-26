"""Main offline educational AI engine."""
import json, os
from .arabic import normalize
from .retrieval import Retriever
from .reasoning import safe_math, explain

class MinhajAI:
    def __init__(self, knowledge_path=None):
        root = os.path.dirname(os.path.dirname(__file__))
        self.path = knowledge_path or os.path.join(root, "data", "knowledge.json")
        self.docs = self._load()
        self.retriever = Retriever(self.docs)

    def _load(self):
        try:
            with open(self.path, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return []

    def ask(self, question):
        question = str(question or "").strip()
        if not question:
            return {"answer": "اكتب سؤالك أولًا.", "sources": []}
        result = safe_math(question)
        if result is not None:
            return {"answer": f"الناتج: {result}", "sources": []}
        hits = self.retriever.search(question, 3)
        if hits:
            best = hits[0]
            return {"answer": explain(best), "sources": [{"title": h.get("title"), "score": h["score"]} for h in hits]}
        return {"answer": "لم أجد معلومات كافية في قاعدة المعرفة المحلية. أضف محتوى الدرس إلى data/knowledge.json ثم أعد المحاولة.", "sources": []}
