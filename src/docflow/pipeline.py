from __future__ import annotations
import uuid
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential
from .config import AppCfg
from .models import RunResult
from .ocr import run_ocr_if_enabled
from .ai import extract_with_ai
from .store import Store
from .connectors.mock import MockCRM, MockDMS

def _connectors(cfg: AppCfg):
    crm = MockCRM()
    dms = MockDMS()
    return crm, dms


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def process_pdf(pdf_path: Path, cfg: AppCfg) -> RunResult:
    run_id = str(uuid.uuid4())
    store = Store(cfg.store.sqlite_path)
    store.init()
    store.log_start(run_id, str(pdf_path))

    try:
        processed_pdf, text = run_ocr_if_enabled(pdf_path, cfg.ocr)
        extraction = extract_with_ai(text=text, cfg=cfg.ai)
        crm, dms = _connectors(cfg)
        crm.record(extraction=extraction, run_id=run_id)
        filed_path = dms.file(pdf_path=processed_pdf, extraction=extraction,
                              archive_dir=cfg.inbox.archive_path)

        status = "success" if extraction.confidence >= 0.75 else "needs_review"
        result = RunResult(run_id=run_id, status=status,
                           pdf_original=str(pdf_path),
                           pdf_processed=str(filed_path),
                           extraction=extraction)
        store.log_finish(run_id, status=status,
                         extraction=extraction.model_dump())
        return result
    except Exception as e:
        store.log_finish(run_id, status="failed", error=str(e))
        return RunResult(run_id=run_id, status="failed",
                         pdf_original=str(pdf_path),
                         pdf_processed=str(pdf_path),
                         error=str(e))