# KNOWLEDGE PROVIDER ABSTRACTION
## BATCH 19 — KNOWLEDGE GROUNDING & EVIDENCE INTELLIGENCE

### 1. Abstract Base Class (`KnowledgeProvider`)
Defines `search(query: KnowledgeQuery)`, `get_document(id)`, `get_source(id)`, and `health_check()`.

### 2. Concrete Offline Providers
- `InMemoryKnowledgeProvider`: In-memory storage with deterministic lexical token overlap search.
- `LocalDocumentKnowledgeProvider`: Parses local markdown and text knowledge files directly into documents and chunks.
- Provider abstraction is decoupled from vector databases, allowing future adapters for embeddings, web search, or academic APIs without core redesign.
