# KIR AI Document Intelligence

A local-first Python document intelligence system that transforms raw materials into high-quality educational and research PDF artifacts.

## Repository Execution Safety Guideline

> **Important Rule for Developers & AI Agents:**
> "Never use unrestricted recursive glob/rglob from repository root in this project unless there is an explicit justification. The repository may contain large virtual environments, dependency trees, caches, and generated artifacts. Recursive scans must either target a known directory or prune excluded directories before traversal."

### Safe File Discovery
Always use `app.utils.file_discovery.find_files` to prevent recursive traversal into `venv/`, `.git/`, or `node_modules/`:
```python
from app.utils.file_discovery import find_files

# Finds files while pruning venv, .git, etc. before entering:
pdfs = find_files("outputs", patterns="*.pdf")
```

### Inspecting PDFs
To safely inspect page counts and dimensions across generated PDFs:
```bash
PYTHONPATH=. venv/bin/python scripts/inspect_pdfs.py outputs
```
