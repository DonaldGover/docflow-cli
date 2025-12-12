from __future__ import annotations
from pathlib import Path
import subprocess
from .config import OcrCfg

def run_ocr_if_enabled(pdf_path: Path, cfg: OcrCfg) -> tuple[Path, str]:
    processed = pdf_path
    if cfg.enabled and cfg.engine == "ocrmypdf":
        out = pdf_path.with_suffix(".ocr.pdf")
        try:
            subprocess.run(["ocrmypdf", "--skip-text", str(pdf_path), str(out)],
                           check=True, capture_output=True, text=True)
            processed = out
        except Exception:
            processed = pdf_path
    return processed, ""