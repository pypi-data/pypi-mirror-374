# server/app.py
from __future__ import annotations
import os
import sys
import io
import uuid
import hmac
import ast
import traceback
import contextlib
import threading
import argparse
import subprocess
from collections import defaultdict
from typing import Dict, Any, Set, List, Optional
from datetime import timedelta

import torch
import torch.distributed as dist
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse, PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn
import pathlib


# ======================= Runtime config (via CLI) =======================
API_HOST: str = "0.0.0.0"
API_PORT: int = 8000
CODE_MAX_BYTES: int = 256 * 1024 * 256
DIST_TIMEOUT_SEC: int = 3600
ALLOWED_KEYS: Set[str] = set()  # Authorization: Bearer <API_KEY>

# ============================ Global state =============================
_namespaces: Dict[str, Dict[str, Any]] = defaultdict(dict)  # per-session globals per rank
_dist_lock = threading.Lock()                                # serialize collectives across requests
CTRL_PG = None                                               # CPU control process group (Gloo)

# Debug broadcast logging (rank0 prints)
DEBUG_BCAST = bool(int(os.getenv("KA_DEBUG_BCAST", "0")))

# ============================ Auth helper ==============================
def _require_auth(req: Request):
    if not ALLOWED_KEYS:  # open if no keys configured (dev mode)
        return
    auth = req.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
    candidate = auth[7:].strip()
    for key in ALLOWED_KEYS:
        if hmac.compare_digest(candidate, key):
            return
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")

# ======================= Code execution helpers ========================
def _init_namespace(session: str) -> Dict[str, Any]:
    ns = _namespaces[session]
    if "__builtins__" not in ns:
        ns["__builtins__"] = __builtins__
        ns["torch"] = torch
        ns["dist"] = dist
    ns["rank"] = dist.get_rank() if dist.is_initialized() else 0
    ns["world"] = dist.get_world_size() if dist.is_initialized() else 1
    ns["local_rank"] = int(os.getenv("LOCAL_RANK", "0"))
    return ns

def _exec_with_last_expr(code: str, ns: Dict[str, Any]) -> Any:
    tree = ast.parse(code, mode="exec")
    if tree.body and isinstance(tree.body[-1], ast.Expr):
        if len(tree.body) > 1:
            exec(compile(ast.Module(body=tree.body[:-1], type_ignores=[]), "<cell>", "exec"), ns, ns)
        expr = ast.Expression(tree.body[-1].value)  # type: ignore[arg-type]
        return eval(compile(expr, "<cell>", "eval"), ns, ns)
    else:
        exec(compile(tree, "<cell>", "exec"), ns, ns)
        return None

def _run_python(code: str, session: str) -> Dict[str, Any]:
    ns = _init_namespace(session)
    out_buf, err_buf = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(out_buf), contextlib.redirect_stderr(err_buf):
            value = _exec_with_last_expr(code, ns)
            ns["_"] = value
        return {"ok": True, "stdout": out_buf.getvalue(), "stderr": err_buf.getvalue(), "value": value}
    except Exception as e:
        return {
            "ok": False,
            "stdout": out_buf.getvalue(),
            "stderr": err_buf.getvalue(),
            "error": {
                "ename": type(e).__name__,
                "evalue": str(e),
                "traceback": traceback.format_exception(type(e), e, e.__traceback__),
            },
        }

def _run_shell(cmd: str) -> Dict[str, Any]:
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        ok = (res.returncode == 0)
        return {"ok": ok, "stdout": res.stdout, "stderr": res.stderr, "value": None} if ok else {
            "ok": False,
            "stdout": res.stdout,
            "stderr": res.stderr,
            "error": {"ename": "ShellError", "evalue": f"exit {res.returncode}", "traceback": []},
        }
    except Exception as e:
        return {
            "ok": False,
            "stdout": "",
            "stderr": "",
            "error": {"ename": type(e).__name__, "evalue": str(e), "traceback": traceback.format_exc().splitlines()},
        }

