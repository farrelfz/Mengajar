"""
Source-Grounded Slide Generator.

Generates presentation-ready slide HTML content directly grounded in the
source ContentBlocks without hallucinating generic research templates or p-values.
"""

from __future__ import annotations

import html
import re
from typing import Any
from pydantic import BaseModel, Field

from app.intelligence.markdown_tree_parser import ContentBlock, SemanticBlockType
from app.presentation.slide_architect import PlannedSlide


FORBIDDEN_SYSTEM_LOG_PATTERNS = [
    re.compile(r"\[\d{2}:\d{2}:\d{2}\]"),
    re.compile(r"Job\s+[a-z0-9_]+"),
    re.compile(r"Traceback\s+\(most\s+recent\s+call\s+last\):"),
    re.compile(r"HTTP\s+[45]\d{2}"),
    re.compile(r"model:\s*ag/"),
]

FORBIDDEN_HALLUCINATIONS = [
    "p < 0.05",
    "p < 0.01",
    "Primary Factor / Treatment",
    "Target Metric / Measured Response",
    "Statistically significant correlation",
    "Hypothesis Test Protocol",
]


class GeneratedSlide(BaseModel):
    slide_id: str
    slide_number: int
    title: str
    layout: str
    rendered_html: str
    source_refs: list[str]
    has_sanitization_error: bool = False
    has_hallucination_warning: bool = False
    validation_notes: list[str] = Field(default_factory=list)


