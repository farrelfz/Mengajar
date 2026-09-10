"""
app/cli/shared.py — Shared utilities for both `kir` and `mengajar` CLIs.

Contains:
- Console & questionary style helpers
- _run_pipeline() — async core that calls MaterialProductionPipeline
- cmd_doctor() — environment health check
- Shared Rich helpers (_ok, _warn, _err, _info, _print_rule)
"""
from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path
from typing import Any

import questionary
from questionary import Style as QStyle
from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

# ─────────────────────────────────────────────────────────────
# Shared console (single instance, imported by both CLIs)
# ─────────────────────────────────────────────────────────────
console = Console()


# ─────────────────────────────────────────────────────────────
# Domain & audience mappings (aligned with blueprint enums)
# ─────────────────────────────────────────────────────────────
DOMAIN_CHOICES = [
    "Research Methodology",
    "General Science",
    "Physics",
    "Mathematics",
    "Computer Science",
    "Biology",
    "Chemistry",
    "Education",
]

AUDIENCE_CHOICES = [
    "Beginner",
    "Middle School",
    "High School",
    "Undergraduate",
    "Researcher",
    "General Public",
]

_DOMAIN_MAP_LAZY: dict[str, Any] | None = None
_AUDIENCE_MAP_LAZY: dict[str, Any] | None = None


def _get_domain_map() -> dict[str, Any]:
    global _DOMAIN_MAP_LAZY
    if _DOMAIN_MAP_LAZY is None:
        from app.blueprints.content import KnowledgeDomain
        _DOMAIN_MAP_LAZY = {
            "Eksperimen (KIR)":     KnowledgeDomain.EXPERIMENT_KIR,
            "KIR / Eksperimen":     KnowledgeDomain.EXPERIMENT_KIR,
            "Research Methodology": KnowledgeDomain.RESEARCH_METHODOLOGY,
            "General Science":      KnowledgeDomain.GENERAL_SCIENCE,
            "Physics":              KnowledgeDomain.PHYSICS,
            "Mathematics":          KnowledgeDomain.MATHEMATICS,
            "Computer Science":     KnowledgeDomain.COMPUTER_SCIENCE,
            "Biology":              KnowledgeDomain.BIOLOGY,
            "Chemistry":            KnowledgeDomain.CHEMISTRY,
            "Education":            KnowledgeDomain.EDUCATION,
        }
    return _DOMAIN_MAP_LAZY


def _get_audience_map() -> dict[str, Any]:
    global _AUDIENCE_MAP_LAZY
    if _AUDIENCE_MAP_LAZY is None:
        from app.blueprints.content import AudienceLevel
        _AUDIENCE_MAP_LAZY = {
            "Beginner":       AudienceLevel.BEGINNER,
            "Middle School":  AudienceLevel.MIDDLE_SCHOOL,
            "High School":    AudienceLevel.HIGH_SCHOOL,
            "Undergraduate":  AudienceLevel.UNDERGRADUATE,
            "Researcher":     AudienceLevel.RESEARCHER,
            "General Public": AudienceLevel.GENERAL_PUBLIC,
        }
    return _AUDIENCE_MAP_LAZY


# ─────────────────────────────────────────────────────────────
# Print helpers
# ─────────────────────────────────────────────────────────────

def print_rule(title: str = "", accent: str = "#7c3aed") -> None:
    console.print(Rule(title, style=accent))


def ok(msg: str) -> None:
    console.print(f"  [bold green]✓[/bold green]  {msg}")


def warn(msg: str) -> None:
    console.print(f"  [bold yellow]⚠[/bold yellow]  {msg}")


def err(msg: str) -> None:
    console.print(f"  [bold red]✗[/bold red]  {msg}")


def info(msg: str, accent: str = "#7c3aed") -> None:
    console.print(f"  [bold {accent}]›[/bold {accent}]  {msg}")


# ─────────────────────────────────────────────────────────────
# Banner printer
# ─────────────────────────────────────────────────────────────

def print_banner(ascii_art: str, subtitle: str, accent: str) -> None:
    console.print()
    console.print(Align.center(Text(ascii_art, style=f"bold {accent}")))
    console.print(Align.center(Text(subtitle, style="dim")))
    console.print()


