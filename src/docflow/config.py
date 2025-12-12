from __future__ import annotations
from pathlib import Path
from pydantic import BaseModel, Field
import os

try:
    import tomllib  # py3.11+
except ImportError:
    import tomli as tomllib  # type: ignore


class InboxCfg(BaseModel):
    path: str = Field(..., min_length=1)
    archive_path: str = Field(..., min_length=1)


class OcrCfg(BaseModel):
    enabled: bool = True
    engine: str = "ocrmypdf"


class AiCfg(BaseModel):
    provider: str = "openai"
    model: str = "gpt-4.1-mini"
    api_key_env: str = "OPENAI_API_KEY"


class StoreCfg(BaseModel):
    sqlite_path: str = "./docflow.db"


class ConnectorsCfg(BaseModel):
    crm: str = "mock"
    dms: str = "mock"


class AppCfg(BaseModel):
    inbox: InboxCfg
    ocr: OcrCfg = OcrCfg()
    ai: AiCfg = AiCfg()
    store: StoreCfg = StoreCfg()
    connectors: ConnectorsCfg = ConnectorsCfg()


def load_config(path: Path) -> AppCfg:
    raw = tomllib.loads(path.read_text("utf-8"))
    cfg = AppCfg(**raw)
    if cfg.ai.provider == "openai":
        os.getenv(cfg.ai.api_key_env, "")
    return cfg