from __future__ import annotations
import argparse
import json
import sys
import shutil
from pathlib import Path
from typing import List, Optional

from jupyter_client.kernelspec import KernelSpecManager

APP = "kernel_agent"  # kernelspec dir prefix: kernel_agent-<name>


# --------------------------- Paths & utils ---------------------------

def _user_kernel_dir() -> Path:
    return Path(KernelSpecManager().user_kernel_dir)

def _prefix_kernel_dir(prefix: Path) -> Path:
    return prefix / "share" / "jupyter" / "kernels"

def _sys_prefix_dir() -> Path:
    return _prefix_kernel_dir(Path(sys.prefix))

def _kernel_folder_name(name: str) -> str:
    return f"{APP}-{name}"

def _resolve_base_dir(args) -> Path:
    # default: user dir; support --sys-prefix and --prefix like Jupyter
    if getattr(args, "sys_prefix", False):
        return _sys_prefix_dir()
    if getattr(args, "prefix", None):
        return _prefix_kernel_dir(Path(args.prefix))
    return _user_kernel_dir()

def _iter_kernels(base_dir: Path):
    if not base_dir.exists():
        return
    for p in sorted(base_dir.iterdir()):
        if p.is_dir() and p.name.startswith(f"{APP}-") and (p / "kernel.json").exists():
            yield p


# --------------------------- kernelspec I/O --------------------------

def _write_kernel_json(
    kdir: Path,
    *,
    display_name: str,
    endpoint: str,
    api_key: Optional[str],
    channel: Optional[str],
    sse: Optional[str],
    on_disconnect: Optional[str],
    timeout: Optional[float],
):
    """
    Create/overwrite kernel.json that launches our runtime:
      python -m kernel_agent.kernel -f {connection_file} --endpoint ... [--api_key ...] [--channel ...] ...
    """
    kdir.mkdir(parents=True, exist_ok=True)

    argv = [
        sys.executable, "-m", "kernel_agent.kernel",
        "-f", "{connection_file}",
        "--endpoint", endpoint,
        "--display-name", display_name,
    ]
    if api_key:
        argv += ["--api_key", api_key]
    if channel:
        argv += ["--channel", channel]
    if sse:
        argv += ["--sse", sse]  # "on" or "off"
    if on_disconnect:
        argv += ["--on-disconnect", on_disconnect]  # "hold" or "exit"
    if timeout is not None:
        argv += ["--timeout", str(timeout)]

    spec = {
        "argv": argv,
        "display_name": display_name,
        "language": "python",
    }
    (kdir / "kernel.json").write_text(json.dumps(spec, indent=2))


# ----------------------------- commands -----------------------------

def cmd_install(args):
    base = _resolve_base_dir(args)
    kdir = base / _kernel_folder_name(args.name)
    existed = kdir.exists()
    # I want the super kernel Image
    #display_name = args.display_name or f"SuperKernel ({args.name})"
    display_name = f"{args.name.upper()}\n(SuperKernel)"        
    _write_kernel_json(
        kdir,
        display_name=display_name,
        endpoint=args.endpoint,
        api_key=args.api_key,
        channel=args.channel,
        sse=args.sse,
        on_disconnect=args.on_disconnect,
        timeout=args.timeout,
    )
    print(("Updated" if existed else "Created") + f": {kdir}")
    # Show a quick summary:
    print("  display_name:", display_name)
    print("  endpoint    :", args.endpoint)
    print("  auth        :", "API key set" if bool(args.api_key) else "none")
    print("  channel     :", args.channel or "-")
    print("  sse         :", args.sse or "off")
    print("  on_disconnect:", args.on_disconnect)
    if args.timeout is not None:
        print("  timeout     :", args.timeout, "sec")

