"""Lightweight Arabic text normalization for the local Minhaj AI."""
import re

_DIACRITICS = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")

def normalize(text: str) -> str:
    text = str(text or "").strip().lower()
    text = _DIACRITICS.sub("", text)
    table = str.maketrans({"أ":"ا", "إ":"ا", "آ":"ا", "ى":"ي", "ة":"ه", "ؤ":"و", "ئ":"ي"})
    text = text.translate(table)
    text = re.sub(r"[^\w\s؟?.,:؛;()+\-*/=]", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()

def tokens(text: str):
    return normalize(text).split()
