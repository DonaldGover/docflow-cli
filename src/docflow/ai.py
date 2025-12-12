from __future__ import annotations
import os, json, requests, hashlib, random
from .models import Extraction
from .config import AiCfg

SYSTEM_PROMPT = """You are an information extraction engine.
Return ONLY valid JSON matching this schema:
{
  "document_type": "RFP|BID|REBATE|MSC|ERR|UNKNOWN",
  "summary": "plain English",
  "required_actions": ["..."],
  "notice_date": "YYYY-MM-DD or null",
  "amount": "string or null",
  "confidence": 0.0-1.0
}
"""

def extract_with_ai(text: str, cfg: AiCfg, seed: int | None = None) -> Extraction:
    api_key = os.getenv(cfg.ai.api_key_env, "")
    if not api_key:
        digest = hashlib.sha1(text.encode("utf-8")).hexdigest()
        rand = random.Random(int(digest[:8], 16) + (seed or 0))
        confidence = round(rand.uniform(0.4, 0.9), 2)
        return Extraction(
            document_type="MSC",
            summary="Stub extraction for testing reproducibility.",
            required_actions=["Validate pipeline output consistency."],
            confidence=confidence,
        )

    url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions")
    payload = {
        "model": cfg.model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text[:120000]},
        ],
        "temperature": 0.2,
    }
    resp = requests.post(url, json=payload, headers={"Authorization": f"Bearer {api_key}"}, timeout=60)
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    data = json.loads(content)
    return Extraction(**data)