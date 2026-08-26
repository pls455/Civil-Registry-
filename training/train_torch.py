"""Optional local fine-tuning scaffold.
Requires PyTorch installed locally. It trains a compact character language model from training.jsonl.
For serious quality, replace this baseline with a licensed pretrained Arabic model and LoRA/QLoRA.
"""
import json, pathlib, math

try:
    import torch
    import torch.nn as nn
except ImportError:
    raise SystemExit("Install PyTorch locally first; this training script never calls an API.")

ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/"data"/"training.jsonl"
OUT=ROOT/"models"/"minhaj_char.pt"

text=[]
for line in DATA.read_text(encoding="utf-8").splitlines():
    r=json.loads(line); text.append("سؤال: "+r["instruction"]+"\nإجابة: "+r["response"]+"\n")
corpus="".join(text)
chars=sorted(set(corpus)); stoi={c:i for i,c in enumerate(chars)}; itos=chars
x=torch.tensor([stoi[c] for c in corpus],dtype=torch.long)

class TinyLM(nn.Module):
    def __init__(self,vocab,emb=256,heads=4,layers=4,ctx=256):
        super().__init__(); self.ctx=ctx
        self.tok=nn.Embedding(vocab,emb); self.pos=nn.Embedding(ctx,emb)
        layer=nn.TransformerEncoderLayer(emb,heads,dim_feedforward=4*emb,batch_first=True)
        self.tr=nn.TransformerEncoder(layer,layers); self.out=nn.Linear(emb,vocab)
    def forward(self,z):
        n=z.size(1); p=torch.arange(n,device=z.device).unsqueeze(0)
        h=self.tok(z)+self.pos(p); mask=torch.triu(torch.ones(n,n,device=z.device),1).bool()
        return self.out(self.tr(h,mask=mask))

model=TinyLM(len(chars)); opt=torch.optim.AdamW(model.parameters(),lr=3e-4)
ctx=256; steps=min(2000,max(100,len(x)//ctx*20))
for step in range(steps):
    if len(x)<=ctx+1: break
    s=torch.randint(0,len(x)-ctx-1,(1,)).item(); inp=x[s:s+ctx].unsqueeze(0); tgt=x[s+1:s+ctx+1].unsqueeze(0)
    loss=nn.functional.cross_entropy(model(inp).reshape(-1,len(chars)),tgt.reshape(-1)); opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(),1.0); opt.step()
    if step%100==0: print(step,round(loss.item(),4))
OUT.parent.mkdir(exist_ok=True); torch.save({"state":model.state_dict(),"chars":itos,"config":{"ctx":ctx}},OUT)
print("saved",OUT)