# ─────────────────────────────────────────────────────────────
# Doctor command (shared)
# ─────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────
# Doctor command (shared)
# ─────────────────────────────────────────────────────────────

def cmd_doctor(accent: str = "#7c3aed") -> None:
    """Run comprehensive environment & local 9Router health checks."""
    print_rule("Environment & AI Doctor", accent)
    console.print()

    checks = Table(box=box.ROUNDED, show_header=False, padding=(0, 2))
    checks.add_column("Status", width=4)
    checks.add_column("Component", style="bold", width=24)
    checks.add_column("Detail", style="dim")

    # .env
    env_ok = Path(".env").exists()
    checks.add_row(
        "[green]✓[/green]" if env_ok else "[yellow]![/yellow]",
        ".env file",
        "Found" if env_ok else "Not found (using system / 9router env)",
    )

    # outputs/
    Path("outputs").mkdir(exist_ok=True)
    checks.add_row("[green]✓[/green]", "Output directory", "outputs/ ready")

    # Playwright
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
        pw_ok, pw_msg = True, "Chromium driver reachable"
    except ImportError:
        pw_ok, pw_msg = False, "Run: pip install playwright && playwright install chromium"
    checks.add_row("[green]✓[/green]" if pw_ok else "[red]✗[/red]", "Playwright", pw_msg)

    # Jinja2
    try:
        import jinja2  # noqa: F401
        checks.add_row("[green]✓[/green]", "Jinja2 templates", f"v{jinja2.__version__}")
    except ImportError:
        checks.add_row("[red]✗[/red]", "Jinja2 templates", "Not installed")

    # PyMuPDF
    try:
        import pymupdf  # noqa: F401
        checks.add_row("[green]✓[/green]", "PyMuPDF (PDF inspection)", "Available")
    except ImportError:
        checks.add_row("[red]✗[/red]", "PyMuPDF (PDF inspection)", "Not installed")

    # Local 9Router & AI Providers
    from app.cli.router_manager import get_router_status
    from app.config.settings import get_settings

    st = asyncio.run(get_router_status())
    settings = get_settings()

    # 9Router Daemon / Process
    proc_str = "[green]Running[/green]" if st.process_running else "[yellow]Not detected (standalone/background)[/yellow]"
    checks.add_row(
        "[green]✓[/green]" if st.process_running or st.port_listening else "[red]✗[/red]",
        "9Router Daemon",
        proc_str,
    )

    # Port 20128
    port_str = "Port 20128 LISTENING" if st.port_listening else "Port 20128 CLOSED"
    checks.add_row(
        "[green]✓[/green]" if st.port_listening else "[red]✗[/red]",
        "9Router Port",
        port_str,
    )

    # Gateway API Reachability
    if st.api_reachable:
        api_detail = f"OK ({st.latency_ms:.1f}ms) · {st.available_models_count} models loaded"
        checks.add_row("[green]✓[/green]", "9Router API /models", api_detail)
    else:
        checks.add_row("[red]✗[/red]", "9Router API /models", f"Unavailable ({st.details})")

    # Active AI Model
    eff_model = settings.get_effective_model()
    checks.add_row("[cyan]🤖[/cyan]", "Active AI Model", f"[bold cyan]{eff_model}[/bold cyan]")

    # Ollama Fallback
    ollama_str = "Listening on port 11434" if st.ollama_running else "Offline (local fallback unavailable)"
    checks.add_row(
        "[green]✓[/green]" if st.ollama_running else "[yellow]![/yellow]",
        "Ollama Fallback",
        ollama_str,
    )

    console.print(checks)
    console.print()

    if not st.port_listening:
        console.print(
            Panel(
                "[yellow]9Router belum aktif![/yellow]\n"
                "Jalankan gateway dengan: [bold]kir start-router[/bold] atau [bold]9router -n[/bold]\n"
                f"Target Base URL: [bold]{settings.nine_router_base_url}[/bold]",
                title="9Router Status", border_style="yellow", padding=(0, 2),
            )
        )
    else:
        console.print(
            Panel(
                f"[green]✓ 9Router lokal aktif ({st.latency_ms:.1f}ms). Siap inferensi dengan model [bold]{eff_model}[/bold]![/green]",
                border_style="green", padding=(0, 2),
            )
        )
    console.print()


