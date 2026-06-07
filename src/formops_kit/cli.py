from __future__ import annotations

import argparse
from pathlib import Path

from .core import compile_packets, compile_packets_from_config
from .presets import default_preset, get_preset, list_presets, write_preset_files


def cmd_presets(_: argparse.Namespace) -> None:
    for preset in list_presets():
        print(f"{preset.slug}\t{preset.label}\t{preset.description}")


def cmd_init(args: argparse.Namespace) -> None:
    target = Path(args.path)
    examples = target / "examples"
    files = write_preset_files(args.preset, examples)
    preset = get_preset(args.preset)
    print(f"Created '{preset.label}' example files under {examples}")
    print(f"CSV: {files['csv']}")
    print(f"Config: {files['config']}")


def cmd_compile(args: argparse.Namespace) -> None:
    input_csv = Path(args.input)
    output_dir = Path(args.output)

    if args.config:
        result = compile_packets(
            input_csv=input_csv,
            config_path=Path(args.config),
            output_dir=output_dir,
        )
    else:
        preset = get_preset(args.preset)
        result = compile_packets_from_config(
            input_csv=input_csv,
            config=preset.config,
            output_dir=output_dir,
            config_source=f"preset:{preset.slug}",
        )

    print(f"Rows seen: {result.rows_seen}")
    print(f"Packets created: {result.packets_created}")
    print(f"Skipped rows: {result.skipped_rows}")
    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"- {warning}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="formops",
        description="Turn form responses into operation packets.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    presets_parser = subparsers.add_parser("presets", help="List built-in workflow presets.")
    presets_parser.set_defaults(func=cmd_presets)

    init_parser = subparsers.add_parser("init", help="Create example config and CSV files.")
    init_parser.add_argument("--path", default=".", help="Target project path. Default: current directory.")
    init_parser.add_argument(
        "--preset",
        default=default_preset().slug,
        choices=[preset.slug for preset in list_presets()],
        help="Built-in workflow preset to generate.",
    )
    init_parser.set_defaults(func=cmd_init)

    compile_parser = subparsers.add_parser("compile", help="Compile CSV responses into operation packets.")
    compile_parser.add_argument("--input", required=True, help="Path to CSV export from a form or sheet.")
    compile_parser.add_argument("--config", help="Path to config JSON. Overrides --preset when provided.")
    compile_parser.add_argument(
        "--preset",
        default=default_preset().slug,
        choices=[preset.slug for preset in list_presets()],
        help="Built-in workflow preset to use when --config is not provided.",
    )
    compile_parser.add_argument("--output", default="outbox", help="Output folder. Default: outbox.")
    compile_parser.set_defaults(func=cmd_compile)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
