# Copyright (c) MIST Imaging LLC.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Command line tool for converting datasets to MIST format.

Supported formats come from the conversion registry (e.g., "msd", "csv").
"""
from argparse import ArgumentDefaultsHelpFormatter
from pathlib import Path
from typing import Optional, List
import argparse

# MIST imports.
from mist.conversion_tools.conversion_format_registry import (
    get_conversion_function,
    get_supported_formats,
)
from mist.cli.args import ArgParser


def _validate_format_args(
    parser: argparse.ArgumentParser, ns: argparse.Namespace
) -> None:
    """Validate required arguments for each format."""
    if ns.format == "msd":
        if not ns.msd_source:
            parser.error("--msd-source is required when --format msd")
    elif ns.format == "csv":
        if not ns.train_csv:
            parser.error("--train-csv is required when --format csv")


def parse_conversion_args(
    argv: Optional[List[str]]=None
) -> argparse.Namespace:
    """Parse command line arguments for dataset conversion."""
    p = ArgParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="Convert a dataset to MIST format.",
    )

    # Required arguments.
    p.arg(
        "--format", type=str,
        required=True,
        choices=get_supported_formats(),
        help="Source dataset format to convert.",
    )
    p.arg(
        "--output",
        type=str,
        required=True,
        help="Directory to save the converted dataset (MIST format).",
    )

    # Format-specific arguments.
    p.arg("--msd-source", type=str, help="Directory containing MSD formatted dataset.")
    p.arg("--train-csv", type=str, help="Path to CSV with ids, mask, and images.")
    p.arg("--test-csv", type=str, help="(Optional) Path to CSV with test ids and images.")

    ns = p.parse_args(argv)
    _validate_format_args(p, ns)
    return ns


def run_conversion(ns: argparse.Namespace) -> None:
    """Dispatch to the appropriate converter based on ns.format."""
    # Ensure output directory exists.
    out_dir = Path(ns.output).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    convert_fn = get_conversion_function(ns.format)

    if ns.format == "msd":
        msd_source = Path(ns.msd_source).expanduser().resolve()
        convert_fn(str(msd_source), str(out_dir))
    elif ns.format == "csv":
        train_csv = Path(ns.train_csv).expanduser().resolve()
        test_csv = (
            Path(ns.test_csv).expanduser().resolve() if ns.test_csv else None
        )
        convert_fn(
            str(train_csv), str(out_dir), str(test_csv) if test_csv else None
        )
    else:
        # Should never happen due to argparse choices, but guard anyway.
        raise ValueError(f"Unsupported format: {ns.format}")


def conversion_entry(argv: Optional[List[str]] = None) -> None:
    """Entry point for the dataset conversion script."""
    ns = parse_conversion_args(argv)
    run_conversion(ns)


if __name__ == "__main__":
    conversion_entry()  # pragma: no cover