# ======================= Output packing (Jupyter) ======================
def _mk_stream(name: str, text: str) -> Dict[str, Any]:
    # add a trailing newline if missing
    if text is None:
        text = ""
    if not text.endswith("\n"):
        text += "\n"
    return {"type": "stream", "name": name, "text": text}

def _mk_execute_result(exec_count: Optional[int], val: Any) -> Dict[str, Any]:
    return {
        "type": "execute_result",
        "data": {"text/plain": repr(val)},
        "execution_count": exec_count,
        "metadata": {},
    }

def _mk_error(err: Dict[str, Any]) -> Dict[str, Any]:
    return {"type": "error", "ename": err.get("ename", ""), "evalue": err.get("evalue", ""), "traceback": err.get("traceback") or []}

def _prefix_each_line(text: str, rank: int) -> str:
    """Prefix every line of text with [rank i]."""
    if not text:
        return ""
    lines = text.splitlines()
    return "\n".join(f"[rank {rank:4d}] {line}" for line in lines if line.strip() != "") + "\n"

def _pack_outputs_per_rank(res: Dict[str, Any], exec_count: Optional[int], rank: int) -> List[Dict[str, Any]]:
    """
    Build the per-rank outputs. If truly empty (no stdout/stderr/value/error), return [].
    """
    outs: List[Dict[str, Any]] = []
    if not isinstance(res, dict):
        return outs

    has_any = False
    stdout = res.get("stdout")
    stderr = res.get("stderr")
    if stdout:
        has_any = True
        outs.append(_mk_stream("stdout", _prefix_each_line(stdout, rank)))
    if stderr:
        has_any = True
        outs.append(_mk_stream("stderr", _prefix_each_line(stderr, rank)))

    if res.get("ok"):
        if res.get("value") is not None:
            has_any = True
            # Value gets packed as-is, not line-prefixed (could be tensor, number, etc.)
            outs.append(_mk_execute_result(exec_count, res["value"]))
    else:
        has_any = True
        outs.append(_mk_error(res.get("error") or {}))

    return outs if has_any else []
    
def _pack_outputs_all_ranks(ranks: List[Dict[str, Any]], exec_count: Optional[int]) -> List[Dict[str, Any]]:
    """
    Compose a single outputs[] list that contains each rank's header + outputs,
    but SKIP ranks that have no output at all.
    """
    outs: List[Dict[str, Any]] = []
    for i, res in enumerate(ranks):
        per = _pack_outputs_per_rank(res, exec_count, i)
        if not per:  # no output for this rank; skip entirely
            continue
        #outs.append(_mk_stream("stdout", f"== rank {i} =="))
        outs.extend(per)
    return outs

# ======================== Collectives (broadcast/gather) ===============
def _broadcast_msg(msg: dict):
    if DEBUG_BCAST and dist.get_rank() == 0:
        keys = {k: ('<code>' if k == 'code' else v) for k, v in msg.items()}
        print(f"[rank0] MSG → broadcast: {keys}", flush=True)
    payload = [msg]
    dist.broadcast_object_list(payload, src=0, group=CTRL_PG)
    return payload[0]

def _gather_obj(obj: dict | list | None) -> list:
    outs = [None for _ in range(dist.get_world_size())]
    dist.all_gather_object(outs, obj, group=CTRL_PG)
    return outs

# ====================== Worker: handle a received message ==============
def _handle_message_on_this_rank(msg: Dict[str, Any]) -> Dict[str, Any]:
    action = str(msg.get("action", "")).lower()
    session_id = str(msg.get("session_id") or "default")

    if action in ("reset", "shutdown"):
        _namespaces.pop(session_id, None)
        return {"ok": True, "stdout": "", "stderr": "", "value": None}

    if action == "interrupt":
        return {"ok": True, "stdout": "", "stderr": "", "value": None}

    if action != "execute":
        return {"ok": False, "stdout": "", "stderr": "", "error": {"ename": "ValueError", "evalue": f"unknown action {action}", "traceback": []}}

    code = msg.get("code")
    if not isinstance(code, str):
        return {"ok": False, "stdout": "", "stderr": "", "error": {"ename": "TypeError", "evalue": "code must be str", "traceback": []}}
    if len(code.encode("utf-8")) > CODE_MAX_BYTES:
        return {"ok": False, "stdout": "", "stderr": "", "error": {"ename": "ValueError", "evalue": "code too large", "traceback": []}}

    s = code.strip()
    if s.startswith(("!", "%")):
        return _run_shell(s[1:].strip())
    else:
        return _run_python(code, session_id)

