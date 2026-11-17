"""Mudança de vocabulário entre relato e síntese de V-B (condição principal, 198 perfis).
Usa o mesmo tokenizador de src/tcc/common.py (content_words)."""
import json, re, sys, itertools, statistics as st
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

def content_words(text):
    return [t for t in re.findall(r"[a-z]+", text.lower()) if len(t) >= 3 and t not in ENGLISH_STOP_WORDS]

gen = sys.argv[1]
rel = {}
for l in open(f"{gen}/relatos.jsonl", encoding="utf8"):
    d = json.loads(l)
    if d.get("set") == "eval": rel[d["profile_id"]] = d["relato"]
sin = {}
for l in open(f"{gen}/sinteses_main.jsonl", encoding="utf8"):
    d = json.loads(l); sin[d["profile_id"]] = d["sintese"]
ids = sorted(set(rel) & set(sin))
print("perfis:", len(ids), "relatos eval:", len(rel), "sinteses:", len(sin))
R = {i: content_words(rel[i]) for i in ids}; Sx = {i: content_words(sin[i]) for i in ids}
surv = [len(set(R[i]) & set(Sx[i])) / len(set(R[i])) for i in ids]
print("sobrevivência média (tipos do relato presentes na síntese): %.4f  mediana %.4f" % (st.mean(surv), st.median(surv)))
def jac(a, b): a, b = set(a), set(b); return len(a & b) / len(a | b)
jr = [jac(R[a], R[b]) for a, b in itertools.combinations(ids, 2)]
js = [jac(Sx[a], Sx[b]) for a, b in itertools.combinations(ids, 2)]
print("pares:", len(jr))
print("Jaccard médio entre perfis diferentes: relatos %.4f  sínteses %.4f  razão %.2f" % (st.mean(jr), st.mean(js), st.mean(js)/st.mean(jr)))
print("palavras de conteúdo por texto (média): relatos %.2f  sínteses %.2f" % (st.mean(len(R[i]) for i in ids), st.mean(len(Sx[i]) for i in ids)))
print("vocabulário distinto total: relatos %d  sínteses %d" % (len(set().union(*map(set, R.values()))), len(set().union(*map(set, Sx.values())))))
print("palavras de conteúdo distintas por texto (média): relatos %.2f  sínteses %.2f" % (st.mean(len(set(R[i])) for i in ids), st.mean(len(set(Sx[i])) for i in ids)))