# ─────────────────────────────────────────────────────────────
# 9Router Dedicated Commands
# ─────────────────────────────────────────────────────────────

def cmd_router_status(accent: str = "#7c3aed") -> None:
    """Display focused status card for local 9Router."""
    from app.cli.router_manager import get_router_status
    from app.config.settings import get_settings

    print_rule("9Router Gateway Status", accent)
    console.print()

    st = asyncio.run(get_router_status())
    settings = get_settings()

    status_tbl = Table(box=box.ROUNDED, show_header=False, padding=(0, 2))
    status_tbl.add_column("Key", style="dim", width=22)
    status_tbl.add_column("Value", style="bold")

    status_tbl.add_row("Base URL", st.base_url)
    status_tbl.add_row("Port 20128", "[green]LISTENING[/green]" if st.port_listening else "[red]CLOSED[/red]")
    status_tbl.add_row("Daemon Process", "[green]RUNNING[/green]" if st.process_running else "[dim]Not in pgrep[/dim]")
    status_tbl.add_row(
        "API Connectivity",
        f"[green]REACHABLE ({st.latency_ms:.1f}ms)[/green]" if st.api_reachable else f"[red]UNREACHABLE ({st.details})[/red]",
    )
    status_tbl.add_row("Available Models", f"[cyan]{st.available_models_count} models[/cyan]")
    status_tbl.add_row("Active Model", f"[bold cyan]{st.active_model}[/bold cyan]")
    status_tbl.add_row("Fast Model", settings.ai_fast_model)
    status_tbl.add_row("Reasoning Model", settings.ai_reasoning_model)
    status_tbl.add_row("Ollama Fallback", "[green]READY[/green]" if st.ollama_running else "[yellow]OFFLINE[/yellow]")

    console.print(
        Panel(
            status_tbl,
            title=f"[bold {accent}]9Router Architecture[/bold {accent}]",
            border_style=accent,
            padding=(1, 2),
        )
    )
    console.print()


def cmd_router_models(accent: str = "#7c3aed") -> None:
    """List available models from the local 9Router gateway."""
    from app.ai.router import NineRouterClient
    from app.config.settings import get_settings

    print_rule("9Router — Model Catalog", accent)
    console.print()

    client = NineRouterClient()
    models = asyncio.run(client.list_models())

    if not models:
        warn("Tidak dapat mengambil model dari 9Router (apakah gateway sudah berjalan di port 20128?).")
        info("Coba jalankan: [bold]kir start-router[/bold] atau periksa [bold]ai-router status[/bold]", accent)
        console.print()
        return

    settings = get_settings()
    active = settings.get_effective_model()

    tbl = Table(box=box.ROUNDED, padding=(0, 1))
    tbl.add_column("No", justify="right", style="dim", width=4)
    tbl.add_column("Model ID", style="bold", min_width=28)
    tbl.add_column("Provider / Owner", style="cyan")
    tbl.add_column("Context", justify="right")
    tbl.add_column("Capabilities", style="dim")
    tbl.add_column("Status", justify="center")

    for i, m in enumerate(models, 1):
        mid = m.get("id", "-")
        owner = m.get("owned_by", "-")
        ctx = m.get("context_length") or m.get("contextWindow")
        ctx_str = f"{ctx:,}" if isinstance(ctx, int) else "-"
        caps = m.get("capabilities", {})
        cap_tags = []
        if caps.get("reasoning"):
            cap_tags.append("🧠 reasoning")
        if caps.get("tools"):
            cap_tags.append("🔧 tools")
        if caps.get("vision"):
            cap_tags.append("👁 vision")
        cap_str = ", ".join(cap_tags) if cap_tags else "-"

        is_active = mid == active
        status_tag = "[bold green]ACTIVE[/bold green]" if is_active else "[dim]ready[/dim]"

        tbl.add_row(
            str(i),
            f"[bold {accent}]{mid}[/bold {accent}]" if is_active else mid,
            owner,
            ctx_str,
            cap_str,
            status_tag,
        )

    console.print(tbl)
    console.print()
    info(f"Total model terdaftar: [bold]{len(models)}[/bold]. Model aktif: [bold cyan]{active}[/bold cyan]", accent)
    console.print()