# ====================== Worker: Info ======================
def _show_info(exec_count: int | None = None) -> list[dict]:
    world = dist.get_world_size() if dist.is_initialized() else 1
    cuda  = torch.cuda.is_available()
    devs  = torch.cuda.device_count() if cuda else 0
    gen   = int(os.getenv("TORCHELASTIC_RESTART_COUNT", "0"))

    desc = (
        "Torch Cluster is a lightweight, FastAPI-based distributed execution layer "
        "built on PyTorch Distributed (TorchRun). It transforms a group of GPUs and "
        "nodes into a unified, interactive compute fabric accessible directly from "
        "a Jupyter notebook through the Kernel Agent. "
        "https://pypi.org/project/jupyter-kernel-agent/"
    )

    return [
        {
            "type": "execute_result",
            "data": {"text/plain": desc},
            "execution_count": exec_count,
            "metadata": {},
        },
        {
            "type": "stream",
            "name": "stdout",
            "text": f"world_size={world}, cuda={cuda}, device_count={devs}, generation={gen}\n",
        },
    ]


# ====================== Worker: Status ======================
def _show_status(exec_count: int | None = None) -> list[dict]:
    acquired = _dist_lock.acquire(blocking=False)
    if acquired:
        _dist_lock.release()

    world = dist.get_world_size() if dist.is_initialized() else 1
    busy  = not acquired
    summary = f"busy={busy}, world_size={world}"

    return [
        {
            "type": "stream",
            "name": "stdout",
            "text": summary + "\n",
        },
        {
            "type": "execute_result",
            "data": {"text/plain": "Cluster status: " + summary},
            "execution_count": exec_count,
            "metadata": {},
        },
    ]
# ============================ FastAPI app ==============================
def _build_app() -> FastAPI:
    app = FastAPI(title="kernel-agent cluster server", version="0.7.2")

    @app.exception_handler(StarletteHTTPException)
    async def http_exc_handler(request: Request, exc: StarletteHTTPException):
        if exc.status_code == 404:
            html_file = pathlib.Path("/index.html")
            if html_file.exists():
                return HTMLResponse(html_file.read_text(encoding="utf-8"), status_code=200)
            return HTMLResponse("<h1>README.html not found</h1>", status_code=404)
        return PlainTextResponse(str(exc.detail), status_code=exc.status_code)
    
    @app.get("/", response_class=HTMLResponse)
    def root():
        html_file = pathlib.Path("/index.html")   # adjust path if needed
        if html_file.exists():
            return html_file.read_text(encoding="utf-8")
        return "<h1>README.html not found</h1>"
        
    @app.post("/")
    async def kernel(req: Request):
        _require_auth(req)
        try:
            body = await req.json()
        except Exception:
            return JSONResponse({"ok": False, "error": "invalid JSON"}, status_code=400)

        if not isinstance(body, dict):
            return JSONResponse({"ok": False, "error": "invalid JSON"}, status_code=400)

        exec_count = body.get("execution_count")
        try:
            exec_count = int(exec_count) if exec_count is not None else None
        except Exception:
            exec_count = 0

        rid = uuid.uuid4().hex[:8]        
        print(f"session id {rid}")

        outs = None
        ok_all = False
        
        action = str(body.get("action") or "").lower()
        print(f"action is {action}")
        if action == "info":
            outs = _show_info(exec_count=exec_count)
            ok_all = True
        else:    
            with _dist_lock:
                # broadcast full body to all ranks
                body_bcast = dict(body)
                body_bcast.setdefault("request_id", rid)
                _broadcast_msg(body_bcast)
                # rank0 does the same handling locally
                res0 = _handle_message_on_this_rank(body_bcast)
                # gather per-rank results
                ranks: List[Dict[str, Any]] = _gather_obj(res0)
    
            # Merge only non-empty per-rank outputs
            outs = _pack_outputs_all_ranks(ranks, exec_count)
            ok_all = all((r.get("ok", True) if isinstance(r, dict) else True) for r in ranks)
                
        return {
            "ok": ok_all,
            "outputs": outs,  # may be [] if literally no rank produced output
            "execution_count": exec_count if body_bcast.get("action") == "execute" else None,
            "session_id": str(body_bcast.get("session_id") or "default"),
            "action": str(body_bcast.get("action") or ""),
            "request_id": rid,
            "world_size": dist.get_world_size() if dist.is_initialized() else 1,
            "ranks": ranks,  # optional: full per-rank results
        }
    
    @app.get("/health")
    def health():
        return {"ok": True}
    
    return app

