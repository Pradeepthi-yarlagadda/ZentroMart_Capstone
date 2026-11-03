"""Offline retrieval evaluation against practice/questions.csv."""
from pathlib import Path
import pandas as pd
from rag_engine import KnowledgeRetriever
ROOT = Path(__file__).resolve().parent
r = KnowledgeRetriever()
df = pd.read_csv(ROOT/'practice'/'questions.csv', dtype=str).fillna('')
rows=[]
for _, row in df.iterrows():
    hits = r.search(row['question'], top_k=5)
    gold = [x.strip() for x in row.get('gold_evidence','').split(' ; ') if x.strip()]
    retrieved = [h['section_id'] for h in hits]
    hit = any(g in retrieved for g in gold) if gold else None
    rows.append({'id':row['id'],'question':row['question'],'gold_evidence':';'.join(gold),'retrieved_sections':';'.join(retrieved),'evidence_hit_at_5':hit})
out = pd.DataFrame(rows)
out.to_csv(ROOT/'evaluation_results.csv', index=False)
valid = out['evidence_hit_at_5'].dropna()
print(f'Questions evaluated: {len(out)}')
print(f'Gold evidence hit@5: {valid.mean():.1%} ({valid.sum()}/{len(valid)})')
print('Detailed results: evaluation_results.csv')
