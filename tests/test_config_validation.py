from pathlib import Path
from docflow.config import load_config

def test_load_config(tmp_path: Path):
    cfg_file = tmp_path / "cfg.toml"
    cfg_file.write_text("""
[inbox]
path = "./inbox"
archive_path = "./archive"
""", "utf-8")
    cfg = load_config(cfg_file)
    assert cfg.inbox.path