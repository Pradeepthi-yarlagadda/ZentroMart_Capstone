# ZentroMart: AI Customer Support Agent

## Abstract
This project develops an educational AI customer-support assistant for ZentroMart, a fictional Indian e-commerce company. The prototype retrieves relevant sections from company knowledge documents, classifies common support intents, performs identity-gated synthetic order lookups, searches a product catalogue and creates human-handover tickets. The implementation prioritizes traceability and privacy by showing source section IDs and withholding order details until verification succeeds.

## Problem statement
Customers frequently ask repetitive questions about order tracking, returns, refunds, cancellations, payments and product issues. A support assistant must find the applicable current policy, avoid using superseded guidance, protect order-specific information and escalate cases that require human judgment.

## Objectives
1. Build a searchable knowledge base from Markdown policy and help documents.
2. Retrieve relevant evidence for natural-language questions.
3. Detect common customer-support intents.
4. Protect order information using the supplied verification workflow.
5. Support human escalation through ticket creation.
6. Evaluate retrieval against the supplied practice questions.

## Dataset
The supplied synthetic dataset includes 300 customers, 1,000 orders, 1,783 order-item rows, 70 products, 36 pincode records, 4 holidays, 244 support logs, 21 knowledge documents, 52 practice questions and 23 multi-turn practice conversations. The dataset's fixed reference date is 20 October 2026. No real customer records are used.

## Methodology
Knowledge documents are parsed into heading-based chunks. Each chunk retains its section ID, filename, document type, status and effective date. Superseded documents are excluded. TF-IDF word bigrams and character n-grams are used to represent the chunks and query. Cosine similarity is combined using a 0.65 word-feature and 0.35 character-feature weighting. The highest-ranked evidence chunks are returned with their source IDs.

Intent detection uses a transparent keyword baseline for common support categories. The order lookup function from the supplied tools is called only after the customer provides an order ID and then a phone suffix or delivery pincode. The Streamlit interface allows one retry and does not display order data after failed verification. Ticket creation uses the supplied mock ticket tool and reports success only when the tool confirms creation.

## System architecture
Customer message → intent detection → knowledge retrieval → ranked policy/help evidence → grounded response with source IDs. For order-specific requests, the agent additionally uses the verification-gated order tool. Cases requiring human review are passed to the ticket-creation tool.

## Implementation
- Python: application logic and orchestration.
- Pandas: catalogue and dataset handling.
- Scikit-learn: TF-IDF vectorization and cosine similarity.
- Streamlit: interactive web interface.
- Supplied local tools: verified order lookup and ticket creation.

## Evaluation plan
Run `python evaluate.py` to retrieve the top five evidence sections for every question in `practice/questions.csv`. The script records whether any expected gold evidence section appears in the top five and writes `evaluation_results.csv`. The first local run retrieved at least one expected gold evidence section in the top five for 33 of 47 questions with a populated gold-evidence field, giving a hit@5 of 70.2%. Five questions had no gold evidence label and were excluded from this denominator. This is a retrieval metric, not an answer-accuracy score. Further evaluation should assess answer correctness, required facts, prohibited claims, verification behaviour and escalation decisions against the practice conversations.

## Results and discussion
The prototype provides a reproducible retrieval baseline and visible source traceability. Word features capture direct terminology, while character n-grams provide limited robustness to spelling variation. Keyword intent detection is simple and explainable but is not a trained classifier. The extractive answer strategy reduces unsupported generation but may produce less natural responses than a properly grounded LLM.

## Limitations
This is not a production deployment. TF-IDF is not semantic transformer retrieval; Hindi/Hinglish performance is limited. The mock identity check is educational only. No live LLM or voice provider is configured because API credentials were not supplied. The supplied synthetic data must not be treated as real customer data.

## Conclusion
ZentroMart demonstrates the core components of a retrieval-grounded customer-support agent: knowledge ingestion, evidence retrieval, intent routing, identity-gated order access and human handover. Future work can add multilingual sentence embeddings, a vector database, a carefully constrained LLM, automated policy tests and the optional voice interface.
