"""
app/cli/kir_cli.py — CLI `kir` untuk Karya Ilmiah Remaja / KTI.

Target pengguna: peserta KIR, peneliti pelajar, mahasiswa yang menulis karya ilmiah.
Warna aksen  : Ungu #7c3aed
Format output: KTI Document, Research Presentation, Scientific Poster, One-Page Summary
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import questionary
from questionary import Style as QStyle
from rich.align import Align
from rich.columns import Columns
from rich.panel import Panel
from rich.text import Text

from app.cli.shared import (
    AUDIENCE_CHOICES,
    DOMAIN_CHOICES,
    cmd_ai_router_menu,
    cmd_doctor,
    cmd_router_benchmark,
    cmd_router_dashboard,
    cmd_router_models,
    cmd_router_start,
    cmd_router_status,
    cmd_router_test,
    cmd_web,
    console,
    err,
    info,
    print_banner,
    print_rule,
    resolve_user_path,
    run_pipeline,
    show_job_summary,
    wizard_audience,
    wizard_domain,
    wizard_input_file,
    wizard_output_dir,
    wizard_quality,
)

# ─────────────────────────────────────────────────────────────
# Identity
# ─────────────────────────────────────────────────────────────
ACCENT = "#7c3aed"
ACCENT_DIM = "#a78bfa"

KIR_BANNER = r"""
 ██╗  ██╗██╗██████╗      █████╗ ██╗
 ██║ ██╔╝██║██╔══██╗    ██╔══██╗██║
 █████╔╝ ██║██████╔╝    ███████║██║
 ██╔═██╗ ██║██╔══██╗    ██╔══██║██║
 ██║  ██╗██║██║  ██║    ██║  ██║██║
 ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝
"""
SUBTITLE = "Karya Ilmiah Remaja — Document Intelligence  ·  v0.2.0"

# ─────────────────────────────────────────────────────────────
# Questionary style (purple)
# ─────────────────────────────────────────────────────────────
STYLE = QStyle(
    [
        ("qmark",       "fg:#7c3aed bold"),
        ("question",    "bold"),
        ("answer",      "fg:#10b981 bold"),
        ("pointer",     "fg:#7c3aed bold"),
        ("highlighted", "fg:#7c3aed bold"),
        ("selected",    "fg:#10b981"),
        ("separator",   "fg:#555555"),
        ("instruction", "fg:#888888"),
        ("text",        ""),
        ("disabled",    "fg:#858585 italic"),
    ]
)

# ─────────────────────────────────────────────────────────────
# Output modes specific to KIR / KTI
# ─────────────────────────────────────────────────────────────
KIR_MODES: list[dict] = [
    {
        "label":    "📋  KTI Document  —  Full Paper A4 (formal karya ilmiah)",
        "artifact": "kti_document",
        "format":   "kti-a4-portrait",
    },
    {
        "label":    "📊  Research Presentation 16:9  —  Slide seminar/sidang",
        "artifact": "research_presentation",
        "format":   "presentation-16-9",
    },
    {
        "label":    "🗞   Scientific Poster A1  —  Poster pameran ilmiah",
        "artifact": "scientific_poster",
        "format":   "poster-a1",
    },
    {
        "label":    "📄  One-Page Summary  —  Abstrak & ringkasan eksekutif",
        "artifact": "one_page_summary",
        "format":   "summary-a4",
    },
]

MODE_MAP = {m["label"]: m for m in KIR_MODES}


# ─────────────────────────────────────────────────────────────
# Info cards
# ─────────────────────────────────────────────────────────────

def _show_info_cards() -> None:
    cards = Columns(
        [
            Panel(
                "[bold #10b981]Analisis Konten[/]\nAI membaca & menyusun\nstruktur karya ilmiah",
                border_style="#10b981", padding=(0, 2),
            ),
            Panel(
                "[bold #7c3aed]Blueprint KTI[/]\nSkema JSON ketat —\nbukan HTML mentah",
                border_style="#7c3aed", padding=(0, 2),
            ),
            Panel(
                "[bold #f59e0b]Render Presisi[/]\nJinja2 + Playwright →\nPDF siap cetak/sidang",
                border_style="#f59e0b", padding=(0, 2),
            ),
        ],
        equal=True,
        expand=True,
    )
    console.print(cards)
    console.print()


# ─────────────────────────────────────────────────────────────
# Generate command
# ─────────────────────────────────────────────────────────────

def cmd_generate(
    input_file: str | None = None,
    mode_key: str | None = None,
    output_dir: str = "outputs",
    domain: str | None = None,
    audience: str | None = None,
    enable_quality: bool = True,
    model: str | None = None,
) -> None:
    print_rule("Generate Dokumen KTI / Karya Ilmiah", ACCENT)
    console.print()

    # ── Input file ───────────────────────────────────────────
    if input_file:
        input_path = resolve_user_path(input_file)
        if not input_path.exists():
            err(f"File '{input_file}' tidak ditemukan (mencari di: {input_path}).")
            return
    else:
        input_path = wizard_input_file(STYLE, accent=ACCENT)
        if not input_path:
            return

    # ── Output mode ──────────────────────────────────────────
    if mode_key and any(mode_key == m["artifact"] or mode_key == m["format"] for m in KIR_MODES):
        selected_mode = next(m for m in KIR_MODES if mode_key in (m["artifact"], m["format"]))
    else:
        choice = questionary.select(
            "Format output KTI:",
            choices=[m["label"] for m in KIR_MODES],
            style=STYLE,
        ).ask()
        if choice is None:
            return
        selected_mode = MODE_MAP[choice]

    # ── Domain ───────────────────────────────────────────────
    selected_domain = domain if (domain and domain in DOMAIN_CHOICES) else (
        wizard_domain(STYLE) if not input_file else "Research Methodology"
    )
    if not selected_domain:
        return

    # ── Audience ─────────────────────────────────────────────
    selected_audience = audience if (audience and audience in AUDIENCE_CHOICES) else (
        wizard_audience(STYLE) if not input_file else "High School"
    )
    if not selected_audience:
        return

    # ── Output dir ───────────────────────────────────────────
    if not output_dir or output_dir == "outputs":
        out = wizard_output_dir(STYLE, default="outputs/kir") if not input_file else "outputs/kir"
        if not out:
            return
        output_dir = out

    # ── Quality eval ─────────────────────────────────────────
    if input_file is None:
        q = wizard_quality(STYLE)
        if q is None:
            return
        enable_quality = q

    # ── Summary ──────────────────────────────────────────────
    show_job_summary(
        input_path, selected_mode["label"], selected_domain,
        selected_audience, output_dir, enable_quality, ACCENT,
        model=model,
    )

    if input_file is None:
        go = questionary.confirm("Mulai generate?", default=True, style=STYLE).ask()
        if not go:
            info("Dibatalkan.", ACCENT)
            return

    # ── Run ───────────────────────────────────────────────────
    run_pipeline(
        input_path=input_path,
        target_artifact_str=selected_mode["artifact"],
        target_format=selected_mode["format"],
        output_dir=output_dir,
        domain_str=selected_domain,
        audience_str=selected_audience,
        enable_quality=enable_quality,
        accent=ACCENT,
        model=model,
    )


# ─────────────────────────────────────────────────────────────
# Plan command
# ─────────────────────────────────────────────────────────────

def cmd_plan() -> None:
    print_rule("Plan — Blueprint JSON Saja", ACCENT)
    console.print()
    info("Hanya fase Intelligence yang dijalankan. Tidak ada PDF yang dihasilkan.", ACCENT)
    console.print()
    input_path = wizard_input_file(STYLE, accent=ACCENT)
    if not input_path:
        return
    domain = wizard_domain(STYLE)
    if not domain:
        return
    console.print()
    from app.cli.shared import warn
    warn("Plan-only mode belum tersambung penuh ke skip-rendering.")
    info("Gunakan [bold]kir generate[/bold] untuk menghasilkan artefak penuh.", ACCENT)
    console.print()


# ─────────────────────────────────────────────────────────────
# Main interactive loop
# ─────────────────────────────────────────────────────────────

COMMANDS: dict[str, object] = {
    "⚡  Generate KTI / Karya Ilmiah  —  full pipeline → PDF": cmd_generate,
    "🎨  Web Studio UI  —  Buka Web Dashboard lokal di port 20129": lambda: cmd_web(accent=ACCENT),
    "🤖  AI Router & Models  —  status, benchmark, & model 9Router": lambda: cmd_ai_router_menu(ACCENT, STYLE),
    "🗺   Plan saja  —  Blueprint JSON, tanpa rendering":        cmd_plan,
    "🩺  Doctor  —  cek environment & 9Router gateway":          cmd_doctor,
    "🚪  Keluar": None,
}


def main_kir() -> None:
    """Entry point for the `kir` CLI."""
    parser = argparse.ArgumentParser(prog="kir", description="KIR — Karya Ilmiah Remaja CLI",
                                     add_help=False)
    parser.add_argument("-h", "--help", action="store_true")
    sub = parser.add_subparsers(dest="subcmd")

    web_p = sub.add_parser("web", help="Jalankan Web Dashboard Studio lokal di port 20129")
    web_p.add_argument("-p", "--port", type=int, default=20129, help="Port web server (default: 20129)")
    web_p.add_argument("-H", "--host", default="127.0.0.1", help="Host binding (default: 127.0.0.1)")
    web_p.add_argument("-n", "--no-browser", action="store_true", help="Jangan buka browser otomatis")

    sub.add_parser("dashboard", help="Buka Web Dashboard 9Router di browser (port 20128)")
    sub.add_parser("doctor", help="Cek environment & 9Router gateway")
    sub.add_parser("status", help="Cek status gateway 9Router & AI provider")
    sub.add_parser("models", help="Daftar model yang tersedia di 9Router")

    t = sub.add_parser("test", help="Test inferensi model 9Router")
    t.add_argument("-m", "--model", help="ID model target (default: active model)")
    t.add_argument("-p", "--prompt", default="Jelaskan dalam 1 kalimat apa itu metode ilmiah.", help="Prompt pengujian")

    sub.add_parser("benchmark", help="Benchmark latensi & reliabilitas seluruh model 9Router")
    sub.add_parser("start-router", help="Jalankan 9Router daemon di background")

    gen = sub.add_parser("generate", help="Generate dokumen KTI")
    gen.add_argument("-i", "--input",    help="File input (.txt / .md)")
    gen.add_argument("-m", "--mode",     help="Format output (kti_document, research_presentation, …)")
    gen.add_argument("-o", "--output",   default="outputs/kir")
    gen.add_argument("-d", "--domain",   help="Domain ilmu")
    gen.add_argument("-a", "--audience", help="Tingkat audiens")
    gen.add_argument("--model",          help="Model AI 9Router (e.g. ag/gemini-3.7-flash-high, ollama/kimi-k2.5)")
    gen.add_argument("--no-quality",     action="store_true")

    sub.add_parser("plan", help="Blueprint JSON saja")

    args, _ = parser.parse_known_args()
    print_banner(KIR_BANNER, SUBTITLE, ACCENT)

    if args.help:
        _show_info_cards()
        print_rule("Perintah Tersedia", ACCENT)
        console.print()
        for label in COMMANDS:
            console.print(f"  {label}")
        console.print()
        console.print("[dim]Gunakan [bold]kir <perintah> --help[/bold] untuk opsi lengkap.[/dim]\n")
        return

    if args.subcmd == "web":
        cmd_web(port=args.port, host=args.host, open_browser=not args.no_browser, accent=ACCENT); return
    if args.subcmd == "dashboard":
        cmd_router_dashboard(ACCENT); return
    if args.subcmd == "doctor":
        cmd_doctor(ACCENT); return
    if args.subcmd == "status":
        cmd_router_status(ACCENT); return
    if args.subcmd == "models":
        cmd_router_models(ACCENT); return
    if args.subcmd == "test":
        cmd_router_test(model=args.model, prompt=args.prompt, accent=ACCENT); return
    if args.subcmd == "benchmark":
        cmd_router_benchmark(ACCENT); return
    if args.subcmd == "start-router":
        cmd_router_start(ACCENT); return
    if args.subcmd == "generate":
        cmd_generate(input_file=args.input, mode_key=args.mode, output_dir=args.output,
                     domain=args.domain, audience=args.audience,
                     enable_quality=not args.no_quality, model=args.model); return
    if args.subcmd == "plan":
        cmd_plan(); return

    # ── Interactive mode ──────────────────────────────────────
    _show_info_cards()
    if not sys.stdin.isatty():
        info("Mode interaktif membutuhkan terminal. Gunakan [bold]kir --help[/bold].", ACCENT)
        return

    while True:
        choice = questionary.select("Apa yang ingin kamu lakukan?",
                                    choices=list(COMMANDS.keys()), style=STYLE).ask()
        cmd_fn = COMMANDS.get(choice) if choice else None
        if choice is None or cmd_fn is None:
            console.print()
            console.print(Align.center(Text("Semangat berkarya ilmiah! 🔬", style=f"{ACCENT} bold")))
            console.print()
            break

        console.print()
        try:
            cmd_fn()  # type: ignore[operator]
        except KeyboardInterrupt:
            info("Dihentikan — kembali ke menu.", ACCENT)
        except Exception:
            console.print_exception()

        console.print()
        again = questionary.confirm("Kembali ke menu utama?", default=True, style=STYLE).ask()
        if not again:
            console.print()
            console.print(Align.center(Text("Semangat berkarya ilmiah! 🔬", style=f"{ACCENT} bold")))
            console.print()
            break
        console.clear()
        print_banner(KIR_BANNER, SUBTITLE, ACCENT)
        _show_info_cards()


if __name__ == "__main__":
    main_kir()