# ====================== Rank workers main loop ========================
def _worker_loop():
    while True:
        payload = [None]
        dist.broadcast_object_list(payload, src=0, group=CTRL_PG)
        msg = payload[0] or {}
        if not isinstance(msg, dict):
            _ = _gather_obj({"ok": False, "stdout": "", "stderr": "", "error": {"ename": "TypeError", "evalue": "payload not dict", "traceback": []}})
            continue
        out = _handle_message_on_this_rank(msg)
        _ = _gather_obj(out)

# ============================ Entrypoint ==============================
def main(argv: Optional[List[str]] = None):
    global API_HOST, API_PORT, CODE_MAX_BYTES, DIST_TIMEOUT_SEC, ALLOWED_KEYS, CTRL_PG

    p = argparse.ArgumentParser(
        prog="torch_server",
        description="Torch Cluster Server for Kernel Agent (Authorization: Bearer <API_KEY>, endpoint: POST /)"
    )
    p.add_argument("--host", default="0.0.0.0", help="Bind host (default 0.0.0.0)")
    p.add_argument("--port", type=int, default=8080, help="Bind port (default 8080)")
    p.add_argument("--api_key", default=None, help="Comma-separated API keys")
    p.add_argument("--api_key_file", default=None, help="File with one API key per line")
    p.add_argument("--code_max_bytes", type=int, default=256 * 1024, help="Max code size (bytes)")
    p.add_argument("--dist_timeout", type=int, default=600, help="torch.distributed timeout (sec)")
    args = p.parse_args(argv)

    API_HOST, API_PORT = args.host, args.port
    CODE_MAX_BYTES = int(args.code_max_bytes)
    DIST_TIMEOUT_SEC = int(args.dist_timeout)

    keys: Set[str] = set()
    if args.api_key:
        keys.update(k.strip() for k in args.api_key.split(",") if k.strip())
    if args.api_key_file and os.path.exists(args.api_key_file):
        with open(args.api_key_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    keys.add(line)
    ALLOWED_KEYS = keys

    local_rank = int(os.getenv("LOCAL_RANK", "0"))
    has_cuda = torch.cuda.is_available()
    if has_cuda:
        n = torch.cuda.device_count()
        if local_rank >= n:
            print(f"[LOCAL_RANK={local_rank}] > visible cuda count ({n}) -> exit", flush=True)
            sys.exit(0)
        torch.cuda.set_device(local_rank)
        device = torch.device(f"cuda:{local_rank}")
        dist.init_process_group(
            backend="nccl",
            timeout=timedelta(seconds=DIST_TIMEOUT_SEC),
            device_id=device,
        )
    else:
        dist.init_process_group(
            backend="gloo",
            timeout=timedelta(seconds=DIST_TIMEOUT_SEC),
        )

    CTRL_PG = dist.new_group(backend=dist.Backend.GLOO)

    rank = dist.get_rank()
    if rank == 0:
        app = _build_app()
        try:
            uvicorn.run(app, host=API_HOST, port=API_PORT, log_level="info")
        finally:
            dist.destroy_process_group()
    else:
        try:
            _worker_loop()
        finally:
            dist.destroy_process_group()

if __name__ == "__main__":
    main()