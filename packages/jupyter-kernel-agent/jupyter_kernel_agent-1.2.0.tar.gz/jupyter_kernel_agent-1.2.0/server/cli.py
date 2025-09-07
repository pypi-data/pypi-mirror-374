from __future__ import annotations
import argparse, uuid, uvicorn, sys
from pathlib import Path
from typing import Set
from server.app import app

def _load_list_arg(val: str | None) -> Set[str]:
    if not val: return set()
    return {p.strip() for p in val.split(",") if p.strip()}

def _load_file(path: str | None) -> Set[str]:
    if not path: return set()
    p = Path(path)
    if not p.exists():
        print(f"[torch_server] api_key file not found: {p}", file=sys.stderr)
        sys.exit(2)
    keys = set()
    for line in p.read_text().splitlines():
        for item in line.replace(",", " ").split():
            if item.strip():
                keys.add(item.strip())
    return keys

def main(argv: list[str] | None = None):
    p = argparse.ArgumentParser(prog="torch_server", description="Run the torch-kernel FastAPI server (Authorization: Bearer <API_KEY>)")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--reload", action="store_true")
    p.add_argument("--workers", type=int, default=1)
    p.add_argument("--api_key", default=None, help="Comma-separated API keys for Authorization: Bearer ...")
    p.add_argument("--api_key_file", default=None, help="File with one API key per line")
    args = p.parse_args(argv)

    api_keys = _load_list_arg(args.api_key) | _load_file(args.api_key_file)
    if not api_keys:
        key = uuid.uuid4().hex
        api_keys = {key}
        print("* API key generated:")
        print(f"*   Authorization: Bearer {key}")

    app.state.api_keys = api_keys  # type: ignore[attr-defined]
    sample = next(iter(api_keys))
    print(f"* Auth enabled, sample header: Authorization: Bearer {sample}")

    uvicorn.run(
        "server.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
        log_level="info",
    )

if __name__ == "__main__":
    main()