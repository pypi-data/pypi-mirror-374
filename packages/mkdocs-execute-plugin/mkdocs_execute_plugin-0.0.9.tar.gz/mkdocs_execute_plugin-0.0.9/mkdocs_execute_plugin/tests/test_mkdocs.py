import os
import tempfile
import shutil

from pytest import fixture
from pathlib import Path
from contextlib import contextmanager

from mkdocs.__main__ import cli


@fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


def test_mkdocs(temp_dir):
    src_dir = Path(__file__).parent
    temp_dir = Path(temp_dir)
    shutil.copy(src_dir / "mkdocs.yml", temp_dir)
    shutil.copytree(src_dir / "docs", temp_dir / "docs")

    site_dir = temp_dir / "site"

    with set_directory(temp_dir):
        cli(["build", "--site-dir", str(site_dir.absolute())], standalone_mode=False)

    index_file: Path = site_dir / "index.html"
    assert index_file.read_text().count("__test_output__") == 2

    python_file: Path = site_dir / "python" / "index.html"
    python_html = python_file.read_text()
    assert python_html.count("__test_output__") == 2

    # Check that fallback kernel execution output is present
    jupytext_file: Path = site_dir / "jupytext.html"
    if not jupytext_file.exists():
        # Some mkdocs configs may put it in a subdir
        jupytext_file = site_dir / "jupytext" / "index.html"
    assert jupytext_file.exists(), "jupytext output file not found"
    jupytext_html = jupytext_file.read_text()
    assert "hello world" in jupytext_html, (
        "Expected output from fallback kernel not found in jupytext.html"
    )

    static_file: Path = site_dir / "static" / "index.html"
    assert static_file.read_text().count("__test_output__") == 1

    output_dir: Path = site_dir / "nested" / "_execute_outputs"
    image_file = output_dir / "index.md_1_0.png"
    assert image_file.is_file()


@contextmanager
def set_directory(path: Path):
    """Change the current working directory to the given path, and then change it back."""
    origin = Path().absolute()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)
