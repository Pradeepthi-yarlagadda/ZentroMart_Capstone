"""Conversation orchestration, identity verification and ticket escalation."""
from pathlib import Path
import sys, re
import pandas as pd
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools'))
from tools import lookup_order, create_ticket
from rag_engine import KnowledgeRetriever, detect_intent

retriever = KnowledgeRetriever()
DATA = ROOT / 'data'


def grounded_reply(question, history=None):
    intent = detect_intent(question)
    hits = retriever.search(question, top_k=4)
    if not hits or hits[0]['score'] < 0.035:
        return ('I could not find a sufficiently reliable answer in the current ZentroMart knowledge base. '
                'I can create a support ticket for a human colleague to review.'), intent, []
    # Conservative extractive response: do not invent policy details.
    best = hits[:3]
    excerpts = []
    for h in best:
        text = h['text']
        # keep section heading and concise relevant body
        lines = [x.strip() for x in text.splitlines() if x.strip() and not x.strip().startswith('#')]
        excerpts.append(' '.join(lines)[:650])
    reply = 'Here is what I found in ZentroMart’s current guidance:\n\n' + '\n\n'.join(excerpts)
    reply += '\n\nIf this is about a specific order, please verify your identity before sharing or requesting order details.'
    return reply, intent, best


def verify_order(order_id, verification_value):
    return lookup_order(order_id, verification_value=verification_value)


def make_handover(summary, order_id=None, reason=None, intent=None):
    return create_ticket(summary=summary, order_id=order_id, reason=reason, intent=intent)


def search_product(query, limit=5):
    df = pd.read_csv(DATA / 'products.csv', dtype=str).fillna('')
    q = query.lower()
    mask = df.apply(lambda row: q in ' '.join(row.astype(str)).lower(), axis=1)
    return df[mask].head(limit).to_dict('records')
