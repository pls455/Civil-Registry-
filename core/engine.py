"""Offline educational AI: intent detection, retrieval, memory and structured answers."""
import json, os, re
from .arabic import normalize, tokens
from .retrieval import Retriever
from .reasoning import safe_math, explain

class MinhajAI:
    def __init__(self, knowledge_path=None, memory_limit=12):
        root = os.path.dirname(os.path.dirname(__file__))
        self.path = knowledge_path or os.path.join(root, "data", "knowledge.json")
        self.docs = self._load()
        self.retriever = Retriever(self.docs)
        self.history = []
        self.memory_limit = memory_limit

    def _load(self):
        try:
            with open(self.path, encoding="utf-8") as f: return json.load(f)
        except (OSError, ValueError): return []

    def _intent(self, q):
        qn = normalize(q)
        if any(x in qn for x in ("اختبار", "امتحان", "اسئله", "اسئلة")): return "quiz"
        if any(x in qn for x in ("اشرح", "شرح", "وضح", "فهمني", "ما معنى")): return "explain"
        if any(x in qn for x in ("لخص", "تلخيص", "ملخص")): return "summary"
        return "answer"

    def ask(self, question):
        question = str(question or "").strip()
        if not question: return {"answer":"اكتب سؤالك أولًا.","sources":[],"intent":"empty"}
        result = safe_math(question)
        if result is not None: return self._remember(question, f"الناتج: {result}", "math", [])
        intent = self._intent(question)
        hits = self.retriever.search(question, 5)
        if not hits:
            # Search individual meaningful words for short Arabic questions.
            hits = self.retriever.search(" ".join(tokens(question)[-4:]), 5)
        if not hits:
            answer = "لم أجد مادة كافية في قاعدة المعرفة المحلية لهذا السؤال."
            return self._remember(question, answer, intent, [])
        best = hits[0]
        content = best.get("content", "")
        title = best.get("title", "الموضوع")
        if intent == "explain": answer = f"خلينا نبسطها. {title}:\n\n{content}"
        elif intent == "summary": answer = f"ملخص {title}:\n\n{content}"
        else: answer = f"الموضوع الأقرب لسؤالك هو: {title}\n\n{content}"
        return self._remember(question, answer, intent, [{"title":h.get("title"),"score":h["score"]} for h in hits])

    def _remember(self, q, answer, intent, sources):
        self.history.append({"question":q,"answer":answer,"intent":intent})
        self.history = self.history[-self.memory_limit:]
        return {"answer":answer,"sources":sources,"intent":intent}
