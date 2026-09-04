# 07 — Catalog & Discovery API

## Machine-Readable Catalog API (`CapabilityCatalog`)

The system provides a programmatic discovery interface in `app/libraries/catalog.py`:

```python
from app.libraries.catalog import CapabilityCatalog
from app.capabilities.taxonomy import CapabilityFamily, SemanticIntent

catalog = CapabilityCatalog()

# 1. Discover all domains
domains = catalog.list_domains()
# ['academic_writing', 'data_literacy', 'experiment_design', 'general', 'pedagogy', 'physics', 'presentation', 'research_education', 'scientific_thinking']

# 2. Filter capabilities by domain
writing_caps = catalog.list_capabilities(domain="academic_writing")

# 3. Find capabilities by semantic intent
comparison_caps = catalog.find_by_intent(SemanticIntent.COMPARE)

# 4. Find capabilities by family
process_caps = catalog.find_by_family(CapabilityFamily.PROCESS_VISUALIZATION)

# 5. Ecosystem statistical summary
summary = catalog.get_summary()
```

---

## Performance Characteristics
- In-memory indexing using dictionary lookups and multi-axis inverted indexes.
- Benchmark: 1,000 queries complete in **<25ms** (<0.025 ms per query).
