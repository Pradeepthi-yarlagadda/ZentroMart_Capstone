"""Grounded retrieval for ZentroMart. Uses TF-IDF word + character n-grams."""
from pathlib import Path
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parent
KB_DIR = ROOT / "kb"


def parse_frontmatter(raw):
    meta = {}
    if raw.startswith('---'):
        parts = raw.split('---', 2)
        if len(parts) == 3:
            for line in parts[1].splitlines():
                if ':' in line:
                    k, v = line.split(':', 1)
                    meta[k.strip()] = v.strip()
            return meta, parts[2].strip()
    return meta, raw


def load_chunks():
    chunks = []
    for path in sorted(KB_DIR.glob('*.md')):
        raw = path.read_text(encoding='utf-8')
        meta, body = parse_frontmatter(raw)
        # Superseded documents are deliberately excluded from authoritative retrieval.
        if meta.get('status', '').lower() == 'superseded':
            continue
        sections = re.split(r'(?=^#{1,3} \[)', body, flags=re.M)
        for section in sections:
            section = section.strip()
            if len(section) < 25:
                continue
            match = re.search(r'\[([A-Z0-9._-]+)\]', section)
            section_id = match.group(1) if match else 'DOC-INTRO'
            title = re.search(r'^#{1,3} (.+)$', section, flags=re.M)
            chunks.append({
                'text': section,
                'section_id': section_id,
                'title': title.group(1) if title else path.stem,
                'file': path.name,
                'doc_type': meta.get('doc_type', 'unknown'),
                'status': meta.get('status', 'unknown'),
                'effective_from': meta.get('effective_from', '')
            })
    return chunks


class KnowledgeRetriever:
    def __init__(self):
        self.chunks = load_chunks()
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, strip_accents='unicode', stop_words='english')
        self.word_matrix = self.vectorizer.fit_transform([c['text'] for c in self.chunks])
        self.char_vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), min_df=1, sublinear_tf=True)
        self.char_matrix = self.char_vectorizer.fit_transform([c['text'] for c in self.chunks])

    def search(self, query, top_k=4):
        q1 = self.vectorizer.transform([query])
        q2 = self.char_vectorizer.transform([query])
        scores = 0.65*cosine_similarity(q1, self.word_matrix)[0] + 0.35*cosine_similarity(q2, self.char_matrix)[0]
        ranked = scores.argsort()[::-1][:top_k]
        return [{**self.chunks[i], 'score': float(scores[i])} for i in ranked if scores[i] > 0]


def detect_intent(text):
    t = text.lower()
    rules = {
        'order_tracking': ['where is my order', 'track my order', 'order status', 'delivery status', 'order kaha', 'mera order'],
        'return': ['return', 'send it back', 'wapis', 'wapas'],
        'refund': ['refund', 'money back', 'paise', 'rrn'],
        'cancellation': ['cancel', 'cancellation'],
        'damaged_wrong_item': ['damaged', 'broken', 'defective', 'wrong item', 'missing item'],
        'payment': ['payment', 'cod', 'cash on delivery', 'upi'],
        'human_handover': ['human', 'agent', 'representative', 'person', 'talk to someone']
    }
    for intent, terms in rules.items():
        if any(term in t for term in terms):
            return intent
    return 'general_query'