def cmd_router_test(
    model: str | None = None,
    prompt: str = "Jelaskan dalam 1 kalimat apa itu metode ilmiah.",
    accent: str = "#7c3aed",
) -> None:
    """Run a quick completion test on a 9Router model."""
    from app.cli.router_manager import test_single_model
    from app.config.settings import get_settings

    settings = get_settings()
    target_model = model or settings.get_effective_model()

    print_rule(f"9Router Test — {target_model}", accent)
    console.print()
    info(f"Mengirim test prompt ke model: [bold]{target_model}[/bold]...", accent)

    with console.status(f"[bold {accent}]Menguji model {target_model}…[/bold {accent}]"):
        res = asyncio.run(test_single_model(target_model, prompt=prompt))

    if res["success"]:
        ok(f"Berhasil merespons dalam [bold green]{res['latency']}s[/bold green] ({res['tokens']} tokens)")
        console.print()
        console.print(
            Panel(
                f"[italic]{res['response']}[/italic]",
                title=f"[bold green]Response ({target_model})[/bold green]",
                border_style="green",
                padding=(1, 2),
            )
        )
    else:
        err(f"Gagal dalam {res['latency']}s: {res['error']}")
    console.print()


def cmd_router_benchmark(accent: str = "#7c3aed") -> None:
    """Benchmark all models on 9Router and save leaderboard report."""
    from app.cli.router_manager import benchmark_models

    print_rule("9Router — Multi-Model Latency Benchmark", accent)
    console.print()
    info("Menguji model-model yang tersedia untuk mengukur latensi & reliabilitas...", accent)

    with console.status(f"[bold {accent}]Menjalankan benchmark model…[/bold {accent}]"):
        results, report_file = asyncio.run(benchmark_models())

    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    tbl = Table(box=box.ROUNDED, padding=(0, 2))
    tbl.add_column("Rank", justify="center", width=6)
    tbl.add_column("Model ID", style="bold")
    tbl.add_column("Latency", justify="right")
    tbl.add_column("Status", justify="center")

    for i, r in enumerate(successful, 1):
        tbl.add_row(f"#{i}", r["model"], f"[green]{r['latency']}s[/green]", "[green]✓ SUCCESS[/green]")

    for r in failed:
        tbl.add_row("-", r["model"], f"[red]{r['latency']}s[/red]", "[red]✗ FAILED[/red]")

    console.print(tbl)
    console.print()
    ok(f"Benchmark selesai! Berhasil: [bold green]{len(successful)}[/bold green], Gagal: [bold red]{len(failed)}[/bold red]")
    info(f"Laporan tersimpan di: [dim]{report_file}[/dim]", accent)
    console.print()


def cmd_router_start(accent: str = "#7c3aed") -> None:
    """Launch local 9router daemon."""
    from app.cli.router_manager import start_router_daemon

    print_rule("Start 9Router Gateway", accent)
    console.print()
    with console.status(f"[bold {accent}]Memulai proses 9Router…[/bold {accent}]"):
        ok_start, msg = start_router_daemon()
    if ok_start:
        ok(msg)
    else:
        err(msg)
    console.print()


def cmd_router_switch_model(accent: str = "#7c3aed", style: QStyle | None = None) -> None:
    """Interactively select and switch the active model."""
    from app.ai.router import NineRouterClient
    from app.config.settings import get_settings

    client = NineRouterClient()
    models = asyncio.run(client.list_models())
    choices = [m.get("id") for m in models if m.get("id")]
    settings = get_settings()
    if not choices:
        candidates = [
            settings.ai_default_model,
            settings.ai_fast_model,
            settings.ai_reasoning_model,
            settings.ai_code_model,
            settings.ai_long_context_model,
        ]
        choices = list(dict.fromkeys([c for c in candidates if c]))

    sel = questionary.select(
        "Pilih model aktif untuk 9Router:",
        choices=choices,
        style=style,
    ).ask()

    if sel:
        settings.set_active_model(sel)
        ok(f"Model aktif diubah menjadi: [bold cyan]{sel}[/bold cyan]")
        console.print()


