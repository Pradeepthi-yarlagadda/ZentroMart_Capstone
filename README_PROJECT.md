# ZentroMart — AI Customer Support Agent

## Project overview
A Python-based customer-support prototype for a fictional Indian e-commerce store. It combines a retrieval-augmented knowledge search (RAG-style retrieval), intent detection, a synthetic order-lookup tool with identity verification, catalogue search, and human ticket handover.

## Features
- Searches current company knowledge-base sections with TF-IDF word and character n-grams.
- Excludes superseded documents from retrieval.
- Shows section IDs and source filenames for traceability.
- Detects common support intents (returns, refunds, cancellations, delivery, payments, damaged items and human handover).
- Uses the supplied mock order tool; order data is only displayed after phone-suffix or delivery-pincode verification.
- Enforces at most one retry in the Streamlit session.
- Creates human handover tickets using the supplied tool.
- Searches the product catalogue.
- Includes an offline evaluation script using practice/questions.csv.

## Run locally (VS Code or terminal)
1. Extract this project folder.
2. Open a terminal in the project folder.
3. Create and activate a virtual environment:
   - Windows: `py -m venv .venv` then `.venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
4. Install packages: `pip install -r requirements.txt`
5. Validate the original dataset rules: `python validate_dataset.py` (if the validator is included in your extracted source folder; otherwise use the supplied original ZIP validator).
6. Start the app: `streamlit run app.py`
7. In a second terminal, evaluate retrieval: `python evaluate.py`.

## Google Colab
Upload/extract the project ZIP, install dependencies with `!pip install -r requirements.txt`, then run `!python evaluate.py`. Streamlit is best run locally; in Colab you can test the retrieval and agent modules in notebook cells.

## How RAG works here
1. Each Markdown knowledge-base section is loaded as a separate chunk.
2. Front matter metadata and section IDs are retained.
3. Superseded policy documents are excluded.
4. TF-IDF word and character features are calculated.
5. A weighted cosine-similarity score ranks relevant chunks for a user question.
6. The UI displays retrieved evidence so a human can inspect the source. The baseline response is deliberately conservative and extractive; it does not claim to be an LLM-generated answer.

## Important limitations
- This is an educational prototype using synthetic data, not a production customer-service system.
- The supplied verification tool simulates identity checks and is not secure authentication.
- Retrieval is a lightweight lexical baseline, not a transformer embedding model. It can miss paraphrases and multilingual queries. Upgrade by using a multilingual embedding model and a vector database, then evaluate against the supplied gold evidence.
- The prototype does not include the optional Gnani speech-to-text/text-to-speech integration because no API credentials or audio samples were supplied.
- The fixed dataset reference date is 20 October 2026. Use this date for policy and deadline calculations.

## Suggested next improvements
- Replace TF-IDF with multilingual sentence-transformer embeddings and FAISS/Chroma.
- Add a configured LLM with a strict prompt requiring answers only from retrieved evidence and refusal when evidence is insufficient.
- Add automated tests for verification, policy precedence, escalation triggers and business-day calculations.
- Add voice input/output using the provider credentials specified by the course brief.

## Dataset
All customer, order, product and support data are synthetic and provided solely for this educational capstone.
