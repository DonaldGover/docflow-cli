from pathlib import Path
from docflow.config import AppCfg, InboxCfg
from docflow.pipeline import process_pdf

def test_pipeline_stub_ai(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    pdf = tmp_path / "x.pdf"
    pdf.write_bytes(b"%PDF-1.4\n% demo\n")
    cfg = AppCfg(inbox=InboxCfg(path=str(tmp_path),
                                archive_path=str(tmp_path / "archive")))
    result = process_pdf(pdf, cfg)
    assert result.status in ("needs_review", "success")
    assert (tmp_path / "archive").exists()