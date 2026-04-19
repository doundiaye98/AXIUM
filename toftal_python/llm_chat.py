"""Appels à l’API Chat Completions (OpenAI ou endpoint compatible)."""

from __future__ import annotations

import json
import logging
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

log = logging.getLogger("axium.llm")


def complete_chat(
    *,
    base_url: str,
    api_key: str,
    model: str,
    system: str,
    messages: list[dict[str, str]],
    max_tokens: int = 1200,
    timeout: int = 90,
) -> str:
    """
    Envoie messages (sans le system) ; system est ajouté en tête.
    messages : rôles user | assistant uniquement.
    """
    url = base_url.rstrip("/") + "/chat/completions"
    payload: dict[str, Any] = {
        "model": model,
        "messages": [{"role": "system", "content": system}, *messages],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = Request(
        url,
        data=raw,
        method="POST",
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {api_key}",
        },
    )
    try:
        with urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        err_txt = exc.read().decode("utf-8", "replace")
        try:
            err_json = json.loads(err_txt)
            msg = (err_json.get("error") or {}).get("message") or err_txt
        except json.JSONDecodeError:
            msg = err_txt or str(exc)
        log.warning("LLM HTTP %s: %s", exc.code, msg[:500])
        raise RuntimeError(msg) from exc
    except URLError as exc:
        log.warning("LLM network: %s", exc)
        raise RuntimeError("network") from exc

    try:
        text = body["choices"][0]["message"]["content"]
        return (text or "").strip()
    except (KeyError, IndexError, TypeError) as exc:
        log.warning("LLM bad JSON: %s", str(body)[:800])
        raise RuntimeError("bad_response") from exc