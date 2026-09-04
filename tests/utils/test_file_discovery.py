"""
Unit tests for safe file discovery and directory pruning utility.
"""
from pathlib import Path
import pytest
from app.utils.file_discovery import find_files, DEFAULT_SKIP_DIRS


def test_find_files_normal_directory(tmp_path: Path):
    # Setup test file tree
    (tmp_path / "sub1").mkdir()
    (tmp_path / "sub2").mkdir()
    file_a = tmp_path / "sub1" / "doc1.pdf"
    file_b = tmp_path / "sub2" / "doc2.pdf"
    file_txt = tmp_path / "sub1" / "notes.txt"

    file_a.write_text("a")
    file_b.write_text("b")
    file_txt.write_text("txt")

    results = find_files(tmp_path, patterns="*.pdf")
    assert results == [file_a, file_b]


def test_find_files_prunes_excluded_directories(tmp_path: Path):
    # Create normal and excluded directories
    normal_dir = tmp_path / "outputs"
    normal_dir.mkdir()
    (normal_dir / "report.pdf").write_text("report")

    venv_dir = tmp_path / "venv"
    venv_dir.mkdir()
    (venv_dir / "fake_lib.pdf").write_text("fake")

    dot_venv = tmp_path / ".venv"
    dot_venv.mkdir()
    (dot_venv / "dot_fake.pdf").write_text("dot_fake")

    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "git_artifact.pdf").write_text("git")

    node_modules = tmp_path / "node_modules"
    node_modules.mkdir()
    (node_modules / "pkg.pdf").write_text("pkg")

    pycache = tmp_path / "__pycache__"
    pycache.mkdir()
    (pycache / "compiled.pdf").write_text("pyc")

    # Discover PDFs from root tmp_path
    results = find_files(tmp_path, patterns="*.pdf")

    # Only output file should be discovered
    assert results == [normal_dir / "report.pdf"]


def test_find_files_deterministic_ordering(tmp_path: Path):
    f_c = tmp_path / "c.txt"
    f_a = tmp_path / "a.txt"
    f_b = tmp_path / "b.txt"
    for f in [f_c, f_a, f_b]:
        f.write_text("test")

    results = find_files(tmp_path, patterns="*.txt")
    assert results == [f_a, f_b, f_c]


def test_find_files_nonexistent_path(tmp_path: Path):
    nonexistent = tmp_path / "does_not_exist"
    assert find_files(nonexistent) == []


def test_find_files_single_file_target(tmp_path: Path):
    file_a = tmp_path / "test.pdf"
    file_a.write_text("pdf content")

    assert find_files(file_a, patterns="*.pdf") == [file_a]
    assert find_files(file_a, patterns="*.txt") == []


def test_find_files_multiple_patterns(tmp_path: Path):
    f_pdf = tmp_path / "doc.pdf"
    f_html = tmp_path / "doc.html"
    f_txt = tmp_path / "doc.txt"
    for f in [f_pdf, f_html, f_txt]:
        f.write_text("content")

    results = find_files(tmp_path, patterns=["*.pdf", "*.html"])
    assert results == [f_html, f_pdf]
