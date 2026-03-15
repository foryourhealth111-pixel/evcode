from __future__ import annotations

import json
import os
import sys


def main() -> int:
    payload = json.load(sys.stdin) if not sys.stdin.isatty() else {}
    mode = os.environ.get("EVCODE_MODE", "interactive_governed")
    agent_type = payload.get("agent_type", "default")
    response = {
        "continue": True,
        "additionalContext": "\n".join(
            [
                "EvCode subagent governance is active.",
                f"- mode: {mode}",
                f"- agent_type: {agent_type}",
                "- preserve requirement and execution-plan traceability in child work",
                "- the host patch layer must ensure the child task ends with ` $vibe`",
            ]
        ),
    }
    print(json.dumps(response))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
