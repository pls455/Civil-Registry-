"""Local study planner and mastery tracking."""
class StudyPlanner:
    def __init__(self): self.scores = {}
    def record(self, topic, correct, total):
        if total <= 0: return
        self.scores[topic] = round((correct / total) * 100, 1)
    def recommend(self):
        if not self.scores: return "ابدأ باختبار قصير لتحديد مستواك."
        weak = sorted(self.scores.items(), key=lambda x:x[1])[:3]
        return "راجع أولًا: " + "، ".join(f"{t} ({s}%)" for t,s in weak)
