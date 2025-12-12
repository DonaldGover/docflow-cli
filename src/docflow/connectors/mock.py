from __future__ import annotations
from pathlib import Path
import shutil
from docflow.models import Extraction

class MockCRM:
    def record(self, extraction: Extraction, run_id: str) -> None:
        return

class MockDMS:
    def file(self, pdf_path: Path, extraction: Extraction, archive_dir: str) -> Path:
        dest_dir = Path(archive_dir)
        dest_dir.mkdir(parents=True, exist_ok=True)
        safe_type = extraction.document_type.lower()
        dest = dest_dir / f"{pdf_path.stem}_{safe_type}.pdf"
        shutil.copy2(pdf_path, dest)
        return dest