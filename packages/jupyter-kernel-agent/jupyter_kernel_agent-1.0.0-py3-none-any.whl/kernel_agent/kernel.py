from __future__ import annotations
from ipykernel.kernelbase import Kernel
from ipykernel.kernelapp import IPKernelApp

import argparse
import json
import os
import sys
import uuid
import traceback
from typing import Any, Dict

import requests
from requests.exceptions import RequestException, Timeout, ConnectionError as ReqConnectionError

try:
    from . import __version__
except Exception:
    __version__ = "0.6.0"


def _post_json(url: str, body: Dict[str, Any], api_key: str | None, timeout: float) -> Dict[str, Any]:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    r = requests.post(url, headers=headers, json=body, timeout=timeout)
    r.raise_for_status()
    try:
        return r.json()
    except Exception:
        return {"ok": True, "stdout": r.text}


class KernelAgent(Kernel):
    implementation = "kernel_agent"
    implementation_version = __version__
    language = "python"
    language_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    language_info = {"name": "python", "mimetype": "text/x-python", "file_extension": ".py"}
    banner = "Kernel Agent (HTTP) — API key auth; magics: %reset, %shutdown, %welcome, %reconnect"

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
        self._disconnected = False
        self._send_welcome_banner()

    def _rpc(self, action: str, **extra) -> Dict[str, Any]:
        if not self.endpoint:
            raise RuntimeError("ENDPOINT is not set")
        payload = {"action": action, "session_id": self.session_id, **extra}
        return _post_json(self.endpoint, payload, self.api_key, timeout=self.timeout)

    def _emit_response(self, resp: Dict[str, Any]) -> None:
        if isinstance(resp, dict):
            if resp.get("stdout"):
                self._write_stream("stdout", resp["stdout"])
            if resp.get("stderr"):
                self._write_stream("stderr", resp["stderr"])
        outs = resp.get("outputs") if isinstance(resp, dict) else None
        if isinstance(outs, list):
            for out in outs:
                typ = out.get("type")
                if typ == "stream":
                    self._write_stream(out.get("name", "stdout"), out.get("text", ""))
                elif typ == "execute_result":
                    self.send_response(
                        self.iopub_socket,
                        "execute_result",
                        {"execution_count": self.execution_count, "data": out.get("data", {}), "metadata": {}},
                    )
                elif typ == "error":
                    tb = out.get("traceback")
                    if tb:
                        self._write_stream("stderr", "".join(tb))

    def _write_stream(self, name: str, text: str) -> None:
        self.send_response(self.iopub_socket, "stream", {"name": name, "text": text})

    def _send_welcome_banner(self):
        md = (
            f"### {self.display_name}\n"
            f"- **Endpoint**: `{self.endpoint}`\n"
            f"- **Session**: `{self.session_id}`\n"
            f"- **Auth**: Authorization: Bearer <API_KEY>\n"
            f"- **Magics**: %reset, %shutdown, %welcome, %reconnect\n"
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

    def _maybe_magic(self, code: str) -> bool:
        s = code.strip()
        if s in {"%reset"}:
            try:
                self._rpc("reset")
            except Exception:
                pass
            old = self.session_id
            self.session_id = str(uuid.uuid4())
            self._disconnected = False
            self._write_stream("stdout", f"[kernel-agent] Reset session {old} → {self.session_id}\n")
            self._send_welcome_banner()
            return True
        if s in {"%shutdown"}:
            try:
                self._rpc("shutdown")
            except Exception:
                pass
            self._write_stream("stdout", "[kernel-agent] Remote session shutdown requested.\n")
            return True
        if s in {"%welcome"}:
            self._send_welcome_banner()
            return True
        if s in {"%reconnect"}:
            try:
                self._rpc("interrupt")
                self._disconnected = False
                self._write_stream("stdout", f"[kernel-agent] Reconnected to {self.endpoint}\n")
                self._send_welcome_banner()
            except Exception as e:
                self._show_disconnected(f"Reconnect failed: {e}")
            return True
        return False

    def do_execute(self, code: str, silent: bool, store_history: bool = True,
                   user_expressions: dict | None = None, allow_stdin: bool = False) -> Dict[str, Any]:
        if self._maybe_magic(code):
            return {"status": "ok", "execution_count": self.execution_count, "payload": [], "user_expressions": {}}
        if self._disconnected:
            self._write_stream("stderr", "[kernel-agent] Disconnected: use %reconnect\n")
            return {"status": "error", "execution_count": self.execution_count, "payload": [], "user_expressions": {}}
        if silent:
            return {"status": "ok", "execution_count": self.execution_count, "payload": [], "user_expressions": {}}
        try:
            resp = self._rpc("execute", code=code, execution_count=self.execution_count)
            self._emit_response(resp)
            status = "ok" if (isinstance(resp, dict) and resp.get("ok", True)) else "error"
            return {"status": status, "execution_count": self.execution_count, "payload": [], "user_expressions": {}}
        except (ReqConnectionError, Timeout, RequestException) as e:
            self._handle_disconnect(e)
            return {"status": "error", "execution_count": self.execution_count, "payload": [], "user_expressions": {}}
        except Exception:
            self._write_stream("stderr", traceback.format_exc())
            return {"status": "error", "execution_count": self.execution_count, "payload": [], "user_expressions": {}}

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


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m kernel_agent.kernel",
        description="Kernel Agent (HTTP) — remote execution with API key auth.",
    )
    p.add_argument("--endpoint", required=True, help="RPC URL, e.g. http://host:8000/kernel")
    p.add_argument("--api_key", default=None, help="API key for Authorization: Bearer …")
    p.add_argument("--timeout", type=float, default=None, help="HTTP timeout seconds (default 300)")
    p.add_argument("--display-name", default=None, help="Banner display name")
    p.add_argument("--on-disconnect", choices=["hold", "exit"], default="hold")
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
    IPKernelApp.launch_instance(kernel_class=KernelAgent, argv=rest)


if __name__ == "__main__":
    main()