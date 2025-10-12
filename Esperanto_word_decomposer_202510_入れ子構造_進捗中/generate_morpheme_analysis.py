#!/usr/bin/env python3
"""
Generate a morpheme-decomposition output for the bundled Esperanto example sentences.

The script loads the existing input text, runs the current literumilo analyzer in
`morpheme` mode, and persists the annotated result to an output file.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT = Path("エスペラント例文(語根分解精度のチェックに用いる).txt")
DEFAULT_OUTPUT = Path("esperanto_example_sentences_morpheme_analysis.txt")


def _configure_import_path() -> None:
    """Ensure the bundled literumilo package is importable when running from source."""
    package_root = REPO_ROOT / "literumilo"
    package_root_str = str(package_root)
    if package_root_str not in sys.path:
        sys.path.insert(0, package_root_str)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run literumilo against the Esperanto sample sentences and store the morpheme analysis."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Path to the input text file (default: %(default)s, relative to repository root).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Destination path for the morpheme analysis (default: %(default)s, relative to repository root).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    _configure_import_path()
    from literumilo import analyze_string  # Imported only after sys.path is updated.

    input_path = (args.input if args.input.is_absolute() else REPO_ROOT / args.input).resolve()
    output_path = (args.output if args.output.is_absolute() else REPO_ROOT / args.output).resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Read, analyze, and persist the morpheme-separated text.
    text = input_path.read_text(encoding="utf-8")
    analyzed_text = analyze_string(text, True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(analyzed_text, encoding="utf-8")
    print(f"Morpheme analysis written to: {output_path}")


if __name__ == "__main__":
    main()
