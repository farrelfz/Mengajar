"""
app/cli/mengajar_cli.py — CLI `mengajar` untuk Materi Pengajaran.

Target pengguna: Guru, dosen, instruktur, pengajar.
Warna aksen  : Biru #2563eb
Format output: Teaching Presentation 16:9, Detailed Handout A4, Student Worksheet
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
ACCENT = "#2563eb"
ACCENT_GREEN = "#10b981"

MENGAJAR_BANNER = r"""
 ███╗   ███╗███████╗███╗   ██╗ ██████╗  █████╗      ██╗ █████╗ ██████╗
 ████╗ ████║██╔════╝████╗  ██║██╔════╝ ██╔══██╗     ██║██╔══██╗██╔══██╗
 ██╔████╔██║█████╗  ██╔██╗ ██║██║  ███╗███████║     ██║███████║██████╔╝
 ██║╚██╔╝██║██╔══╝  ██║╚██╗██║██║   ██║██╔══██║██   ██║██╔══██║██╔══██╗
 ██║ ╚═╝ ██║███████╗██║ ╚████║╚██████╔╝██║  ██║╚█████╔╝██║  ██║██║  ██║
 ╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝ ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
"""
SUBTITLE = "AI untuk Materi Pengajaran Profesional  ·  v0.2.0"

# ─────────────────────────────────────────────────────────────
# Questionary style (blue)
# ─────────────────────────────────────────────────────────────
STYLE = QStyle(
    [
        ("qmark",       "fg:#2563eb bold"),
        ("question",    "bold"),
        ("answer",      "fg:#10b981 bold"),
        ("pointer",     "fg:#2563eb bold"),
        ("highlighted", "fg:#2563eb bold"),
        ("selected",    "fg:#10b981"),
        ("separator",   "fg:#555555"),
        ("instruction", "fg:#888888"),
        ("text",        ""),
        ("disabled",    "fg:#858585 italic"),
    ]
)

# ─────────────────────────────────────────────────────────────
# Output modes specific to teaching / pengajaran
# ─────────────────────────────────────────────────────────────
MENGAJAR_MODES: list[dict] = [
    {
        "label":    "🖥   Slide Presentasi 16:9  —  Untuk mengajar di kelas / proyektor",
        "artifact": "teaching_presentation",
        "format":   "presentation-16-9",
    },
    {
        "label":    "📚  Modul / Handout A4  —  Bahan ajar untuk dibagikan ke siswa",
        "artifact": "detailed_handout",
        "format":   "a4-tutorial",
    },
    {
        "label":    "📝  Lembar Kerja Siswa (LKS)  —  Worksheet interaktif",
        "artifact": "student_worksheet",
        "format":   "a4-portrait",
    },
    {
        "label":    "🗂   Rangkuman Satu Halaman  —  Ringkasan konsep untuk review",
        "artifact": "one_page_summary",
        "format":   "summary-a4",
    },
]

MODE_MAP = {m["label"]: m for m in MENGAJAR_MODES}

# Mata pelajaran yang relevan untuk pengajaran
MATPEL_CHOICES = [
    "Matematika",
    "Fisika",
    "Kimia",
    "Biologi",
    "Ilmu Komputer",
    "Bahasa Indonesia",
    "Bahasa Inggris",
    "Sejarah",
    "Geografi",
    "Ekonomi",
    "Sosiologi",
    "General Science",
]

# Jenjang pendidikan untuk pengajaran
JENJANG_CHOICES = [
    "SD / Sekolah Dasar",
    "SMP / Sekolah Menengah Pertama",
    "SMA / Sekolah Menengah Atas",
    "SMK / Kejuruan",
    "Perguruan Tinggi (S1)",
    "Umum / Semua Jenjang",
]

# Mapping ke enum yang tersedia di blueprint
_MATPEL_TO_DOMAIN = {
    "Matematika":         "Mathematics",
    "Fisika":             "Physics",
    "Kimia":              "Chemistry",
    "Biologi":            "Biology",
    "Ilmu Komputer":      "Computer Science",
    "Bahasa Indonesia":   "Education",
    "Bahasa Inggris":     "Education",
    "Sejarah":            "Education",
    "Geografi":           "General Science",
    "Ekonomi":            "General Science",
    "Sosiologi":          "Education",
    "General Science":    "General Science",
}

_JENJANG_TO_AUDIENCE = {
    "SD / Sekolah Dasar":               "Beginner",
    "SMP / Sekolah Menengah Pertama":    "Middle School",
    "SMA / Sekolah Menengah Atas":       "High School",
    "SMK / Kejuruan":                    "High School",
    "Perguruan Tinggi (S1)":             "Undergraduate",
    "Umum / Semua Jenjang":              "General Public",
}


# ─────────────────────────────────────────────────────────────
# Info cards
# ─────────────────────────────────────────────────────────────

def _show_info_cards() -> None:
    cards = Columns(
        [
            Panel(
                "[bold #10b981]Analisis Materi[/]\nAI memahami topik &\nstruktur pengajaran",
                border_style="#10b981", padding=(0, 2),
            ),
            Panel(
                "[bold #2563eb]Blueprint Pedagogi[/]\nPola ajar terstruktur —\nbukan HTML mentah",
                border_style="#2563eb", padding=(0, 2),
            ),
            Panel(
                "[bold #f59e0b]Output Siap Pakai[/]\nSlide / Modul / LKS\ndalam format PDF",
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
    output_dir: str = "outputs/mengajar",
    matpel: str | None = None,
    jenjang: str | None = None,
    enable_quality: bool = True,
    model: str | None = None,
) -> None:
    print_rule("Generate Materi Pengajaran", ACCENT)
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
    if mode_key and any(mode_key in (m["artifact"], m["format"]) for m in MENGAJAR_MODES):
        selected_mode = next(m for m in MENGAJAR_MODES if mode_key in (m["artifact"], m["format"]))
    else:
        choice = questionary.select(
            "Jenis materi yang ingin dibuat:",
            choices=[m["label"] for m in MENGAJAR_MODES],
            style=STYLE,
        ).ask()
        if choice is None:
            return
        selected_mode = MODE_MAP[choice]

    # ── Mata pelajaran ────────────────────────────────────────
    if matpel:
        matched_m = next((m for m in MATPEL_CHOICES if matpel.lower() in m.lower()), None)
        selected_matpel = matched_m or matpel
    elif input_file:
        selected_matpel = "General Science"
    else:
        selected_matpel = questionary.select(
            "Mata pelajaran / bidang studi:",
            choices=MATPEL_CHOICES,
            style=STYLE,
        ).ask()
        if selected_matpel is None:
            return

    # ── Jenjang / Audience ────────────────────────────────────
    if jenjang:
        matched_j = next((j for j in JENJANG_CHOICES if jenjang.lower() in j.lower()), None)
        selected_jenjang = matched_j or jenjang
    elif input_file:
        selected_jenjang = "SMA / Sekolah Menengah Atas"
    else:
        selected_jenjang = questionary.select(
            "Jenjang pendidikan target:",
            choices=JENJANG_CHOICES,
            style=STYLE,
        ).ask()
        if selected_jenjang is None:
            return

    # ── Output dir ───────────────────────────────────────────
    if not output_dir or output_dir == "outputs/mengajar":
        out = wizard_output_dir(STYLE, default="outputs/mengajar") if not input_file else "outputs/mengajar"
        if not out:
            return
        output_dir = out

    # ── Quality eval ─────────────────────────────────────────
    if input_file is None:
        q = wizard_quality(STYLE)
        if q is None:
            return
        enable_quality = q

    # Translate ke domain/audience enum strings
    domain_str = _MATPEL_TO_DOMAIN.get(selected_matpel, "General Science")
    audience_str = _JENJANG_TO_AUDIENCE.get(selected_jenjang, "High School")

    # ── Summary ──────────────────────────────────────────────
    show_job_summary(
        input_path,
        f"{selected_mode['label']}\n  [dim]Matpel :[/dim] {selected_matpel}  |  Jenjang: {selected_jenjang}",
        domain_str,
        audience_str,
        output_dir,
        enable_quality,
        ACCENT,
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
        domain_str=domain_str,
        audience_str=audience_str,
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
    matpel = questionary.select(
        "Mata pelajaran:", choices=MATPEL_CHOICES, style=STYLE,
    ).ask()
    if not matpel:
        return
    console.print()
    from app.cli.shared import warn
    warn("Plan-only mode belum tersambung penuh ke skip-rendering.")
    info("Gunakan [bold]mengajar generate[/bold] untuk menghasilkan artefak penuh.", ACCENT)
    console.print()


# ─────────────────────────────────────────────────────────────
# Main interactive loop
# ─────────────────────────────────────────────────────────────

COMMANDS: dict[str, object] = {
    "⚡  Generate Materi  —  Slide / Modul / LKS → PDF siap pakai": cmd_generate,
    "🎨  Web Studio UI  —  Buka Web Dashboard lokal di port 20129": lambda: cmd_web(accent=ACCENT),
    "🤖  AI Router & Models  —  status, benchmark, & model 9Router": lambda: cmd_ai_router_menu(ACCENT, STYLE),
    "🗺   Plan saja  —  Blueprint JSON, tanpa rendering":              cmd_plan,
    "🩺  Doctor  —  cek environment & 9Router gateway":               cmd_doctor,
    "🚪  Keluar": None,
}


def main_mengajar() -> None:
    """Entry point for the `mengajar` CLI."""
    parser = argparse.ArgumentParser(prog="mengajar",
                                     description="MENGAJAR — AI Materi Pengajaran CLI",
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
    t.add_argument("-p", "--prompt", default="Jelaskan dalam 1 kalimat konsep dasar gravitasi.", help="Prompt pengujian")

    sub.add_parser("benchmark", help="Benchmark latensi & reliabilitas seluruh model 9Router")
    sub.add_parser("start-router", help="Jalankan 9Router daemon di background")

    gen = sub.add_parser("generate", help="Generate materi pengajaran")
    gen.add_argument("-i", "--input",    help="File input (.txt / .md)")
    gen.add_argument("-m", "--mode",     help="Format output (teaching_presentation, detailed_handout, …)")
    gen.add_argument("-o", "--output",   default="outputs/mengajar")
    gen.add_argument("--matpel",         help="Mata pelajaran")
    gen.add_argument("--jenjang",        help="Jenjang pendidikan")
    gen.add_argument("--model",          help="Model AI 9Router (e.g. ag/gemini-3.7-flash-high, ollama/kimi-k2.5)")
    gen.add_argument("--no-quality",     action="store_true")

    sub.add_parser("plan", help="Blueprint JSON saja")

    args, _ = parser.parse_known_args()
    print_banner(MENGAJAR_BANNER, SUBTITLE, ACCENT)

    if args.help:
        _show_info_cards()
        print_rule("Perintah Tersedia", ACCENT)
        console.print()
        for label in COMMANDS:
            console.print(f"  {label}")
        console.print()
        console.print("[dim]Gunakan [bold]mengajar <perintah> --help[/bold] untuk opsi lengkap.[/dim]\n")
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
        cmd_generate(
            input_file=args.input, mode_key=args.mode, output_dir=args.output,
            matpel=args.matpel, jenjang=args.jenjang,
            enable_quality=not args.no_quality, model=args.model,
        ); return
    if args.subcmd == "plan":
        cmd_plan(); return

    # ── Interactive mode ──────────────────────────────────────
    _show_info_cards()
    if not sys.stdin.isatty():
        info("Mode interaktif membutuhkan terminal. Gunakan [bold]mengajar --help[/bold].", ACCENT)
        return

    while True:
        choice = questionary.select("Apa yang ingin kamu buat?",
                                    choices=list(COMMANDS.keys()), style=STYLE).ask()
        cmd_fn = COMMANDS.get(choice) if choice else None
        if choice is None or cmd_fn is None:
            console.print()
            console.print(Align.center(Text("Selamat mengajar! 📚", style=f"{ACCENT} bold")))
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
            console.print(Align.center(Text("Selamat mengajar! 📚", style=f"{ACCENT} bold")))
            console.print()
            break
        console.clear()
        print_banner(MENGAJAR_BANNER, SUBTITLE, ACCENT)
        _show_info_cards()


if __name__ == "__main__":
    main_mengajar()
