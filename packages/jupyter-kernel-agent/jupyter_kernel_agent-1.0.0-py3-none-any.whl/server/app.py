from __future__ import annotations
from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
import hmac
import io, traceback, ast, uuid, asyncio, subprocess
from typing import Dict, Any, Optional, Set
from collections import defaultdict
from contextlib import redirect_stdout, redirect_stderr

app = FastAPI(title="torch-kernel server", version="0.5.0")

# Populated by server.cli
app.state.api_keys: Set[str] = set()

# Per-session state
_namespaces: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"__name__": "__main__"})
_locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
_counts: Dict[str, int] = defaultdict(int)

class KernelRPC(BaseModel):
    action: str
    session_id: Optional[str] = None
    code: Optional[str] = None
    execution_count: Optional[int] = None

def _require_auth(req: Request):
    api_keys: Set[str] = getattr(req.app.state, "api_keys", set())
    if not api_keys:
        return  # no auth configured

    auth = req.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        candidate = auth[7:].strip()
        for key in api_keys:
            if hmac.compare_digest(candidate, key):
                return
    raise HTTPException(status_code=401, detail="unauthorized")

def _exec_with_last_expr(code: str, g: Dict[str, Any]) -> Any:
    tree = ast.parse(code, mode="exec")
    if tree.body and isinstance(tree.body[-1], ast.Expr):
        if len(tree.body) > 1:
            exec(compile(ast.Module(body=tree.body[:-1], type_ignores=[]), "<cell>", "exec"), g, g)
        last_expr = ast.Expression(body=tree.body[-1].value)  # type: ignore[arg-type]
        return eval(compile(last_expr, "<cell>", "eval"), g, g)
    else:
        exec(compile(tree, "<cell>", "exec"), g, g)
        return None

def _mk_stream(name: str, text: str) -> Dict[str, Any]:
    return {"type": "stream", "name": name, "text": text}

def _mk_execute_result(exec_count: Optional[int], value: Any) -> Dict[str, Any]:
    return {
        "type": "execute_result",
        "data": {"text/plain": repr(value)},
        "execution_count": exec_count,
        "metadata": {},
    }

def _mk_error(exc: BaseException) -> Dict[str, Any]:
    return {
        "type": "error",
        "ename": type(exc).__name__,
        "evalue": str(exc),
        "traceback": traceback.format_exception(type(exc), exc, exc.__traceback__),
    }

def _clear_session(sid: str):
    _namespaces.pop(sid, None)
    _locks.pop(sid, None)
    _counts.pop(sid, None)

@app.post("/")
async def kernel(req: KernelRPC, _auth=Depends(_require_auth)):
    sid = req.session_id or str(uuid.uuid4())
    g = _namespaces[sid]
    lock = _locks[sid]

    if req.action in ("reset", "shutdown"):
        _clear_session(sid)
        return {"ok": True, "outputs": [], "execution_count": None, "session_id": sid, "action": req.action}

    if req.action == "interrupt":
        return {"ok": True, "outputs": [], "execution_count": None, "session_id": sid, "action": "interrupt"}

    if req.action != "execute":
        raise HTTPException(status_code=400, detail=f"unknown action '{req.action}'")

    if not isinstance(req.code, str):
        raise HTTPException(status_code=400, detail="code required for action=execute")

    if req.execution_count is None:
        _counts[sid] = _counts.get(sid, 0) + 1
        exec_count = _counts[sid]
    else:
        exec_count = req.execution_count
        _counts[sid] = exec_count

    outputs = []
    ok = True
    code = req.code.strip()

    if code.startswith(("!", "%")):
        try:
            res = subprocess.run(code[1:].strip(), shell=True, capture_output=True, text=True)
            if res.stdout: outputs.append(_mk_stream("stdout", res.stdout))
            if res.stderr: outputs.append(_mk_stream("stderr", res.stderr))
        except Exception as e:
            ok = False
            outputs.append(_mk_error(e))
        return {"ok": ok, "outputs": outputs, "execution_count": exec_count, "session_id": sid, "action": "execute"}

    stdout_buf, stderr_buf = io.StringIO(), io.StringIO()
    async with lock:
        try:
            with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
                value = _exec_with_last_expr(code, g)
                g["_"] = value
        except Exception as e:
            ok = False
            if (t := stdout_buf.getvalue()): outputs.append(_mk_stream("stdout", t))
            if (t := stderr_buf.getvalue()): outputs.append(_mk_stream("stderr", t))
            outputs.append(_mk_error(e))
        else:
            if (t := stdout_buf.getvalue()): outputs.append(_mk_stream("stdout", t))
            if (t := stderr_buf.getvalue()): outputs.append(_mk_stream("stderr", t))
            if value is not None: outputs.append(_mk_execute_result(exec_count, value))

    return {"ok": ok, "outputs": outputs, "execution_count": exec_count, "session_id": sid, "action": "execute"}