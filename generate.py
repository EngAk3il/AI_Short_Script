#!/usr/bin/env python3
"""
generate.py — Default: prepare agent brief (intelligent Antigravity workflow).

Use --auto only if you explicitly want Python+API static generation (not recommended).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare intelligent script generation (agent-first by default)"
    )
    parser.add_argument("--topic", "-t", help="Topic")
    parser.add_argument("--creator", "-c", help="Creator")
    parser.add_argument("--topics", help="Batch JSON file")
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Legacy: Python calls Claude + DuckDuckGo (static pipeline — avoid for quality)",
    )
    # Legacy flags forwarded to --auto mode only
    parser.add_argument("--facts", "-f")
    parser.add_argument("--output", "-o")
    parser.add_argument("--no-research", action="store_true")
    args = parser.parse_args()

    if args.auto:
        _run_auto_mode(args)
        return

    # Default: prepare agent brief
    cmd = [sys.executable, str(Path(__file__).parent / "prepare.py")]
    if args.topic:
        cmd.extend(["-t", args.topic])
    if args.creator:
        cmd.extend(["-c", args.creator])
    if args.topics:
        cmd.extend(["--topics", args.topics])
    if not args.topic and not args.topics:
        parser.error("Provide --topic and --creator, or --topics")
    if not args.creator and not args.topics:
        parser.error("Provide --creator")
    subprocess.run(cmd, check=False)


def _run_auto_mode(args: argparse.Namespace) -> None:
    """Optional legacy automated generation."""
    from lib.generation_context import load_generation_context, require_hook_library
    from lib.research import research_topic
    from lib.script_generator import generate_with_validation
    from lib.agent_brief import slugify
    from lib.paths import SCRIPTS_DIR

    if args.topics:
        print("⚠️  --auto with --topics: run prepare.py per topic instead for better quality")
        sys.exit(1)
    if not args.topic or not args.creator:
        print("❌ --auto requires --topic and --creator")
        sys.exit(1)

    facts = {}
    if args.facts and Path(args.facts).exists():
        facts = json.loads(Path(args.facts).read_text(encoding="utf-8"))

    ctx = load_generation_context(args.creator, args.topic)
    require_hook_library(ctx)
    if not args.no_research:
        ctx.facts = research_topic(args.topic, extra_facts=facts or None)
    else:
        ctx.facts = facts

    script, passed, log = generate_with_validation(ctx)
    out = Path(args.output) if args.output else SCRIPTS_DIR / args.creator / f"{slugify(args.topic)}_dna.md"
    out.write_text(script, encoding="utf-8")
    print(log)
    sys.exit(0 if passed else 2)


if __name__ == "__main__":
    main()
