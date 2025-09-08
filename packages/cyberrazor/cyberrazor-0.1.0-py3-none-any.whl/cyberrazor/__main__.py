import os
import sys
import runpy
from pathlib import Path

from . import __version__


def print_banner_from_pro():
    # Try to reuse the banner from existing free/main file if available
    try:
        from .freetier import print_banner as ft_banner
        ft_banner()
    except Exception:
        print(f"CyberRazor v{__version__}")


def activate_and_maybe_run_pro() -> bool:
    # Ask for activation key on start
    print("Enter activation key to unlock Pro (press Enter to continue in Free Tier):", end=" ")
    activation_key = input().strip()
    if not activation_key:
        return False

    # Attempt to use existing backend activation in local pro agent if present
    project_root = Path(__file__).resolve().parent.parent
    candidate = project_root / "cyberrazor_agent.py"
    if candidate.exists():
        # Use cyberrazor_agent's activate flow via runpy
        os.environ.setdefault("PYTHONPATH", str(project_root))
        try:
            module_globals = runpy.run_path(str(candidate), run_name="__main__")
            activate_tool = module_globals.get("activate_tool")
            is_activated = module_globals.get("is_activated")
            if callable(activate_tool):
                ok = activate_tool(activation_key)
                return bool(ok)
        except SystemExit:
            return False
        except Exception:
            return False

    # If packaged without local pro agent, consider remote validation (optional no-op)
    return False


def main():
    print_banner_from_pro()
    # If activation validates, run the Pro agent if present; else free tier
    if activate_and_maybe_run_pro():
        # Run the pro agent script if available
        project_root = Path(__file__).resolve().parent.parent
        candidate = project_root / "cyberrazor_agent.py"
        if candidate.exists():
            # hand off to pro agent as a new process to preserve its CLI UX
            os.execv(sys.executable, [sys.executable, str(candidate)])
        else:
            print("Pro unlocked, but Pro agent not bundled. Staying in Free Tier.")

    # Free tier fallback
    from .freetier import run_cli
    return run_cli()


if __name__ == "__main__":
    main()
