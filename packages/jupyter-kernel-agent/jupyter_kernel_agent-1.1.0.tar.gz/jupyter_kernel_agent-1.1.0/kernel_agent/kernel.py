from __future__ import annotations
from ipykernel.kernelbase import Kernel
from ipykernel.kernelapp import IPKernelApp

import argparse
import json
import os
import sys
import uuid
import traceback
from typing import Any, Dict, Optional

import requests
from requests.exceptions import RequestException, Timeout, ConnectionError as ReqConnectionError

from .schemas import RPCResponse, OutputItem  # Pydantic schemas for POST /

try:
    from . import __version__
except Exception:
    __version__ = "0.6.0"


# ----------------------------- HTTP helper -----------------------------

def _post_json(url: str, body: Dict[str, Any], api_key: str | None, timeout: float) -> Dict[str, Any]:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    r = requests.post(url, headers=headers, json=body, timeout=timeout)
    r.raise_for_status()
    try:
        return r.json()
    except Exception:
        # Some servers may return text/plain; wrap minimally
        return {"ok": True, "stdout": r.text}


# =============================== Kernel ================================

class KernelAgent(Kernel):
    implementation = "kernel_agent"
    implementation_version = __version__
    language = "python"
    language_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    language_info = {"name": "python", "mimetype": "text/x-python", "file_extension": ".py"}
    banner = (
        "Kernel Agent (HTTP) — API key auth; actions: "
        "%info, %status, %reset, %shutdown, %reconnect, %sse on|off"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.endpoint = os.environ.get("ENDPOINT") or ""
        self.session_id = os.environ.get("KERNEL_AGENT_SESSION_ID") or str(uuid.uuid4())
        self.display_name = os.environ.get("KERNEL_AGENT_DISPLAY_NAME") or "Kernel Agent"
        self.api_key = os.environ.get("KERNEL_AGENT_API_KEY") or None
        try:
            self.timeout = float(os.environ.get("KERNEL_AGENT_TIMEOUT") or "300")
        except Exception:
            self.timeout = 300.0
        self.on_disconnect = (os.environ.get("KERNEL_AGENT_ON_DISCONNECT") or "hold").lower()
        # Channel: optional routing tag sent with every request
        self.channel = os.environ.get("KERNEL_AGENT_CHANNEL") or None
        # SSE is off by default for compatibility; enable with env/CLI/%sse
        self.use_sse = (os.environ.get("KERNEL_AGENT_SSE", "off").lower() == "on")

        self._disconnected = False
        self._send_welcome_banner()

    # ------------------------- RPC helpers -------------------------

    def _rpc(self, action: str, **extra) -> Dict[str, Any]:
        if not self.endpoint:
            raise RuntimeError("ENDPOINT is not set")
        payload = {"action": action, "session_id": self.session_id, **extra}
        if self.channel:
            payload["channel"] = self.channel
        return _post_json(self.endpoint, payload, self.api_key, timeout=self.timeout)

    def _rpc_stream(self, action: str, **extra) -> None:
        """
        SSE streaming call. If /sse is unavailable, silently falls back to normal RPC.
        Streams 'chunk' outputs progressively; ignores 'hello/heartbeat/done'.
        """
        if not self.endpoint:
            raise RuntimeError("ENDPOINT is not set")

        sse_url = self.endpoint.rstrip("/")
        if not sse_url.endswith("/sse"):
            sse_url = sse_url + "/sse"

        headers = {"Accept": "text/event-stream"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {"action": action, "session_id": self.session_id, **extra}
        if self.channel:
            payload["channel"] = self.channel

        try:
            with requests.post(sse_url, headers=headers, json=payload, stream=True, timeout=self.timeout) as r:
                ctype = r.headers.get("content-type", "").split(";")[0].strip().lower()
                if r.status_code >= 400 or ctype != "text/event-stream":
                    raise RequestException(f"SSE not available (HTTP {r.status_code})")

                current_event = None
                for raw in r.iter_lines(decode_unicode=True):
                    if not raw:
                        continue
                    if raw.startswith("event:"):
                        current_event = raw.split(":", 1)[1].strip()
                        continue
                    if raw.startswith("data:"):
                        payload_str = raw[5:].lstrip()
                    else:
                        payload_str = raw  # allow plain JSON lines
                    try:
                        msg = json.loads(payload_str)
                    except Exception:
                        continue

                    # If chunk is a Jupyter-style output, validate & render
                    if isinstance(msg, dict) and "type" in msg:
                        try:
                            out = OutputItem.model_validate(msg)
                            self._emit_output_item(out)
                        except Exception:
                            self._emit_output_dict(msg)
                    # Ignore hello/heartbeat/done markers
            return
        except Exception:
            # Fallback to non-streaming RPC
            resp = self._rpc(action, **extra)
            self._emit_response(resp)

    # ----------------------- Emit/Render helpers --------------------

    def _emit_output_item(self, out: OutputItem) -> None:
        typ = out.type
        if typ == "stream":
            self._write_stream(getattr(out, "name", "stdout"), getattr(out, "text", ""))
        elif typ == "execute_result":
            self.send_response(
                self.iopub_socket,
                "execute_result",
                {
                    "execution_count": self.execution_count,
                    "data": out.data,
                    "metadata": out.metadata or {},
                },
            )
        elif typ == "display_data":
            self._send_display_data(out.data, out.metadata or {})
        elif typ == "error":
            tb = out.traceback or []
            if tb:
                self._write_stream("stderr", "".join(tb))

    def _emit_output_dict(self, out: Dict[str, Any]) -> None:
        typ = out.get("type")
        if typ == "stream":
            self._write_stream(out.get("name", "stdout"), out.get("text", ""))
        elif typ == "execute_result":
            self.send_response(
                self.iopub_socket,
                "execute_result",
                {
                    "execution_count": self.execution_count,
                    "data": out.get("data", {}) or {},
                    "metadata": out.get("metadata", {}) or {},
                },
            )
        elif typ == "display_data":
            self._send_display_data(out.get("data", {}) or {}, out.get("metadata", {}) or {})
        elif typ == "error":
            tb = out.get("traceback")
            if tb:
                self._write_stream("stderr", "".join(tb))

    def _emit_response(self, resp: Dict[str, Any]) -> None:
        # Preferred: validate & normalize via RPCResponse
        try:
            model = RPCResponse.model_validate(resp)
            for out in model.outputs:
                self._emit_output_item(out)
            return
        except Exception:
            # Fallback to legacy dict handling to keep full compatibility
            pass

        # Legacy path (unchanged)
        if isinstance(resp, dict):
            if resp.get("stdout"):
                self._write_stream("stdout", resp["stdout"])
            if resp.get("stderr"):
                self._write_stream("stderr", resp["stderr"])
        outs = resp.get("outputs") if isinstance(resp, dict) else None
        if isinstance(outs, list):
            for out in outs:
                if isinstance(out, dict):
                    self._emit_output_dict(out)

    def _send_display_data(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> None:
        self.send_response(self.iopub_socket, "display_data", {"data": data, "metadata": metadata or {}})

    def _write_stream(self, name: str, text: str) -> None:
        self.send_response(self.iopub_socket, "stream", {"name": name, "text": text})

    # ------------------------- UX helpers --------------------------

    def _send_welcome_banner(self):
        md = (
            f"### {self.display_name}\n"
            f"- **Version**: `{__version__}`\n"
            f"- **Endpoint**: `{self.endpoint}`\n"
            f"- **Session**: `{self.session_id}`\n"
            f"- **Channel**: `{self.channel or '-'}`\n"
            f"- **Auth**: Authorization: Bearer &lt;API_KEY&gt;\n"
            f"- **Actions**: %info, %status, %reset, %shutdown, %reconnect, %sse on|off\n"
            f"- **SSE**: {'enabled' if self.use_sse else 'disabled'} (toggle with `%sse on|off`)\n"
        )
        self.send_response(
            self.iopub_socket,
            "display_data",
            {"data": {"text/markdown": md}, "metadata": {}, "transient": {"display_id": "kernel_agent_welcome"}},
        )

    def _show_disconnected(self, why: str):
        self._disconnected = True
        md = (
            f"### 🔌 Disconnected\n"
            f"- Endpoint: `{self.endpoint}`\n"
            f"- Reason: {why}\n"
            f"Kernel is holding. Use %reconnect or restart."
        )
        self.send_response(
            self.iopub_socket,
            "display_data",
            {"data": {"text/markdown": md}, "metadata": {}, "transient": {"display_id": "kernel_agent_status"}},
        )

    def _handle_disconnect(self, err: BaseException):
        if self.on_disconnect == "exit":
            self._write_stream("stderr", f"[kernel-agent] Remote unreachable: {err}\n")
            try:
                super().do_shutdown(restart=False)
            finally:
                sys.exit(1)
        self._show_disconnected(f"{type(err).__name__}: {err}")

    # ------------------------- Action parser -----------------------

    def _parse_action(self, code: str) -> tuple[Optional[str], dict]:
        """
        Map user-entered lines to server actions.
        Returns (action|None, extra_payload_dict).
        """
        s = (code or "").strip()

        # SSE toggle is local (no server action)
        if s.startswith("%sse"):
            parts = s.split()
            if len(parts) == 2 and parts[1].lower() in {"on", "off"}:
                self.use_sse = (parts[1].lower() == "on")
                self._write_stream("stdout", f"[kernel-agent] SSE {'enabled' if self.use_sse else 'disabled'}\n")
            else:
                self._write_stream("stdout", "[kernel-agent] usage: %sse on|off\n")
            # show live status after toggling
            return "status", {"code": "%status", "execution_count": self.execution_count}

        if s == "%info":
            return "info", {"code": "%info", "execution_count": self.execution_count}
        if s == "%status":
            return "status", {"code": "%status", "execution_count": self.execution_count}
        if s == "%reset":
            return "reset", {}
        if s == "%shutdown":
            return "shutdown", {}
        if s == "%reconnect":
            return "interrupt", {}

        # Not a command: treat as executable code
        return None, {}

    # --------------------------- Execute ---------------------------

    def do_execute(
        self,
        code: str,
        silent: bool,
        store_history: bool = True,
        user_expressions: dict | None = None,
        allow_stdin: bool = False,
    ) -> Dict[str, Any]:
        if self._disconnected:
            self._write_stream("stderr", "[kernel-agent] Disconnected: use %reconnect\n")
            return {"status": "error", "execution_count": self.execution_count, "payload": [], "user_expressions": {}}
        if silent:
            return {"status": "ok", "execution_count": self.execution_count, "payload": [], "user_expressions": {}}

        try:
            action, extra = self._parse_action(code)

            # 1) Action branch: always POST to server
            if action is not None:
                if action in {"info", "status"}:
                    if self.use_sse:
                        self._rpc_stream(action, **extra)
                    else:
                        resp = self._rpc(action, **extra)
                        self._emit_response(resp)
                    return {"status": "ok", "execution_count": self.execution_count, "payload": [], "user_expressions": {}}

                if action == "reset":
                    try:
                        resp = self._rpc("reset")
                        self._emit_response(resp)
                    except Exception:
                        pass
                    old = self.session_id
                    self.session_id = str(uuid.uuid4())
                    self._disconnected = False
                    self._write_stream("stdout", f"[kernel-agent] Reset session {old} → {self.session_id}\n")
                    self._send_welcome_banner()
                    return {"status": "ok", "execution_count": self.execution_count, "payload": [], "user_expressions": {}}

                if action == "shutdown":
                    try:
                        resp = self._rpc("shutdown")
                        self._emit_response(resp)
                    except Exception:
                        pass
                    self._write_stream("stdout", "[kernel-agent] Remote session shutdown requested.\n")
                    return {"status": "ok", "execution_count": self.execution_count, "payload": [], "user_expressions": {}}

                if action == "interrupt":
                    try:
                        resp = self._rpc("interrupt")
                        self._emit_response(resp)
                        self._disconnected = False
                        self._write_stream("stdout", f"[kernel-agent] Reconnected to {self.endpoint}\n")
                        self._send_welcome_banner()
                    except Exception as e:
                        self._show_disconnected(f"Reconnect failed: {e}")
                    return {"status": "ok", "execution_count": self.execution_count, "payload": [], "user_expressions": {}}

            # 2) Otherwise: normal code execution
            if self.use_sse:
                self._rpc_stream("execute", code=code, execution_count=self.execution_count)
            else:
                resp = self._rpc("execute", code=code, execution_count=self.execution_count)
                self._emit_response(resp)

            return {"status": "ok", "execution_count": self.execution_count, "payload": [], "user_expressions": {}}

        except (ReqConnectionError, Timeout, RequestException) as e:
            self._handle_disconnect(e)
            return {"status": "error", "execution_count": self.execution_count, "payload": [], "user_expressions": {}}
        except Exception:
            self._write_stream("stderr", traceback.format_exc())
            return {"status": "error", "execution_count": self.execution_count, "payload": [], "user_expressions": {}}

    # --------------------------- Shutdown --------------------------

    def do_shutdown(self, restart: bool = False) -> bool:
        try:
            self._rpc("reset" if restart else "shutdown")
        except Exception:
            pass
        if restart:
            old = self.session_id
            self.session_id = str(uuid.uuid4())
            self._disconnected = False
            self._write_stream("stdout", f"[kernel-agent] Restarted. New session {self.session_id} (was {old})\n")
            self._send_welcome_banner()
        return super().do_shutdown(restart=restart)


# ------------------------- CLI bootstrap ---------------------------

def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m kernel_agent.kernel",
        description="Kernel Agent (HTTP) — remote execution with API key auth. Optional SSE streaming.",
    )
    p.add_argument("--endpoint", required=True, help="RPC URL root, e.g. http://host:8000 (POST /, optional /sse)")
    p.add_argument("--api_key", default=None, help="API key for Authorization: Bearer …")
    p.add_argument("--timeout", type=float, default=None, help="HTTP timeout seconds (default 300)")
    p.add_argument("--display-name", default=None, help="Banner display name")
    p.add_argument("--on-disconnect", choices=["hold", "exit"], default="hold")
    p.add_argument("--sse", choices=["on", "off"], default=None, help="Enable Server-Sent Events streaming")
    p.add_argument("--channel", default=None, help="Logical routing channel to include in every request")  # NEW
    return p


def main(argv: list[str] | None = None) -> None:
    args, rest = _build_arg_parser().parse_known_args(argv if argv is not None else sys.argv[1:])
    os.environ["ENDPOINT"] = args.endpoint
    if args.api_key:
        os.environ["KERNEL_AGENT_API_KEY"] = args.api_key
    if args.timeout:
        os.environ["KERNEL_AGENT_TIMEOUT"] = str(args.timeout)
    if args.display_name:
        os.environ["KERNEL_AGENT_DISPLAY_NAME"] = args.display_name
    os.environ["KERNEL_AGENT_ON_DISCONNECT"] = args.on_disconnect
    if args.sse:
        os.environ["KERNEL_AGENT_SSE"] = args.sse  # "on" or "off"
    if args.channel:
        os.environ["KERNEL_AGENT_CHANNEL"] = args.channel  # store so __init__ picks it up
    IPKernelApp.launch_instance(kernel_class=KernelAgent, argv=rest)


if __name__ == "__main__":
    main()