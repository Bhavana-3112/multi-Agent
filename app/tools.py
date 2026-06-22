from pathlib import Path

from agents import function_tool

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"


def _safe_path(path: str) -> Path:
    """Resolve path under output/ and block traversal."""
    resolved = (OUTPUT_DIR / path).resolve()
    if not str(resolved).startswith(str(OUTPUT_DIR.resolve())):
        raise ValueError(f"Path must stay inside output/: {path}")
    return resolved


@function_tool
def write_file(path: str, content: str) -> str:
    """Write content to a file under the output/ directory."""
    file_path = _safe_path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return f"Wrote {len(content)} bytes to {file_path.relative_to(OUTPUT_DIR.parent)}"


@function_tool
def read_file(path: str) -> str:
    """Read content from a file under the output/ directory."""
    file_path = _safe_path(path)
    if not file_path.exists():
        return f"Error: file not found: {path}"
    return file_path.read_text(encoding="utf-8")
