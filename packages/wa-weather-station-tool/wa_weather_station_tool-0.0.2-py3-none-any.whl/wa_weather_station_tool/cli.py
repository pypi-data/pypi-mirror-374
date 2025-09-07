from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from . import __version__


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI.

    This minimal version only parses common downloader options
    and prints them back. Real downloading will be implemented later.
    """
    parser = argparse.ArgumentParser(
        prog="wa_dpird_weather_downloader",
        description=(
            "Download WA DPIRD weather station data (minimal CLI scaffold)."
        ),
    )

    parser.add_argument(
        "--station",
        type=str,
        required=True,
        help="Station ID/code to download (e.g., '009225').",
    )
    parser.add_argument(
        "--start",
        type=str,
        required=False,
        default=None,
        help="Start date (YYYY-MM-DD). Optional for minimal version.",
    )
    parser.add_argument(
        "--end",
        type=str,
        required=False,
        default=None,
        help="End date (YYYY-MM-DD). Optional for minimal version.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        required=False,
        default=Path("weather_data.csv"),
        help="Output CSV file path (default: weather_data.csv).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"wa_dpird_weather_downloader {__version__}",
    )

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """Entry point for the minimal CLI.

    For now, it validates arguments and writes a small placeholder CSV
    to confirm the tool is wired up correctly.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    # Placeholder behavior: emit a tiny CSV with headers + a single row
    # containing the provided parameters, so downstream scripts can verify IO.
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        "station_id,start_date,end_date,note\n"
        f"{args.station},{args.start or ''},{args.end or ''},"
        "placeholder_data\n",
        encoding="utf-8",
    )

    print(
        "Created placeholder CSV:",
        str(args.out.resolve()),
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