def cmd_web(
    port: int = 20129,
    host: str = "127.0.0.1",
    open_browser: bool = True,
    accent: str = "#7c3aed",
) -> None:
    """Launch the Web Dashboard Studio server."""
    from app.web.server import run_web_server

    print_rule("Web Dashboard Studio", accent)
    console.print()
    console.print(f"[{accent}]Memulai Studio Web Server di:[/{accent}] [bold cyan underline]http://{host}:{port}[/bold cyan underline]")
    console.print("[dim]Gunakan Ctrl+C untuk menghentikan server web.[/dim]")
    console.print()
    run_web_server(host=host, port=port, open_browser=open_browser)


def cmd_router_dashboard(accent: str = "#7c3aed") -> None:
    """Open or display the 9Router web dashboard URL."""
    import webbrowser
    dashboard_url = "http://127.0.0.1:20128/dashboard"
    print_rule("9Router Web Dashboard", accent)
    console.print()
    console.print(f"[{accent}]URL Dashboard 9Router:[/{accent}] [bold cyan underline]{dashboard_url}[/bold cyan underline]")
    try:
        opened = webbrowser.open(dashboard_url)
        if opened:
            ok(f"Browser otomatis terbuka ke [bold cyan]{dashboard_url}[/bold cyan]")
        else:
            info(f"Silakan buka di browser Anda: [bold cyan]{dashboard_url}[/bold cyan]")
    except Exception as exc:
        info(f"Buka manual URL di browser: [bold cyan]{dashboard_url}[/bold cyan] ({exc})")
    console.print()


def cmd_ai_router_menu(accent: str = "#7c3aed", style: QStyle | None = None) -> None:
    """Interactive management menu for 9Router and AI models."""
    while True:
        print_rule("AI Router & Model Manager", accent)
        console.print()
        choice = questionary.select(
            "Pilih opsi AI Router:",
            choices=[
                "🎨  Buka Web Dashboard Studio (Port 20129)",
                "🌐  Buka Web Dashboard 9Router (Port 20128)",
                "📊  Status & Health Gateway 9Router",
                "📋  Daftar Model yang Tersedia",
                "⚡  Quick Test Inferensi Model Aktif",
                "🧪  Benchmark Semua Model (Latency & Kecepatan)",
                "🎯  Ganti Model Aktif untuk Sesi Ini",
                "🚀  Start 9Router Gateway di Background",
                "⬅️   Kembali ke Menu Utama",
            ],
            style=style,
        ).ask()

        if not choice or "Kembali" in choice:
            break
        elif "Studio (Port 20129)" in choice:
            cmd_web(accent=accent)
        elif "9Router (Port 20128)" in choice:
            cmd_router_dashboard(accent)
        elif "Status" in choice:
            cmd_router_status(accent)
        elif "Daftar" in choice:
            cmd_router_models(accent)
        elif "Quick Test" in choice:
            cmd_router_test(accent=accent)
        elif "Benchmark" in choice:
            cmd_router_benchmark(accent)
        elif "Ganti Model" in choice:
            cmd_router_switch_model(accent, style)
        elif "Start" in choice:
            cmd_router_start(accent)


# ─────────────────────────────────────────────────────────────
# Core pipeline runner (shared, async)
# ─────────────────────────────────────────────────────────────

