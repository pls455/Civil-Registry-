import json, math, re
from pathlib import Path

ROOT=Path(__file__).parent

class MinhajAI:
    def __init__(self):
        self.docs=json.loads((ROOT/'data'/'knowledge.json').read_text(encoding='utf-8'))
        self.history=[]

    def tokenize(self, text):
        return [x for x in re.findall(r'[\u0600-\u06ff\w]+', text.lower()) if len(x)>1]

    def search(self, query, limit=4):
        q=set(self.tokenize(query)); scored=[]
        for d in self.docs:
            words=set(self.tokenize(d['title']+' '+d['text']+' '+d.get('subject','')))
            score=len(q & words)
            if score: scored.append((score,d))
        return [d for _,d in sorted(scored,key=lambda x:x[0],reverse=True)[:limit]]

    def answer(self, message):
        low=message.lower()
        hits=self.search(message)
        if any(k in low for k in ['اختبار','quiz','امتحان']):
            qs=[{'question':d['question'],'answer':d['answer']} for d in self.docs if 'question' in d][:5]
            return {'mode':'quiz','answer':'جهزت لك اختبارًا محليًا من قاعدة المعرفة.','questions':qs}
        if any(k in low for k in ['احسب','حل','=','رياضيات']):
            result=self.calculate(message)
            if result is not None: return {'mode':'math','answer':f'الناتج = {result}'}
        if hits:
            context='\n\n'.join(f"{d['title']}: {d['text']}" for d in hits)
            return {'mode':'study','answer':self.compose(message,context),'sources':[d['title'] for d in hits]}
        return {'mode':'general','answer':'لم أجد معلومة مطابقة في قاعدة المعرفة المحلية. أضف الدرس أو السؤال إلى data/knowledge.json وسأستخدمه مباشرة.'}

    def compose(self,q,context):
        return f'بناءً على المحتوى المحلي:\n\n{context}\n\nالسؤال: {q}\n\nالشرح: ركّز على المفاهيم المذكورة أعلاه، ثم طبّقها على السؤال خطوة بخطوة. هذه الإجابة مبنية من المعرفة المخزنة محليًا وليست من خدمة خارجية.'

    def calculate(self,text):
        m=re.search(r'([0-9\s+\-*/().]+)',text)
        if not m or not any(c in m.group(1) for c in '+-*/'): return None
        expr=m.group(1).strip()
        if len(expr)>60: return None
        if not re.fullmatch(r'[0-9\s+\-*/().]+',expr): return None
        try:
            return round(eval(expr,{'__builtins__':{}},{}),10)
        except Exception: return None

    def knowledge_summary(self):
        return {'documents':len(self.docs),'subjects':sorted(set(d.get('subject','عام') for d in self.docs))}
