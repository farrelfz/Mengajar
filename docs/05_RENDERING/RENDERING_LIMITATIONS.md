# RENDERING LIMITATIONS

## 1. Current Constraints
While the Hybrid Rendering Pipeline works effectively, certain limitations must be acknowledged:

### A. Playwright Overhead
Launching a headless Chromium instance for every document adds significant overhead. If a batch of hundreds of documents is requested, the system will need a persistent Playwright browser pool rather than launching and tearing down the browser context per composition.

### B. Matplotlib Fonts
Matplotlib generates SVG charts. While we enforce design tokens and `#hex` colors, ensuring Matplotlib's generated font perfectly matches the Jinja HTML font (e.g., `Inter` or `Helvetica`) across operating systems requires more rigorous font provisioning or explicit CSS overrides.

### C. ReportLab SVG Complexity
ReportLab successfully generates basic vector diagrams. However, implementing deeply complex flowcharts (like a 30-node nested process flow) might break layout boundaries. For extreme diagrams, a dedicated layout engine (like Graphviz) might be required in the future.

### D. CSS Page Breaks
Currently, `page-break-after: always` controls standard layout. If a specific paragraph overflows the exact physical dimension of A4, Playwright pushes the remainder to an unstyled blank page. A sophisticated Javascript-based polyfill (like Paged.js) could intercept overflows and auto-generate new styled wrapper regions, but for now we rely on Batch 4 Composition ensuring strict density limits before rendering.