async def _run_pipeline_async(
    input_path: Path,
    target_artifact_str: str,
    target_format: str,
    output_dir: str,
    domain_str: str,
    audience_str: str,
    enable_quality: bool,
    model: str | None = None,
) -> None:
    from app.blueprints.content import AudienceLevel, KnowledgeDomain
    from app.blueprints.production import TargetArtifactType
    from app.config.settings import get_settings
    from app.orchestration.production_pipeline import MaterialProductionPipeline

    if model:
        get_settings().set_active_model(model)

    # Resolve artifact type enum
    try:
        artifact_type = TargetArtifactType(target_artifact_str)
    except ValueError:
        artifact_type = TargetArtifactType.TEACHING_PRESENTATION

    domain = _get_domain_map().get(domain_str, KnowledgeDomain.RESEARCH_METHODOLOGY)
    audience = _get_audience_map().get(audience_str, AudienceLevel.HIGH_SCHOOL)

    raw_input = input_path.read_text(encoding="utf-8")
    pipeline = MaterialProductionPipeline()

    result = await pipeline.produce_artifact(
        raw_input=raw_input,
        source_hint=input_path.name,
        domain=domain,
        audience=audience,
        target_artifact=artifact_type,
        target_format=target_format,
        output_dir=output_dir,
        evaluate_quality=enable_quality,
    )

    console.print()
    if result.success:
        pdf_info = f"\n  [dim]PDF    :[/dim]  {result.pdf_path}" if result.pdf_path else ""
        # File size
        size_info = ""
        if result.pdf_path:
            p = Path(result.pdf_path)
            if p.exists():
                size_kb = p.stat().st_size / 1024
                size_info = f"\n  [dim]Size   :[/dim]  {size_kb:.1f} KB"
        console.print(
            Panel(
                f"[bold green]Generation complete![/bold green]\n\n"
                f"  [dim]Job ID :[/dim]  {result.job_id}"
                f"{pdf_info}{size_info}",
                title="[bold green]✓ Success[/bold green]",
                border_style="green", padding=(1, 3),
            )
        )
    else:
        err_body = "\n".join(f"  • {e}" for e in result.errors)
        console.print(
            Panel(
                f"[bold red]Generation failed.[/bold red]\n\n{err_body}",
                title="[bold red]✗ Failed[/bold red]",
                border_style="red", padding=(1, 3),
            )
        )
        sys.exit(1)


def run_pipeline(
    input_path: Path,
    target_artifact_str: str,
    target_format: str,
    output_dir: str,
    domain_str: str,
    audience_str: str,
    enable_quality: bool,
    accent: str = "#7c3aed",
    model: str | None = None,
) -> None:
    """Sync wrapper: runs the pipeline with a rich progress spinner."""
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

    console.print()
    with Progress(
        SpinnerColumn(spinner_name="dots", style=accent),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=30, style=accent, complete_style="#10b981"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    ) as progress:
        task = progress.add_task("[bold]Running pipeline…[/bold]", total=None)
        try:
            asyncio.run(
                _run_pipeline_async(
                    input_path, target_artifact_str, target_format,
                    output_dir, domain_str, audience_str, enable_quality,
                    model=model,
                )
            )
        except Exception:
            progress.stop()
            console.print_exception()
            sys.exit(1)
        finally:
            progress.update(task, completed=True)


# ─────────────────────────────────────────────────────────────
# Path resolution helper (supports Windows path, WSL, and quotes)
# ─────────────────────────────────────────────────────────────

def resolve_user_path(raw: str) -> Path:
    """
    Resolve user-entered file paths flexibly:
    - Strips surrounding single/double quotes and escaped quotes
    - Converts Windows drive paths (e.g. C:\\Users\\... or "C:\\Users\\...") to WSL (/mnt/c/Users/...)
    - Expands ~ to home directory
    - Normalizes backslashes to forward slashes
    """
    if not raw:
        return Path(raw)

    cleaned = raw.strip()
    # Strip any leading/trailing quotes including escaped quotes like \"
    while cleaned and (cleaned[0] in ('"', "'") or cleaned.startswith(r'\"') or cleaned.startswith(r"\'")):
        if cleaned.startswith(r'\"') or cleaned.startswith(r"\'"):
            cleaned = cleaned[2:]
        elif cleaned[0] in ('"', "'"):
            cleaned = cleaned[1:]
    while cleaned and (cleaned[-1] in ('"', "'") or cleaned.endswith(r'\"') or cleaned.endswith(r"\'")):
        if cleaned.endswith(r'\"') or cleaned.endswith(r"\'"):
            cleaned = cleaned[:-2]
        elif cleaned[-1] in ('"', "'"):
            cleaned = cleaned[:-1]

    cleaned = cleaned.strip()

    # Detect Windows drive letter: e.g. C:\... or c:/...
    win_match = re.match(r"^([a-zA-Z]):[/\\](.*)", cleaned)
    if win_match:
        drive = win_match.group(1).lower()
        rest = win_match.group(2).replace("\\", "/")
        wsl_cand = Path(f"/mnt/{drive}/{rest}")
        return wsl_cand

    # Standard unix path with backslash replacement (in case user pasted Windows path without drive)
    unix_path = cleaned.replace("\\", "/")
    return Path(unix_path).expanduser()


