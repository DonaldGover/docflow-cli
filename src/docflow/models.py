from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal, Optional

DocType = Literal["RFP", "BID", "REBATE", "MSC", "ERR", "UNKNOWN"]

class Extraction(BaseModel):
    document_type: DocType = "UNKNOWN"
    summary: str = Field(..., min_length=1)
    required_actions: list[str] = []
    notice_date: Optional[str] = None
    amount: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.6)

class RunResult(BaseModel):
    run_id: str
    status: Literal["success", "failed", "needs_review"]
    pdf_original: str
    pdf_processed: str
    extraction: Extraction | None = None
    error: str | None = None