def cmd_list(args):
    base = _resolve_base_dir(args)
    found = False
    for kdir in _iter_kernels(base):
        found = True
        try:
            spec = json.loads((kdir / "kernel.json").read_text())
        except Exception:
            spec = {}
        display = spec.get("display_name", "(unknown)")
        argv = spec.get("argv", [])
        endpoint, api_key_set, channel, sse, on_dis, timeout = None, False, None, None, None, None

        if isinstance(argv, list):
            it = iter(enumerate(argv))
            for i, tok in it:
                if tok == "--endpoint" and i + 1 < len(argv):
                    endpoint = argv[i + 1]
                elif tok == "--api_key" and i + 1 < len(argv):
                    api_key_set = True
                elif tok == "--channel" and i + 1 < len(argv):
                    channel = argv[i + 1]
                elif tok == "--sse" and i + 1 < len(argv):
                    sse = argv[i + 1]
                elif tok == "--on-disconnect" and i + 1 < len(argv):
                    on_dis = argv[i + 1]
                elif tok == "--timeout" and i + 1 < len(argv):
                    timeout = argv[i + 1]

        print(f"- name: {kdir.name[len(APP)+1:]}")  # strip "kernel_agent-"
        print(f"  display_name : {display}")
        if endpoint:
            print(f"  endpoint     : {endpoint}")
        print(f"  auth         : {'API key set' if api_key_set else 'none'}")
        print(f"  channel      : {channel or '-'}")
        print(f"  sse          : {sse or 'off'}")
        print(f"  on_disconnect: {on_dis or 'hold'}")
        if timeout:
            print(f"  timeout      : {timeout} sec")
        print(f"  path         : {kdir}\n")
    if not found:
        print(f"(no {APP} kernels found in)", base)

def cmd_delete(args):
    base = _resolve_base_dir(args)
    targets: List[Path] = []
    if args.all:
        targets = list(_iter_kernels(base))
        if not targets:
            print("(nothing to delete)")
            return
    else:
        if not args.name:
            print("Error: --name required (or --all)", file=sys.stderr)
            sys.exit(2)
        kdir = base / _kernel_folder_name(args.name)
        if not kdir.exists():
            print(f"Not found: {kdir}", file=sys.stderr)
            sys.exit(1)
        targets = [kdir]
    for t in targets:
        shutil.rmtree(t, ignore_errors=True)
        print(f"Deleted: {t}")


# ------------------------------ CLI ---------------------------------

def _add_scope_flags(p: argparse.ArgumentParser):
    g = p.add_mutually_exclusive_group()
    g.add_argument("--user", action="store_true", help="Install to user kernels dir (default)")
    g.add_argument("--sys-prefix", action="store_true", help="Install to sys.prefix kernels dir (good for JupyterHub images)")
    g.add_argument("--prefix", type=str, help="Install to <prefix>/share/jupyter/kernels")
    return p

def main(argv: List[str] | None = None):
    ap = argparse.ArgumentParser(
        prog="kernel_agent",
        description="Install and manage Kernel Agent Jupyter kernelspecs.",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    # install
    p_ins = sub.add_parser("install", help="Install (or update) a kernelspec for a remote endpoint")
    p_ins.add_argument("--endpoint", required=True, help="RPC URL root, e.g. http://host:8000 (POST /, optional /sse)")
    p_ins.add_argument("--name", required=True, help="Name suffix → kernel_agent-<name>")
    p_ins.add_argument("--display-name", default=None, help="Jupyter display name (default: 'Kernel Agent (<name>)')")
    p_ins.add_argument("--api_key", help="API key for Authorization: Bearer …")
    p_ins.add_argument("--channel", default=None, help="Logical routing channel included in every request")
    p_ins.add_argument("--sse", choices=["on", "off"], default="on", help="Enable Server-Sent Events streaming")
    p_ins.add_argument("--on-disconnect", choices=["hold", "exit"], default="hold", help="Behavior if remote disconnects")
    p_ins.add_argument("--timeout", type=float, default=None, help="HTTP timeout seconds (default 300)")
    _add_scope_flags(p_ins)
    p_ins.set_defaults(func=cmd_install)

    # list
    p_ls = sub.add_parser("list", help="List installed kernel_agent kernels")
    _add_scope_flags(p_ls)
    p_ls.set_defaults(func=cmd_list)

    # delete
    p_rm = sub.add_parser("delete", help="Delete kernelspec(s)")
    g = p_rm.add_mutually_exclusive_group()
    g.add_argument("--name", help="Name suffix")
    g.add_argument("--all", action="store_true", help="Delete all kernel_agent-* kernels")
    _add_scope_flags(p_rm)
    p_rm.set_defaults(func=cmd_delete)

    args = ap.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()