def _is_valid_input_file(raw: str) -> bool | str:
    if not raw or not raw.strip():
        return "Path file tidak boleh kosong."
    resolved = resolve_user_path(raw)
    if resolved.exists() and resolved.is_file():
        return True
    return f"File '{raw}' tidak ditemukan (mencari di: {resolved}). Pastikan path benar."


# ─────────────────────────────────────────────────────────────
# Interactive wizard helper — reusable across both CLIs
# ─────────────────────────────────────────────────────────────

def wizard_input_file(style: QStyle, accent: str = "#2563eb") -> Path | None:
    """Ask how the user wants to provide input: from file or paste text directly."""
    source_choice = questionary.select(
        "Pilih metode input materi:",
        choices=[
            "📄  Baca dari file (.md / .txt)",
            "✍️   Ketik / Paste teks langsung",
        ],
        style=style,
    ).ask()

    if source_choice is None:
        return None

    if "file" in source_choice:
        s = questionary.text(
            "Masukkan path file (contoh: hand_fire.md atau C:\\Users\\...\\materi.md):",
            style=style,
            validate=_is_valid_input_file,
        ).ask()
        if not s:
            return None
        resolved = resolve_user_path(s)
        console.print(f"  [dim]Path terbaca: {resolved}[/dim]")
        return resolved.resolve()
    else:
        title = questionary.text(
            "Judul / Nama Materi (untuk nama file output):",
            default="materi_input",
            style=style,
        ).ask()
        if not title:
            return None

        console.print(f"\n  [bold {accent}]›[/bold {accent}]  Masukkan teks materi di bawah (tekan Enter 2x saat selesai):")
        lines = []
        while True:
            try:
                line = input()
                if not line and lines and not lines[-1]:
                    break
                lines.append(line)
            except EOFError:
                break

        content = "\n".join(lines).strip()
        if not content:
            console.print("  [red]Input teks kosong.[/red]")
            return None

        # Save to temporary file in inputs/ directory
        inputs_dir = Path("inputs")
        inputs_dir.mkdir(exist_ok=True)
        safe_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in title.lower().replace(" ", "_"))
        temp_path = inputs_dir / f"{safe_name}.md"
        temp_path.write_text(content, encoding="utf-8")
        console.print(f"  [dim]Materi disimpan sementara di: {temp_path}[/dim]\n")
        return temp_path


def wizard_domain(style: QStyle, choices: list[str] | None = None) -> str | None:
    return questionary.select(
        "Knowledge domain / mata pelajaran:",
        choices=choices or DOMAIN_CHOICES,
        style=style,
    ).ask()


def wizard_audience(style: QStyle, choices: list[str] | None = None) -> str | None:
    return questionary.select(
        "Target audience / tingkat siswa:",
        choices=choices or AUDIENCE_CHOICES,
        style=style,
    ).ask()


def wizard_output_dir(style: QStyle, default: str = "outputs") -> str | None:
    return questionary.text(
        "Output directory:",
        default=default,
        style=style,
    ).ask()


def wizard_quality(style: QStyle) -> bool | None:
    return questionary.confirm(
        "Enable quality evaluation (recommended, adds ~30 sec)?",
        default=True,
        style=style,
    ).ask()


def show_job_summary(
    input_path: Path,
    mode_label: str,
    domain: str,
    audience: str,
    output_dir: str,
    enable_quality: bool,
    accent: str,
    model: str | None = None,
) -> None:
    """Print a rich summary card before running the pipeline."""
    from app.config.settings import get_settings

    active_ai = model or get_settings().get_effective_model()

    summary = Table(box=box.ROUNDED, show_header=False, padding=(0, 2))
    summary.add_column("Field", style="dim", width=22)
    summary.add_column("Value", style="bold")
    summary.add_row("Input", str(input_path))
    summary.add_row("Format", mode_label)
    summary.add_row("Domain", domain)
    summary.add_row("Audience", audience)
    summary.add_row("AI Model", f"[bold cyan]{active_ai}[/bold cyan] [dim](via 9Router)[/dim]")
    summary.add_row("Output dir", output_dir)
    summary.add_row("Quality check", "Yes ✓" if enable_quality else "No")
    console.print()
    console.print(
        Panel(
            summary,
            title=f"[bold {accent}]Job Configuration[/bold {accent}]",
            border_style=accent,
            padding=(1, 2),
        )
    )
    console.print()
