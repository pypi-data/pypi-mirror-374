# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Entrypoint for running the MIST training pipeline."""
from argparse import ArgumentDefaultsHelpFormatter
from pathlib import Path
from typing import List, Optional, Tuple
import os
import argparse
import rich
import pandas as pd
import torch

# MIST imports.
from mist.cli import args as argmod
from mist.utils import io
from mist.training.trainers.patch_3d_trainer import Patch3DTrainer
from mist.inference.inference_runners import test_on_fold, infer_from_dataframe
from mist.evaluation import evaluation_utils
from mist.evaluation.evaluator import Evaluator


def _parse_train_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse CLI for the training pipeline.

    Falls back to ./results and ./numpy if not provided, then downstream
    functions validate that the expected artifacts exist.
    """
    parser = argmod.ArgParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="MIST training pipeline.",
    )
    # Add training-specific args.
    argmod.add_train_args(parser)
    ns = parser.parse_args(argv)

    # Fallbacks for convenience/consistency with other entrypoints.
    if not ns.results:
        ns.results = str(Path("./results").expanduser().resolve())
    if not ns.numpy:
        ns.numpy = str(Path("./numpy").expanduser().resolve())
    return ns


def _ensure_required_artifacts(ns: argparse.Namespace) -> Tuple[Path, bool]:
    """Verify results & numpy folders contain the expected structure.

    Returns:
        Tuple[Path, bool]: (results_dir, has_test_paths)
    """
    results_dir = Path(ns.results).expanduser().resolve()
    numpy_dir = Path(ns.numpy).expanduser().resolve()

    # Results folder must already exist and contain required files.
    if not results_dir.is_dir():
        raise FileNotFoundError(
            f"Results directory does not exist: {results_dir}"
        )

    required_files = ["config.json", "train_paths.csv", "fg_bboxes.csv"]
    missing = [f for f in required_files if not (results_dir / f).is_file()]
    if missing:
        raise FileNotFoundError(
            "Missing required file(s) in results directory: "
            + ", ".join(missing)
            + f" (in {results_dir})"
        )

    has_test_paths = (results_dir / "test_paths.csv").is_file()

    # NumPy directory must exist with required subfolders.
    if not numpy_dir.is_dir():
        raise FileNotFoundError(f"NumPy directory does not exist: {numpy_dir}")

    required_np_subdirs = ["images", "labels"]  # 'dtms' is optional.
    missing_np = [
        d for d in required_np_subdirs if not (numpy_dir / d).is_dir()
    ]
    if missing_np:
        raise FileNotFoundError(
            "Missing required subfolder(s) in NumPy directory: "
            + ", ".join(missing_np)
            + f" (in {numpy_dir})"
        )
    return results_dir, has_test_paths


def _create_train_dirs(results_dir: Path, has_test_paths: bool) -> None:
    """Create output directories inside results for logs/models/predictions."""
    (results_dir / "logs").mkdir(parents=True, exist_ok=True)
    (results_dir / "models").mkdir(parents=True, exist_ok=True)

    train_pred_dir = results_dir / "predictions" / "train" / "raw"
    train_pred_dir.mkdir(parents=True, exist_ok=True)
    if has_test_paths:
        test_pred_dir = results_dir / "predictions" / "test"
        test_pred_dir.mkdir(parents=True, exist_ok=True)


def _set_visible_devices(mist_arguments: argparse.Namespace) -> None:
    """Set visible CUDA devices from CLI args; return number of GPUs."""
    # Total available GPUs.
    total = torch.cuda.device_count()
    if total == 0:
        raise RuntimeError(
            "No CUDA devices found; training requires at least one GPU."
        )

    gpus = getattr(mist_arguments, "gpus", None)

    # None / [] / [-1]  -> all GPUs.
    if gpus is None or len(gpus) == 0 or (len(gpus) == 1 and gpus[0] == -1):
        visible_devices = ",".join(str(i) for i in range(total))
    else:
        # Minimal validation: indices must be within 0..total-1.
        invalid = [i for i in gpus if i < 0 or i >= total]
        if invalid:
            raise ValueError(
                f"Requested GPU index/indices out of range {invalid}; "
                f"available indices are 0..{total - 1}."
            )
        visible_devices = ",".join(str(i) for i in gpus)

    os.environ["CUDA_VISIBLE_DEVICES"] = visible_devices


def train_entry(argv: Optional[List[str]] = None) -> None:
    """Entrypoint for the training command."""
    console = rich.console.Console()

    ns = _parse_train_args(argv)

    # Validate artifacts from analyze + preprocess
    results_dir, has_test_paths = _ensure_required_artifacts(ns)

    # Avoid accidental overwrite of an existing results.csv.
    results_csv = results_dir / "results.csv"
    if results_csv.exists() and not getattr(ns, "overwrite", False):
        raise FileExistsError(
            f"Found existing results at {results_csv}. Use --overwrite to "
            "replace them."
        )

    _create_train_dirs(results_dir, has_test_paths)

    # Set the visible GPUs (None -> use all GPUs)
    _set_visible_devices(ns)

    # Train
    trainer = Patch3DTrainer(ns)
    trainer.fit()

    # Post-training: generate predictions for each fold
    config = io.read_json_file(str(results_dir / "config.json"))
    for fold in config["training"]["folds"]:
        test_on_fold(ns, fold)

    # Evaluate CV predictions
    filepaths_df, warnings = evaluation_utils.build_evaluation_dataframe(
        train_paths_csv=str(results_dir / "train_paths.csv"),
        prediction_folder=str(results_dir / "predictions" / "train" / "raw"),
    )

    if warnings:
        console.print(warnings)

    if filepaths_df.empty:
        console.print(
            "[red]No valid prediction-mask pairs. Skipping evaluation.[/red]"
        )
    else:
        evaluation_csv = results_dir / "evaluation_paths.csv"
        filepaths_df.to_csv(evaluation_csv, index=False)

        evaluator = Evaluator(
            filepaths_dataframe=filepaths_df,
            evaluation_classes=config["evaluation"]["final_classes"],
            output_csv_path=results_csv,
            selected_metrics=config["evaluation"]["metrics"],
            surf_dice_tol=config["evaluation"]["params"]["surf_dice_tol"],
        )
        evaluator.run()

    # Optional test inference
    if has_test_paths:
        test_df = pd.read_csv(results_dir / "test_paths.csv")
        with torch.no_grad():
            infer_from_dataframe(
                paths_dataframe=test_df,
                output_directory=str(results_dir / "predictions" / "test"),
                mist_configuration=config,
                models_directory=str(results_dir / "models"),
                postprocessing_strategy_filepath=None,
                device=torch.device("cuda"),
            )


if __name__ == "__main__":
    train_entry()  # pragma: no cover
