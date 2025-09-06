from __future__ import annotations
import argparse
import json
import sys
import shutil
from pathlib import Path
from typing import List
from jupyter_client.kernelspec import KernelSpecManager

APP = "kernel_agent"  # kernelspec dir prefix: kernel_agent-<name>


def _user_kernel_dir() -> Path:
    return Path(KernelSpecManager().user_kernel_dir)


def _prefix_kernel_dir(prefix: Path) -> Path:
    return prefix / "share" / "jupyter" / "kernels"


def _sys_prefix_dir() -> Path:
    return _prefix_kernel_dir(Path(sys.prefix))


def _kernel_folder_name(name: str) -> str:
    return f"{APP}-{name}"


def _write_kernel_json(kdir: Path, display_name: str, endpoint: str, api_key: str | None):
    kdir.mkdir(parents=True, exist_ok=True)
    argv = [
        sys.executable, "-m", "kernel_agent.kernel",
        "-f", "{connection_file}",
        "--endpoint", endpoint,
        "--display-name", display_name,
    ]
    if api_key:
        argv += ["--api_key", api_key]
    spec = {"argv": argv, "display_name": display_name, "language": "python"}
    (kdir / "kernel.json").write_text(json.dumps(spec, indent=2))


def _resolve_base_dir(args) -> Path:
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


def cmd_install(args):
    base = _resolve_base_dir(args)
    kdir = base / _kernel_folder_name(args.name)
    existed = kdir.exists()
    _write_kernel_json(kdir, display_name=args.name, endpoint=args.endpoint, api_key=args.api_key)
    print(("Updated" if existed else "Created") + f": {kdir}")


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
        endpoint, api_key_set = None, False
        if isinstance(argv, list):
            for i, tok in enumerate(argv):
                if tok == "--endpoint" and i + 1 < len(argv):
                    endpoint = argv[i + 1]
                if tok == "--api_key" and i + 1 < len(argv):
                    api_key_set = True
        print(f"- name: {kdir.name[len(APP)+1:]}")  # strip prefix
        print(f"  display_name: {display}")
        if endpoint:
            print(f"  endpoint: {endpoint}")
        print(f"  auth: {'API key set' if api_key_set else 'none'}")
        print(f"  path: {kdir}\n")
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


def _add_scope_flags(p: argparse.ArgumentParser):
    g = p.add_mutually_exclusive_group()
    g.add_argument("--user", action="store_true", help="User kernels dir (default)")
    g.add_argument("--sys-prefix", action="store_true", help="sys.prefix kernels dir (for JupyterHub images)")
    g.add_argument("--prefix", type=str, help="Custom <prefix>/share/jupyter/kernels")
    return p


def main(argv: List[str] | None = None):
    ap = argparse.ArgumentParser(
        prog="kernel_agent",
        description="Install and manage Kernel Agent Jupyter kernelspecs.",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_ins = sub.add_parser("install", help="Install a kernelspec for a remote endpoint")
    p_ins.add_argument("--endpoint", required=True, help="RPC URL, e.g. http://host:8000/kernel")
    p_ins.add_argument("--name", required=True, help="Name suffix → kernel_agent-<name>")
    p_ins.add_argument("--api_key", help="API key for Authorization: Bearer …")
    _add_scope_flags(p_ins)
    p_ins.set_defaults(func=cmd_install)

    p_ls = sub.add_parser("list", help="List installed kernel_agent kernels")
    _add_scope_flags(p_ls)
    p_ls.set_defaults(func=cmd_list)

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