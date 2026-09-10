"""
app/cli/router_manager.py — Local 9Router Gateway Manager & Benchmark Suite.

Provides:
- Gateway status check (process, port 20128, API ping, Ollama status)
- Model listing & capability inspection from /v1/models
- Single model latency & completion testing
- Multi-model benchmarking with ranking and persistence (working_models.json)
- Background daemon starter for local 9router
"""
from __future__ import annotations

import asyncio
import json
import os
import shutil
import socket
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.ai.client import AICapability, GenerationRequest
from app.ai.router import NineRouterClient
from app.config.settings import get_settings
from app.core.logging import get_logger

log = get_logger(__name__)


@dataclass
class RouterStatus:
    process_running: bool
    port_listening: bool
    api_reachable: bool
    latency_ms: float
    base_url: str
    active_model: str
    available_models_count: int
    ollama_running: bool
    details: str = ""


def is_port_open(host: str = "127.0.0.1", port: int = 20128, timeout: float = 1.0) -> bool:
    """Check if a specific TCP port is open and listening."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (OSError, ConnectionRefusedError, TimeoutError):
        return False


def is_process_running(name: str = "9router") -> bool:
    """Check if 9router server process exists, excluding current process."""
    my_pid = str(os.getpid())
    try:
        res = subprocess.run(
            ["pgrep", "-af", name],
            capture_output=True,
            text=True,
            timeout=2.0,
        )
        if res.returncode != 0:
            return False
        for line in res.stdout.strip().splitlines():
            parts = line.split()
            if not parts:
                continue
            pid = parts[0]
            cmd = " ".join(parts[1:])
            if pid != my_pid and not ("python" in cmd and "router_manager" in cmd):
                return True
        return False
    except Exception:
        return False


def find_9router_binary() -> str | None:
    """Find the path to the 9router executable."""
    found = shutil.which("9router")
    if found:
        return found
    common_paths = [
        Path.home() / ".nvm" / "versions" / "node" / "v24.15.0" / "bin" / "9router",
        Path.home() / ".local" / "bin" / "9router",
        Path("/usr/local/bin/9router"),
    ]
    for p in common_paths:
        if p.is_file() and os.access(p, os.X_OK):
            return str(p)
    return None


async def get_router_status() -> RouterStatus:
    """Perform a comprehensive status check of the local 9Router environment."""
    settings = get_settings()
    base_url = settings.nine_router_base_url
    client = NineRouterClient()

    proc_ok = is_process_running("9router")
    port_ok = is_port_open("127.0.0.1", 20128)
    api_ok, latency, msg = await client.ping()

    models_count = 0
    if api_ok:
        models = await client.list_models()
        models_count = len(models)

    ollama_ok = is_port_open("127.0.0.1", 11434)
    active = settings.active_model or settings.ai_default_model

    return RouterStatus(
        process_running=proc_ok,
        port_listening=port_ok,
        api_reachable=api_ok,
        latency_ms=latency if api_ok else 0.0,
        base_url=base_url,
        active_model=active,
        available_models_count=models_count,
        ollama_running=ollama_ok,
        details=msg,
    )


def start_router_daemon() -> tuple[bool, str]:
    """Start local 9router daemon in the background if not already running."""
    if is_port_open("127.0.0.1", 20128):
        return True, "9Router port 20128 is already listening."

    bin_path = find_9router_binary()
    if not bin_path:
        return False, "9Router binary not found. Pastikan terinstall via npm/nvm."

    try:
        # Launch 9router in tray background mode without interactive prompts
        subprocess.Popen(
            [bin_path, "-t", "--skip-update"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
        # Wait up to 5 seconds for port to open
        for _ in range(10):
            time.sleep(0.5)
            if is_port_open("127.0.0.1", 20128):
                return True, f"9Router successfully started on port 20128 ({bin_path})"
        return False, "Process started but port 20128 did not open in 5 seconds."
    except Exception as exc:
        return False, f"Failed to launch 9router: {exc}"


async def test_single_model(
    model: str,
    prompt: str = "Balas dalam 1 kalimat pendek: 9Router lokal berfungsi dengan baik.",
    system_prompt: str = "You are a helpful AI assistant.",
    max_tokens: int = 100,
) -> dict[str, Any]:
    """Test a single model completion and measure precise latency."""
    client = NineRouterClient()
    req = GenerationRequest(
        user_prompt=prompt,
        system_prompt=system_prompt,
        required_capability=AICapability.CONTENT_WRITING,
        max_tokens=max_tokens,
        temperature=0.7,
        job_id="test_model",
        step="manual_test",
    )

    settings = get_settings()
    orig_model = settings.active_model
    settings.set_active_model(model)

    start = time.monotonic()
    try:
        resp = await client.generate(req)
        latency = round(time.monotonic() - start, 2)
        return {
            "model": model,
            "success": True,
            "latency": latency,
            "response": resp.content.strip(),
            "tokens": resp.total_tokens,
            "error": None,
        }
    except Exception as exc:
        latency = round(time.monotonic() - start, 2)
        return {
            "model": model,
            "success": False,
            "latency": latency,
            "response": "",
            "tokens": 0,
            "error": str(exc),
        }
    finally:
        settings.set_active_model(orig_model)


async def benchmark_models(
    prompt: str = "Tuliskan ringkasan 2 kalimat tentang metode penelitian ilmiah.",
    max_tokens: int = 150,
) -> tuple[list[dict[str, Any]], Path]:
    """Benchmark all models available on 9Router, rank them, and save report."""
    client = NineRouterClient()
    models_data = await client.list_models()
    model_ids = [m.get("id") for m in models_data if m.get("id")]

    # Fallback to configured presets if gateway model list is empty
    if not model_ids:
        settings = get_settings()
        candidates = [
            settings.ai_default_model,
            settings.ai_fast_model,
            settings.ai_reasoning_model,
            settings.ai_code_model,
            settings.ai_long_context_model,
        ]
        model_ids = list(dict.fromkeys([c for c in candidates if c]))

    results: list[dict[str, Any]] = []
    for m in model_ids:
        res = await test_single_model(m, prompt=prompt, max_tokens=max_tokens)
        results.append(res)

    # Save results to outputs/benchmarks/
    benchmarks_dir = Path("outputs") / "benchmarks"
    benchmarks_dir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    report_file = benchmarks_dir / f"benchmark_{timestamp}.json"
    working_file = benchmarks_dir / "working_models.json"

    successful = [r for r in results if r["success"]]
    successful.sort(key=lambda x: x["latency"])

    report_payload = {
        "timestamp": timestamp,
        "total_tested": len(results),
        "total_working": len(successful),
        "successful_models": successful,
        "failed_models": [r for r in results if not r["success"]],
    }

    report_file.write_text(json.dumps(report_payload, indent=2), encoding="utf-8")

    working_payload = {
        "updated_at": timestamp,
        "models": [{"id": r["model"], "latency": r["latency"]} for r in successful],
    }
    working_file.write_text(json.dumps(working_payload, indent=2), encoding="utf-8")

    return results, report_file
