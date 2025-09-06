import argparse
import os
import re
import sys
from pathlib import Path

import requests
from importlib.metadata import PackageNotFoundError, version as pkg_version


def _to_snake(name: str) -> str:
    """Convert a name to snake_case suitable for env vars."""
    name = re.sub(r"[^0-9a-zA-Z]+", "_", name)
    name = re.sub(r"(?<!^)(?=[A-Z])", "_", name)
    return name.strip("_").lower()


def fetch_agents() -> list[dict]:
    """Return a list of agents for the authenticated user."""
    token = os.environ.get("HUROZO_API_TOKEN")
    if not token:
        return []
    base_uri = os.environ.get("HUROZO_SERVER_URI", "https://app.hurozo.com").rstrip("/")
    try:
        resp = requests.get(
            f"{base_uri}/api/agents",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        if resp.ok:
            data = resp.json() or {}
            return data.get("agents", [])
    except Exception:
        pass
    return []


def _fetch_agent_inputs(agent_id: str) -> list[str]:
    """Return a list of input keys for a saved agent id.

    Tries GET /api/agents/<agent_id> and extracts extra.inputs (or top-level inputs) keys.
    Returns an empty list on any error or if none are defined.
    """
    token = os.environ.get("HUROZO_API_TOKEN")
    if not token:
        return []
    base_uri = os.environ.get("HUROZO_SERVER_URI", "https://app.hurozo.com").rstrip("/")
    try:
        resp = requests.get(
            f"{base_uri}/api/agents/{agent_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        if not resp.ok:
            return []
        data = resp.json() or {}
        agent = data.get("agent") or {}
        inputs = (agent.get("extra", {}) or {}).get("inputs") or agent.get("inputs") or []
        keys: list[str] = []
        for inp in inputs:
            key = inp.get("key") or inp.get("name")
            if key and key not in keys:
                keys.append(str(key))
        return keys
    except Exception:
        return []


def init_agent(dirname: str, agents: list[dict] | None = None) -> None:
    """Scaffold a minimal agent project.

    - Creates requirements.txt and main.py
    - If agents are provided (from the API selection), it will:
      - Instantiate each by display name using hurozo.Agent (name->uuid resolver is built-in)
      - Prefill input keys by querying /api/agents/<id>
      - Call .run() for every instantiated agent
    """
    target = Path(dirname)
    target.mkdir(parents=True, exist_ok=True)

    (target / "requirements.txt").write_text("hurozo\npython-dotenv\nrequests\n")

    # Prepare main.py contents
    agent_blocks: list[str] = []
    inputs_blocks: list[str] = []
    run_blocks: list[str] = []
    if agents:
        for ag in agents:
            display_name = ag.get("name", "agent")
            agent_var = _to_snake(display_name) or "agent"
            agent_blocks.append(f"{agent_var} = Agent('{display_name}')")
            # discover inputs
            ag_id = ag.get("id") or ""
            input_keys = _fetch_agent_inputs(ag_id) if ag_id else []
            if input_keys:
                # Create a readable example mapping
                pairs = ",\n        ".join([f"\"{k}\": \"Some input {i+1}\"" for i, k in enumerate(input_keys)])
                inputs_blocks.append(f"    {agent_var}.input({{\n        {pairs}\n    }})")
            else:
                inputs_blocks.append(f"    {agent_var}.input({{}})")
            run_blocks.append(f"    print({agent_var}.run())")
    else:
        agent_blocks.append("agent = Agent('Your Agent Name')  # display name; resolved to UUID at runtime")
        inputs_blocks.append("    agent.input({})")
        run_blocks.append("    print(agent.run())")

    agent_init_block = "\n".join(agent_blocks)
    inputs_block_joined = "\n".join(inputs_blocks)
    runs_block_joined = "\n".join(run_blocks)
    script = f"""from dotenv import load_dotenv
from hurozo import Agent

load_dotenv()  # Load environment variables from .env if present

{agent_init_block}

def main():
{inputs_block_joined}
{runs_block_joined}


if __name__ == '__main__':
    main()
"""
    (target / "main.py").write_text(script)

    # Create an .env with a token placeholder (do not overwrite if present)
    env_path = target / ".env"
    if not env_path.exists():
        env_path.write_text('# set HUROZO_API_TOKEN=""\n')

    print(_green(f"Initialized project in {target}"))


def _read_key() -> str:
    """Read a single keypress from stdin (raw), cross-platform best-effort.

    - Normal keys return a one-character string.
    - Arrow keys and similar return a full escape sequence like "\x1b[A".
    """
    try:
        import msvcrt  # type: ignore

        ch = msvcrt.getwch()
        # Normalize Windows special keys to ANSI-like sequences the UI understands
        if ch in ("\x00", "\xe0"):
            second = msvcrt.getwch()
            mapping = {
                "H": "\x1b[A",  # Up
                "P": "\x1b[B",  # Down
                "M": "\x1b[C",  # Right
                "K": "\x1b[D",  # Left
            }
            seq = mapping.get(second, ch + second)
            return seq
        return ch
    except ImportError:
        import termios
        import tty
        import select
        import time
        import os as _os

        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            b = _os.read(fd, 1)
            if not b:
                return ""
            first = b.decode("utf-8", errors="ignore")
            if first != "\x1b":
                return first
            # Read the remainder of an escape sequence with a slightly longer window
            seq_b = [b"\x1b"]
            deadline = time.time() + 0.25  # up to 250ms to collect the sequence
            while time.time() < deadline:
                r, _, _ = select.select([fd], [], [], 0.03)
                if not r:
                    break
                nb = _os.read(fd, 1)
                if not nb:
                    break
                seq_b.append(nb)
                nxt = nb.decode("utf-8", errors="ignore")
                # Stop if we detect a typical CSI/SS3 final byte (ASCII @ to ~)
                if len(seq_b) >= 2:
                    if seq_b[1] in (b"[", b"O") and ("@" <= nxt <= "~"):
                        break
                if len(seq_b) >= 8:
                    break
            seq = b"".join(seq_b).decode("utf-8", errors="ignore")
            return seq
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _enable_windows_ansi() -> None:
    """Enable ANSI escape sequence processing on Windows terminals, if possible."""
    if os.name != "nt":
        return
    try:
        import ctypes  # type: ignore

        kernel32 = ctypes.windll.kernel32
        # STD_OUTPUT_HANDLE = -11
        handle = kernel32.GetStdHandle(ctypes.c_int(-11))
        mode = ctypes.c_uint()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
            new_mode = mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING
            kernel32.SetConsoleMode(handle, ctypes.c_uint(new_mode))
    except Exception:
        # Best-effort only; silently continue if enabling fails
        pass


def _fancy_input(prompt_title: str = "Create a new agent", placeholder: str = "my-agent") -> str:
    """Render a lightweight ASCII input UI and return the entered name.

    Falls back to builtin input() if not attached to a TTY.
    """
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        # Non-interactive environment
        return input(f"{prompt_title}\nProject directory name: ")

    # Ensure Windows consoles understand ANSI sequences
    _enable_windows_ansi()

    # Simple ASCII UI with a block cursor inside brackets
    title = _bold(_cyan(prompt_title)) if _color_enabled() else prompt_title
    instructions = "Type a project directory name and press Enter."
    field_width = 34
    value = ""
    cursor = "█" if _color_enabled() else "#"

    # Hide the terminal cursor
    sys.stdout.write("\x1b[?25l")
    try:
        print(title)
        print(instructions)
        print("")
        while True:
            # Sanitize display text to keep within field width
            shown = value[-field_width:]
            pad = max(0, field_width - len(shown))
            line = f"[{shown}{cursor}{' ' * pad}]"
            sys.stdout.write("\r" + line)
            sys.stdout.flush()

            ch = _read_key()
            # Enter
            if ch in ("\r", "\n"):
                if value.strip():
                    sys.stdout.write("\r" + " " * (len(line)) + "\r")
                    print(f"[{value}]")
                    return value.strip()
                else:
                    # If empty, seed with placeholder
                    value = placeholder
                    continue
            # Ctrl+C
            if ch == "\x03":
                raise KeyboardInterrupt
            # Backspace (Unix "\x7f" or Windows "\x08")
            if ch in ("\x7f", "\b"):
                value = value[:-1]
                continue
            # Ignore escape sequences (arrows, etc.)
            if ch.startswith("\x1b"):
                # ignore any ANSI sequence (arrows, Home/End, etc.)
                continue
            # Basic filtering: allow letters, digits, '-', '_', and spaces (later trimmed)
            if re.match(r"[0-9A-Za-z_\- ]", ch):
                # Soft limit overall length to 64
                if len(value) < 64:
                    value += ch
            # Otherwise ignore
    finally:
        # Restore terminal cursor
        sys.stdout.write("\x1b[?25h")
        sys.stdout.flush()


def _fancy_select(options: list[str], title: str = "Select agents") -> list[int]:
    """Interactive multi-select (requires TTY) using InquirerPy."""
    if not options:
        return []
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        raise RuntimeError("Interactive TTY required for selection; run in a terminal.")

    from InquirerPy import inquirer  # type: ignore

    result = inquirer.checkbox(
        message=title,
        choices=[{"name": opt, "value": i} for i, opt in enumerate(options)],
        instruction="Space to toggle, Enter to confirm.",
        transformer=lambda res: f"{len(res)} selected",
    ).execute()
    return list(result) if isinstance(result, list) else []

    # Ensure Windows consoles understand ANSI sequences
    _enable_windows_ansi()

    selected = [False] * len(options)
    idx = 0
    sys.stdout.write("\x1b[?25l")
    try:
        print(_bold(_cyan(title)) if _color_enabled() else title)
        while True:
            for i, opt in enumerate(options):
                mark = "[x]" if selected[i] else "[ ]"
                line = f"{mark} {opt}"
                if i == idx:
                    line = "> " + line
                    if _color_enabled():
                        line = _cyan(line)
                else:
                    line = "  " + line
                print(line)
            ch = _read_key()
            if ch in ("\r", "\n"):
                break
            if ch == " ":
                selected[idx] = not selected[idx]
            # Support vim-style navigation as a fallback
            elif ch.lower() == "k":
                idx = (idx - 1) % len(options)
            elif ch.lower() == "j":
                idx = (idx + 1) % len(options)
            # Common ANSI sequences for arrows
            # Up: normal CSI and SS3 variants
            elif ch in ("\x1b[A", "\x1bOA"):
                idx = (idx - 1) % len(options)
            # Down: normal CSI and SS3 variants
            elif ch in ("\x1b[B", "\x1bOB"):
                idx = (idx + 1) % len(options)
            # Be tolerant of longer CSI forms like "\x1b[1;5A"
            elif ch.startswith("\x1b") and ch.endswith("A"):
                idx = (idx - 1) % len(options)
            elif ch.startswith("\x1b") and ch.endswith("B"):
                idx = (idx + 1) % len(options)
            # move cursor up to redraw
            print(f"\x1b[{len(options)}A", end="")
            sys.stdout.flush()
        print("\x1b[J", end="")
        return [i for i, s in enumerate(selected) if s]
    finally:
        sys.stdout.write("\x1b[?25h")
        sys.stdout.flush()


def deploy_agent() -> None:
    _eprint(_red("The 'deploy' command has been removed. Agents run via the API; no deployment is required."))
    raise SystemExit(2)


def list_agents_cmd() -> None:
    agents = fetch_agents()
    if not agents:
        print("No agents found.")
        return
    for ag in agents:
        status = "published" if ag.get("published") else "draft"
        print(f"{ag.get('name')} ({ag.get('agent_uuid')}) - {status}")


## undeploy removed (no-op)


# ---- Coloring helpers -----------------------------------------------------

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"


def _color_enabled() -> bool:
    # Respect NO_COLOR and only color when attached to a TTY
    return os.environ.get("NO_COLOR") is None and sys.stdout.isatty()


def _style(txt: str, code: str) -> str:
    if _color_enabled():
        return f"{code}{txt}{RESET}"
    return txt


def _green(txt: str) -> str:
    return _style(txt, GREEN)


def _red(txt: str) -> str:
    return _style(txt, RED)


def _bold(txt: str) -> str:
    return _style(txt, BOLD)


def _cyan(txt: str) -> str:
    return _style(txt, CYAN)


def _yellow(txt: str) -> str:
    return _style(txt, YELLOW)


def _eprint(txt: str) -> None:
    stream = sys.stderr
    if os.environ.get("NO_COLOR") is None and stream.isatty():
        print(txt, file=stream)
    else:
        # Strip ANSI if stderr is not a TTY
        print(re.sub(r"\x1b\[[0-9;]*m", "", txt), file=stream)


def _package_version() -> str:
    """Return the installed package version or a sensible fallback."""
    try:
        # Project package name per pyproject
        return pkg_version("hurozo")
    except PackageNotFoundError:
        # Fallback to the version declared in pyproject in dev checkouts
        return "0.1.0"


def _make_examples_block() -> str:
    return (
        f"{_bold('Examples:')}\n"
        "  # Create a new agent project in ./my-agent\n"
        "  hurozo init my-agent\n\n"
        f"  # List available agents (requires {_yellow('HUROZO_API_TOKEN')})\n"
        "  hurozo list\n\n"
        f"  # Run locally via API (requires {_yellow('HUROZO_API_TOKEN')})\n"
        "  cd my-agent && export HUROZO_API_TOKEN=... && python main.py\n"
    )


def _show_help(topic_parts, parser, init_top, list_top) -> None:
    # No topic -> top-level help
    if not topic_parts:
        parser.print_help()
        return
    # One part
    if len(topic_parts) == 1:
        if topic_parts[0] == "init":
            init_top.print_help()
            return
        if topic_parts[0] == "list":
            list_top.print_help()
            return
        
    # Fallback
    _eprint(_red("Unknown help topic. Try 'hurozo --help' or 'hurozo help init'."))
    raise SystemExit(2)


def main() -> None:
    description = (
        _cyan("Hurozo CLI — tools to scaffold and execute agent projects.")
        + "\n\nUse 'init' and 'list' commands."
    )
    epilog = _make_examples_block()

    parser = argparse.ArgumentParser(
        prog="hurozo",
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"hurozo { _package_version() }",
        help="Show the hurozo version and exit.",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="<command>")

    # Shared descriptions for top-level commands
    init_desc = (
        _cyan("Create a minimal agent project at the given directory.")
        + "\n\nGenerates:\n"
        + "  - requirements.txt (with hurozo)\n"
        + "  - main.py (example runner)\n"
    )

    # Wire up command handlers
    def _handle_init(a):
        dirname = a.dirname
        if not dirname:
            try:
                dirname = _fancy_input()
            except KeyboardInterrupt:
                _eprint(_red("Initialization canceled."))
                raise SystemExit(130)
        agents = fetch_agents()
        selected = []
        if agents:
            idxs = _fancy_select([ag.get("name", "") for ag in agents], "Select agents")
            selected = [agents[i] for i in idxs]
        init_agent(dirname, selected if selected else None)

    # Top-level commands
    init_top = subparsers.add_parser(
        "init",
        help="Scaffold a new agent project.",
        description=init_desc,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    init_top.add_argument(
        "dirname",
        nargs="?",
        help="Target directory for the new project. If omitted, an interactive prompt appears.",
    )
    init_top.set_defaults(func=_handle_init)

    list_top = subparsers.add_parser(
        "list",
        help="List agents for the authenticated user.",
        description=None,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    list_top.set_defaults(func=lambda a: list_agents_cmd())

    # help alias: `hurozo help [topic]`
    help_parser = subparsers.add_parser(
        "help",
        help="Show help for a command.",
        description=(
            _cyan("Show detailed help for a given command.")
            + "\n\nExamples:\n"
            + "  hurozo help\n"
            + "  hurozo help init\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    help_parser.add_argument("topic", nargs="*", help="Command/topic to show help for.")
    help_parser.set_defaults(
        func=lambda a, p=parser, it=init_top, lt=list_top: _show_help(a.topic, p, it, lt)
    )

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
