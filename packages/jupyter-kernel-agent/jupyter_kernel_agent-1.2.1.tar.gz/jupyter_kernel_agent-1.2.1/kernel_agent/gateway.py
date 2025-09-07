# gateway.py
from __future__ import annotations

import json
import os
import time
import uuid
from typing import Iterator

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse

# Uses the shared Pydantic schemas
from kernel_agent.schemas import RPCRequest, RPCResponse, StreamOutput, ErrorOutput

app = FastAPI(title="SuperKernelGateway", version="0.2.0")

# -------- Config (env) --------
API_KEY = os.getenv("API_KEY", "").strip()   # if empty: no auth enforcement
CHANNEL = os.getenv("CHANNEL", "default")    # echoed in responses (request can also set channel)


# -------- Auth --------
def require_auth(req: Request):
    """Enforce Authorization: Bearer <API_KEY> if API_KEY is set."""
    if not API_KEY:
        return
    auth = req.headers.get("authorization") or req.headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = auth.split(None, 1)[1].strip()
    if token != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid bearer token")


# -------- SSE helper --------
def sse_event(event: str, data: dict | str) -> str:
    """Format a single SSE event frame."""
    if not isinstance(data, str):
        data = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\n" f"data: {data}\n\n"


# -------- Routes --------
@app.get("/", response_class=HTMLResponse)
def index():
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>SuperKernelGateway</title>
<style>body{{font-family:system-ui,Segoe UI,Arial,sans-serif;margin:2rem;line-height:1.5}}</style>
</head>
<body>
<h1>SuperKernelGateway</h1>
<p>Demo gateway that echoes inputs using Jupyter-style schemas (no actual code execution).</p>
<ul>
  <li><code>GET /health</code> → {"{ 'ok': true }"}</li>
  <li><code>POST /</code> → JSON (RPCRequest), returns RPCResponse (single echo)</li>
  <li><code>POST /sse</code> → Server-Sent Events (echoes the <code>code</code> 5×, 5s apart)</li>
</ul>
<p><b>Default channel</b>: <code>{CHANNEL}</code></p>
</body></html>"""

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/", response_model=RPCResponse, dependencies=[Depends(require_auth)])
async def rpc(body: RPCRequest):
    """
    Non-SSE fallback: returns a single 'stream' output echoing the provided 'code'.
    (SSE endpoint below streams 5 times with 5-second spacing.)
    """
    rid = uuid.uuid4().hex[:8]
    code = body.code or ""
    out = StreamOutput(name="stdout", text=f"{code}\n")

    return RPCResponse(
        ok=True,
        outputs=[out],
        execution_count=body.execution_count if (body.action or "").lower() == "execute" else None,
        session_id=body.session_id or "default",
        action=body.action or "",
        request_id=rid,
        world_size=1,
        ranks=[],
        channel=body.channel or CHANNEL,  # echo back for traceability
    )

@app.post("/sse", dependencies=[Depends(require_auth)])
async def rpc_sse(body: RPCRequest):
    """
    SSE endpoint: echoes 'code' as a stream output 5 times with 5-second delay between chunks.
    Finishes with a 'done' event. No real execution is performed.
    """
    rid = uuid.uuid4().hex[:8]
    session_id = body.session_id or "default"
    code = (body.code or "").rstrip("\n")
    exec_count = body.execution_count
    action = (body.action or "").lower()
    channel = body.channel or CHANNEL

    def gen() -> Iterator[str]:
        # Optional greeting for clients/proxies
        yield sse_event("hello", {"request_id": rid, "session_id": session_id})

        # Only special behavior for 'execute'; other actions just ack once
        if action == "execute":
            for i in range(5):
                # Build a Jupyter-style 'stream' output item
                chunk = StreamOutput(name="stdout", text=f"{i+1}/5: {code}\n").model_dump()
                yield sse_event("chunk", chunk)
                time.sleep(5)
            # Final envelope-like summary for the stream
            yield sse_event(
                "done",
                {
                    "ok": True,
                    "action": "execute",
                    "request_id": rid,
                    "session_id": session_id,
                    "execution_count": exec_count,
                    "world_size": 1,
                    "channel": channel,
                },
            )
            return

        # Non-execute actions: simple ack chunk, then done
        ack = StreamOutput(name="stdout", text=f"{action or 'noop'} ok\n").model_dump()
        yield sse_event("chunk", ack)
        yield sse_event(
            "done",
            {"ok": True, "action": action, "request_id": rid, "session_id": session_id, "world_size": 1, "channel": channel},
        )

    return StreamingResponse(gen(), media_type="text/event-stream")