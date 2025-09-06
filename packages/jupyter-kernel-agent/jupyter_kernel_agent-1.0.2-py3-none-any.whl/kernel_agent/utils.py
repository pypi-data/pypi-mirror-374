"""
Utilities for torch_kernel:
- Config loader with flexible JSON format
- URL derivation for execute/interrupt/shutdown
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

# Default config location (override via TORCH_KERNEL_CONFIG or CLI --config)
CONFIG_DEFAULT = Path.home() / ".torch_kernel.json"


def _to_list(conf: Any) -> List[Dict[str, Any]]:
    """
    Accept either:
      - list[dict, ...]
      - dict with "endpoints": list[dict, ...]
      - single dict → wrapped into a list
    """
    if isinstance(conf, list):
        return conf
    if isinstance(conf, dict):
        if "endpoints" in conf and isinstance(conf["endpoints"], list):
            return conf["endpoints"]
        return [conf]
    raise ValueError("Configuration must be a JSON array or an object")


def _norm_ep(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize endpoint item keys and derive a display-safe name when missing.
    Accepted keys (aliases):
      - endpoint / Endpoint
      - api_key / key
      - name (optional)
    """
    endpoint = item.get("endpoint") or item.get("Endpoint")
    api_key = item.get("api_key") or item.get("key")
    name = item.get("name")

    if not endpoint:
        raise ValueError(f"Missing endpoint URL in item: {item}")

    if not name:
        try:
            host = urlparse(endpoint).netloc or endpoint
        except Exception:
            host = endpoint
        name = re.sub(r"[^a-zA-Z0-9._-]+", "-", host)

    out = {"name": name, "endpoint": endpoint}
    if api_key:
        out["api_key"] = api_key
    return out


def load_config(path: Optional[str | os.PathLike] = None) -> List[Dict[str, Any]]:
    """
    Load and normalize config from path or default.
    """
    p = Path(path) if path else CONFIG_DEFAULT
    if not p.exists():
        raise FileNotFoundError(f"torch_kernel config not found at {p}")
    try:
        data = json.loads(p.read_text())
    except Exception as e:
        raise ValueError(f"Failed to parse JSON config {p}: {e}") from e
    items = _to_list(data)
    return [_norm_ep(it) for it in items]


def derive_urls(endpoint: str) -> Tuple[str, str, str]:
    """
    Accept either a base URL or a specific execute/run URL.

    Returns (EXECUTE_URL, INTERRUPT_URL, SHUTDOWN_URL)
    Rules:
      - If endpoint ends with /execute or /run → treat as execute URL; sibling /interrupt and /shutdown
      - Else → base + /execute, /interrupt, /shutdown
    """
    e = endpoint.rstrip("/")
    lower = e.lower()
    if lower.endswith("/execute") or lower.endswith("/run"):
        base = e.rsplit("/", 1)[0]
        return e, base + "/interrupt", base + "/shutdown"
    return e + "/execute", e + "/interrupt", e + "/shutdown"