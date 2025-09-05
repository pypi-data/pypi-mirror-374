# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Handle command line arguments for main MIST pipelines."""
from typing import Union
import argparse
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser # pylint: disable=unused-import

# MIST imports.
from mist.models.model_registry import list_registered_models
from mist.training.lr_schedulers.lr_scheduler_registry import list_lr_schedulers
from mist.training.optimizers.optimizer_registry import list_optimizers
from mist.loss_functions.loss_registry import list_registered_losses
from mist.loss_functions.alpha_schedulers import list_alpha_schedulers


def positive_int(value: Union[str, int]) -> int:
    """Check if the input is a positive integer."""
    integer_value = int(value)
    if integer_value <= 0:
        raise argparse.ArgumentTypeError(
            f"Argparse error. Expected a positive integer but got {value}."
        )
    return integer_value


def positive_float(value: Union[str, float]) -> float:
    """Check if the input is a positive float."""
    float_value = float(value)
    if float_value <= 0:
        raise argparse.ArgumentTypeError(
            f"Argparse error. Expected a positive float but got {value}."
        )
    return float_value


def non_negative_int(value: Union[str, int]) -> int:
    """Check if the input is a non-negative integer."""
    integer_value = int(value)
    if integer_value < 0:
        raise argparse.ArgumentTypeError(
            f"Argparse error. Expected a non-negative integer but got {value}."
        )
    return integer_value


def float_0_1(value: Union[str, float]) -> float:
    """Check if the input is a float in [0, 1]."""
    float_value = float(value)
    if not 0 <= float_value <= 1:
        raise argparse.ArgumentTypeError(
            "Argparse error. Expected a float from range [0, 1], "
            f"but got {value}."
        )
    return float_value


def str2bool(value: Union[str, bool]) -> bool:
    """Convert a string to a boolean value."""
    if isinstance(value, bool):
        return value
    v = value.lower()
    if v in ("yes", "true", "t", "y", "1"):
        return True
    if v in ("no", "false", "f", "n", "0"):
        return False
    raise argparse.ArgumentTypeError("Boolean value expected!")


class ArgParser(ArgumentParser):
    """Argument parser for MIST pipelines."""
    def arg(self, *args, **kwargs):
        """Add an argument to the parser."""
        return super().add_argument(*args, **kwargs)

    def flag(self, *args, **kwargs):
        """Add a flag to the parser (store_true)."""
        return super().add_argument(*args, action="store_true", **kwargs)

    def boolean_flag(self, *args, **kwargs):
        """Add a boolean flag with optional explicit true/false."""
        return super().add_argument(
            *args,
            type=str2bool,
            nargs="?",
            const=True,
            metavar="BOOLEAN",
            **kwargs,
        )

# pylint: disable=line-too-long
def add_analyzer_args(parser: ArgParser) -> None:
    """Add arguments for the Analyzer class."""
    g = parser.add_argument_group("Analyzer")
    g.add_argument("--data", type=str, help="Path to dataset JSON file.")
    g.add_argument("--results", type=str, help="Path to output of MIST pipeline.")
    g.add_argument("--nfolds", type=int, help="Number of cross-validation folds.")
    parser.boolean_flag("--overwrite", default=False, help="Overwrite previous configuration/results.")


def add_preprocess_args(parser: ArgParser) -> None:
    """Add arguments for the preprocessing pipeline."""
    g = parser.add_argument_group("Preprocess")
    g.add_argument("--results", type=str, help="Path to output of MIST pipeline.")
    g.add_argument("--numpy", type=str, help="Path to save preprocessed NumPy data.")
    parser.boolean_flag("--no-preprocess", default=False, help="Turn off most preprocessing.")
    parser.boolean_flag("--compute-dtms", default=False, help="Compute DTMs.")
    parser.boolean_flag("--overwrite", default=False, help="Overwrite previous configuration/results.")


def add_train_args(parser: ArgParser) -> None:
    """Add arguments for the training pipeline."""
    g = parser.add_argument_group("Train")
    # Input data.
    g.add_argument("--results", type=str, help="Path to output of MIST pipeline.")
    g.add_argument("--numpy", type=str, help="Path to save preprocessed NumPy data.")

    # Hardware.
    g.add_argument("--gpus", nargs="+", default=[-1], type=int, help="IDs of GPUs to use; use -1 for all GPUs.")

    # Model.
    g.add_argument("--model", type=str, choices=list_registered_models(), help="Network architecture.")
    parser.boolean_flag("--pocket", default=False, help="Use pocket version of model (if available).")
    g.add_argument("--patch-size", nargs=3, type=positive_int, metavar=("X", "Y", "Z"), help="Patch size as three ints: X Y Z.")

    # Loss function.
    g.add_argument("--loss", type=str, choices=list_registered_losses(), help="Loss function for training.")
    parser.boolean_flag("--use-dtms", default=False, help="Use DTMs during training.")
    g.add_argument("--composite-loss-weighting", type=str, choices=list_alpha_schedulers(), help="Weighting schedule for composite losses.")

    # Training loop.
    g.add_argument("--epochs", type=non_negative_int, help="Number of epochs per fold.")
    g.add_argument("--batch-size-per-gpu", type=positive_int, help="Batch size per GPU/CPU worker.")
    g.add_argument("--learning-rate", type=positive_float, help="Learning rate.")
    g.add_argument("--lr-scheduler", type=str, choices=list_lr_schedulers(), help="Learning rate scheduler.")
    g.add_argument("--optimizer", type=str, choices=list_optimizers(), help="Optimizer to use.")
    g.add_argument("--l2-penalty", type=positive_float, help="L2 penalty (weight decay).")
    g.add_argument("--folds", nargs="+", type=int, help="Specify which folds to run.")
    g.add_argument("--val-percent", type=float_0_1, help="Percent of training set to use for validation (0.0-1.0).")

    # Overwrite.
    parser.boolean_flag("--overwrite", default=False, help="Overwrite previous configuration/results.")