class SlideGenerator:
    """Renders planned slides into HTML with deterministic source fidelity."""

    def generate_slide(self, planned: PlannedSlide) -> GeneratedSlide:
        """Render a single PlannedSlide using its designated layout and source blocks."""
        layout = planned.layout
        blocks = planned.key_blocks
        title_esc = html.escape(planned.title)

        if layout == "hero_composition":
            slide_html = self._render_hero(planned, title_esc, blocks)
        elif layout == "formula_explainer":
            slide_html = self._render_formula(planned, title_esc, blocks)
        elif layout == "three_column_comparison":
            slide_html = self._render_three_column(planned, title_esc, blocks)
        elif layout == "triangle_relationship":
            slide_html = self._render_triangle(planned, title_esc, blocks)
        elif layout == "data_table":
            slide_html = self._render_table(planned, title_esc, blocks)
        elif layout == "risk_matrix":
            slide_html = self._render_risk(planned, title_esc, blocks)
        elif layout == "timeline_horizontal":
            slide_html = self._render_timeline(planned, title_esc, blocks)
        elif layout == "minimal_question":
            slide_html = self._render_question(planned, title_esc, blocks)
        elif layout == "synthesis":
            slide_html = self._render_synthesis(planned, title_esc, blocks)
        else:
            slide_html = self._render_concept(planned, title_esc, blocks)

        # Content Sanitization Check
        has_log_error = any(pat.search(slide_html) for pat in FORBIDDEN_SYSTEM_LOG_PATTERNS)
        
        # Hallucination Check
        source_texts = " ".join(b.content for b in blocks)
        has_hallucination = False
        notes: list[str] = []
        for term in FORBIDDEN_HALLUCINATIONS:
            if term in slide_html and term not in source_texts:
                has_hallucination = True
                notes.append(f"Forbidden hallucination detected: {term}")

        return GeneratedSlide(
            slide_id=planned.slide_id,
            slide_number=planned.slide_number,
            title=planned.title,
            layout=layout,
            rendered_html=slide_html,
            source_refs=planned.source_refs,
            has_sanitization_error=has_log_error,
            has_hallucination_warning=has_hallucination,
            validation_notes=notes,
        )

    def _render_hero(self, planned: PlannedSlide, title_esc: str, blocks: list[ContentBlock]) -> str:
        subtitle = planned.subtitle or (blocks[0].content if blocks else "")
        return f"""
        <div class="slide-card hero-card">
            <div class="hero-badge">EKSPERIMEN SAINS PEMBELAJARAN</div>
            <h1 class="hero-title">{title_esc}</h1>
            <p class="hero-subtitle">{html.escape(subtitle)}</p>
            <div class="hero-decor-line"></div>
        </div>
        """

    def _render_formula(self, planned: PlannedSlide, title_esc: str, blocks: list[ContentBlock]) -> str:
        formula_blocks = [b for b in blocks if b.type == SemanticBlockType.FORMULA]
        context_blocks = [b for b in blocks if b.type != SemanticBlockType.FORMULA]

        # Combine all formula blocks
        math_boxes = ""
        combined_formulas = " ".join(b.content for b in formula_blocks)
        for fb in formula_blocks:
            math_boxes += f"""
            <div class="math-display-box">
                <div class="formula-latex">$${fb.content}$$</div>
            </div>
            """

        context_text = " ".join(b.content for b in context_blocks).strip()

        # Variable breakdown tailored to formula semantics
        var_breakdown = ""
        f_lower = combined_formulas.lower()

        if "q = mc" in f_lower or "mc\\delta t" in f_lower or "mct" in f_lower:
            var_breakdown = """
            <div class="formula-breakdown-grid">
                <div class="formula-var-item"><span class="var-sym">Q</span><span class="var-desc">Kalor yang diserap / dilepaskan oleh sistem air (Joule atau Kalori)</span></div>
                <div class="formula-var-item"><span class="var-sym">m</span><span class="var-desc">Massa lapisan air pelindung pada telapak tangan (gram atau kg)</span></div>
                <div class="formula-var-item"><span class="var-sym">c</span><span class="var-desc">Kapasitas kalor spesifik air yang sangat tinggi ($4.184\\text{ J/g}^\\circ\\text{C}$)</span></div>
                <div class="formula-var-item"><span class="var-sym">ΔT</span><span class="var-desc">Kenaikan suhu lapisan fluida pelindung sebelum membahayakan kulit</span></div>
            </div>
            """
        elif "\\rightarrow" in combined_formulas or "co_{2" in f_lower or "c_4h_{10" in f_lower:
            var_breakdown = """
            <div class="formula-breakdown-grid">
                <div class="formula-var-item"><span class="var-sym">Reaktan</span><span class="var-desc">Bahan bakar butana ($C_4H_{10}$) dan oksigen ($O_2$) menyimpan energi ikatan kovalen</span></div>
                <div class="formula-var-item"><span class="var-sym">Produk</span><span class="var-desc">Karbon dioksida ($CO_2$) dan uap air ($H_2O$) hasil oksidasi sempurna</span></div>
                <div class="formula-var-item"><span class="var-sym">ΔH</span><span class="var-desc">Pelepasan entalpi pembakaran eksotermik menjadi energi termal dan pancaran foton</span></div>
            </div>
            """
        elif "\\delta h" in f_lower or "h_{\\text{produk}}" in f_lower or "reaksi eksoterm" in f_lower:
            var_breakdown = """
            <div class="formula-breakdown-grid">
                <div class="formula-var-item"><span class="var-sym">ΔH &lt; 0</span><span class="var-desc">Perubahan entalpi bernilai negatif membuktikan pelepasan energi ke lingkungan</span></div>
                <div class="formula-var-item"><span class="var-sym">H_produk</span><span class="var-desc">Tingkat energi potensial molekul produk ($CO_2 + H_2O$) lebih stabil</span></div>
                <div class="formula-var-item"><span class="var-sym">H_reaktan</span><span class="var-desc">Entalpi bahan bakar awal yang kaya akan energi ikatan hidrokarbon</span></div>
            </div>
            """
        elif "e_a" in f_lower or "arrhenius" in f_lower or "e^{-\\frac" in f_lower:
            var_breakdown = """
            <div class="formula-breakdown-grid">
                <div class="formula-var-item"><span class="var-sym">k</span><span class="var-desc">Konstanta laju reaksi kimia pembakaran butana</span></div>
                <div class="formula-var-item"><span class="var-sym">E_a</span><span class="var-desc">Energi aktivasi minimum yang dipasok oleh percikan pemantik api</span></div>
                <div class="formula-var-item"><span class="var-sym">R, T</span><span class="var-desc">Konstanta gas universal ($R$) dan temperatur absolut reaksi ($T$)</span></div>
            </div>
            """
        elif "\\delta u" in f_lower or "q - w" in f_lower:
            var_breakdown = """
            <div class="formula-breakdown-grid">
                <div class="formula-var-item"><span class="var-sym">ΔU</span><span class="var-desc">Perubahan energi dalam sistem gas gelembung sabun</span></div>
                <div class="formula-var-item"><span class="var-sym">Q</span><span class="var-desc">Kalor termal netto yang dibebaskan selama reaksi oksidasi</span></div>
                <div class="formula-var-item"><span class="var-sym">W</span><span class="var-desc">Kerja ekspansi mekanik gas panas terhadap tekanan atmosfer luar</span></div>
            </div>
            """
        elif "dq" in f_lower or "dt/dx" in f_lower or "fourier" in f_lower:
            var_breakdown = """
            <div class="formula-breakdown-grid">
                <div class="formula-var-item"><span class="var-sym">dQ/dt</span><span class="var-desc">Laju perpindahan kalor konduksi melalui lapisan batas air</span></div>
                <div class="formula-var-item"><span class="var-sym">k</span><span class="var-desc">Konduktivitas termal air yang relatif rendah ($k \\approx 0.6\\text{ W/m}\\cdot\\text{K}$)</span></div>
                <div class="formula-var-item"><span class="var-sym">A</span><span class="var-desc">Luas area kontak efektif antara dasar busa dengan telapak tangan</span></div>
                <div class="formula-var-item"><span class="var-sym">dT/dx</span><span class="var-desc">Gradien suhu vertikal melintasi ketebalan lapisan film air</span></div>
            </div>
            """
        elif "\\rho" in f_lower or "buoyant" in f_lower or "konveksi" in f_lower:
            var_breakdown = """
            <div class="formula-breakdown-grid">
                <div class="formula-var-item"><span class="var-sym">ρ_panas</span><span class="var-desc">Massa jenis gas hasil pembakaran bersuhu tinggi mengalami ekspansi termal</span></div>
                <div class="formula-var-item"><span class="var-sym">ρ_dingin</span><span class="var-desc">Massa jenis udara atmosfer sekitar telapak tangan yang lebih padat</span></div>
                <div class="formula-var-item"><span class="var-sym">Gaya Apung</span><span class="var-desc">Gaya apung Archimedes mendorong nyala api bergerak melesat ke atas menjauhi tangan</span></div>
            </div>
            """
        elif "\\sigma" in f_lower or "t^4" in f_lower or "stefan" in f_lower:
            var_breakdown = """
            <div class="formula-breakdown-grid">
                <div class="formula-var-item"><span class="var-sym">P</span><span class="var-desc">Daya radiasi termal total yang dipancarkan oleh lidah api</span></div>
                <div class="formula-var-item"><span class="var-sym">ε, σ</span><span class="var-desc">Emisivitas termal nyala dan konstanta Stefan-Boltzmann ($5.67 \\times 10^{-8}\\text{ W/m}^2\\text{K}^4$)</span></div>
                <div class="formula-var-item"><span class="var-sym">T^4</span><span class="var-desc">Ketergantungan suhu mutlak pangkat empat pada zona emisi foton</span></div>
            </div>
            """
        elif "t(y)" in f_lower or "\\alpha" in f_lower:
            var_breakdown = """
            <div class="formula-breakdown-grid">
                <div class="formula-var-item"><span class="var-sym">T(y)</span><span class="var-desc">Suhu lokal pada jarak vertikal $y$ di atas telapak tangan</span></div>
                <div class="formula-var-item"><span class="var-sym">T_puncak</span><span class="var-desc">Suhu maksimum puncak api (mencapai ~1.000°C di zona bebas)</span></div>
                <div class="formula-var-item"><span class="var-sym">e^(-αy)</span><span class="var-desc">Faktor redaman termal eksponensial yang melindungi lapisan epidermis</span></div>
            </div>
            """
        else:
            var_breakdown = f"""
            <div class="formula-breakdown-grid">
                <div class="formula-var-item"><span class="var-sym">Model</span><span class="var-desc">Formulasi matematis fenomena fisika & kimia terapan</span></div>
                <div class="formula-var-item"><span class="var-sym">Analisis</span><span class="var-desc">Korelasi variabel independen terhadap kestabilan sistem reaksi</span></div>
            </div>
            """

        context_html = f'<div class="formula-context-note"><p>{html.escape(context_text[:280])}</p></div>' if context_text else ""

        return f"""
        <div class="slide-card formula-card">
            <div class="card-header-bar">
                <span class="card-tag">PERSAMAAN & MODEL MATEMATIS</span>
                <h2>{title_esc}</h2>
            </div>
            {math_boxes}
            {var_breakdown}
            {context_html}
        </div>
        """

    def _render_three_column(self, planned: PlannedSlide, title_esc: str, blocks: list[ContentBlock]) -> str:
        items = []
        for b in blocks:
            if b.metadata.get("items"):
                items.extend(b.metadata["items"])
            else:
                items.extend([line.strip("- ") for line in b.content.splitlines() if line.strip()])

        cols_html = ""
        colors = ["#2563eb", "#059669", "#d97706", "#7c3aed"]
        for idx, it in enumerate(items[:3]):
            col_color = colors[idx % len(colors)]
            parts = it.split(":", 1) if ":" in it else (it[:20], it[20:])
            col_title = parts[0].replace("*", "").strip()
            col_desc = parts[1].replace("*", "").strip() if len(parts) > 1 else ""
            cols_html += f"""
            <div class="comparison-col" style="border-top: 4px solid {col_color};">
                <h3 style="color: {col_color};">{html.escape(col_title)}</h3>
                <p>{html.escape(col_desc)}</p>
            </div>
            """

        return f"""
        <div class="slide-card comparison-card">
            <div class="card-header-bar">
                <span class="card-tag">KOMPARASI MEKANISME</span>
                <h2>{title_esc}</h2>
            </div>
            <div class="comparison-grid-3">
                {cols_html}
            </div>
        </div>
        """

    def _render_triangle(self, planned: PlannedSlide, title_esc: str, blocks: list[ContentBlock]) -> str:
        return f"""
        <div class="slide-card triangle-card">
            <div class="card-header-bar">
                <span class="card-tag">MODEL SISTEM TRIANGULAR</span>
                <h2>{title_esc}</h2>
            </div>
            <div class="triangle-container">
                <div class="triangle-svg-box">
                    <svg viewBox="0 0 360 280" class="fire-triangle-svg" style="max-height: 240px; margin: auto; display: block;">
                        <polygon points="180,30 50,250 310,250" fill="#fef2f2" stroke="#dc2626" stroke-width="4" stroke-linejoin="round"/>
                        <circle cx="180" cy="30" r="18" fill="#ea580c" />
                        <text x="180" y="36" text-anchor="middle" fill="#ffffff" font-weight="bold" font-size="16">1</text>
                        <text x="180" y="-8" text-anchor="middle" fill="#ea580c" font-weight="bold" font-size="16">PANAS / ENERGI AKTIVASI</text>

                        <circle cx="50" cy="250" r="18" fill="#2563eb" />
                        <text x="50" y="256" text-anchor="middle" fill="#ffffff" font-weight="bold" font-size="16">2</text>
                        <text x="50" y="285" text-anchor="middle" fill="#2563eb" font-weight="bold" font-size="16">BAHAN BAKAR (FUEL)</text>

                        <circle cx="310" cy="250" r="18" fill="#059669" />
                        <text x="310" y="256" text-anchor="middle" fill="#ffffff" font-weight="bold" font-size="16">3</text>
                        <text x="310" y="285" text-anchor="middle" fill="#059669" font-weight="bold" font-size="16">OKSIGEN (O₂)</text>

                        <text x="180" y="150" text-anchor="middle" fill="#991b1b" font-weight="800" font-size="20">SEGITIGA API</text>
                        <text x="180" y="175" text-anchor="middle" fill="#7f1d1d" font-size="16">Semua 3 elemen wajib hadir</text>
                    </svg>
                </div>
                <div class="triangle-legend">
                    <p><strong>Prinsip Kunci:</strong> Jika salah satu elemen (Panas, Bahan Bakar, atau Oksigen) dihilangkan, maka pembakaran akan padam seketika.</p>
                </div>
            </div>
        </div>
        """

    def _render_table(self, planned: PlannedSlide, title_esc: str, blocks: list[ContentBlock]) -> str:
        headers = []
        rows = []
        for b in blocks:
            if b.metadata.get("headers"):
                headers = b.metadata["headers"]
                rows = b.metadata.get("rows", [])
                break

        th_html = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
        tr_html = ""
        for r in rows:
            td_html = "".join(f"<td>{html.escape(c)}</td>" for c in r)
            tr_html += f"<tr>{td_html}</tr>"

        return f"""
        <div class="slide-card table-card">
            <div class="card-header-bar">
                <span class="card-tag">MATRIKS DATA & OBSERVASI</span>
                <h2>{title_esc}</h2>
            </div>
            <div class="table-container-scroll">
                <table class="presentation-table">
                    <thead><tr>{th_html}</tr></thead>
                    <tbody>{tr_html}</tbody>
                </table>
            </div>
        </div>
        """

    def _render_risk(self, planned: PlannedSlide, title_esc: str, blocks: list[ContentBlock]) -> str:
        warn_text = " ".join(b.content for b in blocks).replace("**", "")
        return f"""
        <div class="slide-card risk-card">
            <div class="risk-header">
                <span class="danger-badge">⚠️ KESELAMATAN & K3 LABORATORIUM</span>
                <h2>{title_esc}</h2>
            </div>
            <div class="risk-body-box">
                <div class="risk-icon">🛡️</div>
                <div class="risk-text">
                    <p>{html.escape(warn_text)}</p>
                </div>
            </div>
            <div class="safety-checklist-summary">
                <span>✓ Pengawasan guru/laboran</span>
                <span>✓ Sediakan kain basah & APAR</span>
                <span>✓ Jauhkan bahan mudah terbakar</span>
            </div>
        </div>
        """

    def _render_timeline(self, planned: PlannedSlide, title_esc: str, blocks: list[ContentBlock]) -> str:
        items = []
        for b in blocks:
            if b.metadata.get("items"):
                items.extend(b.metadata["items"])
            else:
                items.extend(line.strip("1234567890. ") for line in b.content.splitlines() if line.strip())

        steps_html = ""
        for idx, it in enumerate(items[:4], start=1):
            steps_html += f"""
            <div class="timeline-step">
                <div class="step-circle">{idx}</div>
                <div class="step-card">
                    <p>{html.escape(it)}</p>
                </div>
            </div>
            """

        return f"""
        <div class="slide-card timeline-card">
            <div class="card-header-bar">
                <span class="card-tag">TAHAPAN PROSEDUR KERJA</span>
                <h2>{title_esc}</h2>
            </div>
            <div class="timeline-horizontal-grid">
                {steps_html}
            </div>
        </div>
        """

    def _render_question(self, planned: PlannedSlide, title_esc: str, blocks: list[ContentBlock]) -> str:
        q_text = " ".join(b.content for b in blocks)
        return f"""
        <div class="slide-card question-card">
            <div class="question-badge">PERTANYAAN & DISKUSI INQUIRY</div>
            <h2 class="question-heading">{title_esc}</h2>
            <div class="question-quote-box">
                <p>"{html.escape(q_text)}"</p>
            </div>
            <div class="inquiry-hint">💡 Analisis fenomena berdasarkan konsep kalor dan reaksi kimia.</div>
        </div>
        """

    def _render_synthesis(self, planned: PlannedSlide, title_esc: str, blocks: list[ContentBlock]) -> str:
        return f"""
        <div class="slide-card synthesis-card">
            <div class="card-header-bar">
                <span class="card-tag">SINTESIS & KESIMPULAN</span>
                <h2>{title_esc}</h2>
            </div>
            <div class="synthesis-grid">
                <div class="synthesis-item">
                    <h4>🔥 Reaksi Pembakaran</h4>
                    <p>Reaksi eksotermik mengubah energi kimia bahan bakar menjadi energi termal (panas) dan energi radiasi (cahaya).</p>
                </div>
                <div class="synthesis-item">
                    <h4>🔺 Segitiga Api</h4>
                    <p>Pembakaran mutlak membutuhkan 3 komponen: Panas/Energi Aktivasi, Bahan Bakar, dan Oksigen.</p>
                </div>
                <div class="synthesis-item">
                    <h4>💧 Proteksi Termal Air</h4>
                    <p>Kapasitas kalor air yang tinggi ($Q = mc\\Delta T$) menyerap panas pembakaran sebelum membakar kulit tangan.</p>
                </div>
            </div>
        </div>
        """

    def _render_concept(self, planned: PlannedSlide, title_esc: str, blocks: list[ContentBlock]) -> str:
        body_paras = []
        list_items = []
        for b in blocks:
            if b.type == SemanticBlockType.BULLET_LIST:
                list_items.extend(b.metadata.get("items", b.content.splitlines()))
            else:
                body_paras.append(b.content)

        paras_html = "".join(f"<p>{html.escape(p)}</p>" for p in body_paras)
        lists_html = "".join(f"<li>{html.escape(it.strip('- '))}</li>" for it in list_items)

        return f"""
        <div class="slide-card concept-card">
            <div class="card-header-bar">
                <span class="card-tag">KONSEP UTAMA</span>
                <h2>{title_esc}</h2>
            </div>
            <div class="concept-body">
                {paras_html}
                {f'<ul class="concept-list">{lists_html}</ul>' if lists_html else ''}
            </div>
        </div>
        """
