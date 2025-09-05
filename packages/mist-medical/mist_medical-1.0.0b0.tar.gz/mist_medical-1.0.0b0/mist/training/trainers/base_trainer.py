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
"""Base trainer class for MIST."""
from typing import Dict, Any
from abc import ABC, abstractmethod
from pathlib import Path
import os
import math
import random
import numpy as np
import pandas as pd
import rich
import torch
import torch.distributed as dist
import torch.multiprocessing as mp
from sklearn.model_selection import train_test_split
from torch import nn
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.tensorboard import SummaryWriter

# Import MIST modules.
from mist.utils import io, progress_bar
from mist.models.model_loader import get_model
from mist.loss_functions.loss_registry import get_loss
from mist.loss_functions.deep_supervision_wrapper import DeepSupervisionLoss
from mist.loss_functions.losses.dice import DiceLoss
from mist.loss_functions.alpha_schedulers import get_alpha_scheduler
from mist.training.lr_schedulers.lr_scheduler_registry import get_lr_scheduler
from mist.training.optimizers.optimizer_registry import get_optimizer
from mist.training import training_utils
from mist.training.trainers.trainer_constants import TrainerConstants


class BaseTrainer(ABC):
    """Base trainer that provides common functionality for training models."""
    def __init__(self, mist_args):
        """Initialize the trainer class."""
        self.mist_args = mist_args
        self.results_dir = Path(self.mist_args.results).expanduser().resolve()
        self.numpy_dir = Path(self.mist_args.numpy).expanduser().resolve()
        self.models_dir = self.results_dir / "models"
        self.logs_dir = self.results_dir / "logs"

        # Required files.
        paths_csv = self.results_dir / "train_paths.csv"
        self.paths = pd.read_csv(paths_csv)

        self.config_json = self.results_dir / "config.json"
        self.config = io.read_json_file(self.config_json)

        # Merge command line overrides into the config.
        self._overwrite_config_from_args()

        # Resolve hardware configuration.
        self._update_num_gpus_in_config()

        # Set up batch size based on the number of GPUs.
        self.batch_size = (
            self.config["training"]["batch_size_per_gpu"] *
            max(1, self.config["training"]["hardware"]["num_gpus"])
        )

        # Prepare folds.
        self._setup_folds()

        # Set up validation loss.
        self.validation_loss = DiceLoss(exclude_background=True)

        # Set up console for rich text output.
        self.console = rich.console.Console()

    def __getstate__(self):
        """Customize pickling so mp.spawn can serialize this object."""
        state = self.__dict__.copy()
        # Drop unpicklable attributes (contain thread locks, file handles, etc.)
        state["console"] = None
        return state

    def __setstate__(self, state):
        """Recreate transient/unpicklable attributes after unpickling."""
        self.__dict__.update(state)
        # Recreate the console on the child process.
        if self.__dict__.get("console") is None:
            self.console = rich.console.Console()

    @abstractmethod
    def build_dataloaders(self, fold_data, rank, world_size):
        """Abstract method to build data loaders for training and validation."""
        raise NotImplementedError( # pragma: no cover
            "build_dataloaders method must be implemented in the subclass."
        )

    @abstractmethod
    def training_step(self, **kwargs):
        """Abstract method for training step."""
        raise NotImplementedError( # pragma: no cover
            "training_step method must be implemented in the subclass."
        )

    @abstractmethod
    def validation_step(self, **kwargs):
        """Abstract method for validation step."""
        raise NotImplementedError( # pragma: no cover
            "validation_step method must be implemented in the subclass."
        )

    def _set_seed(self, seed: int) -> None:
        """Seed Python, NumPy, and PyTorch RNGs (DDP-aware).

        Uses the provided base `seed`, offset by the process rank so that each 
        rank gets a distinct but reproducible RNG stream. Also sets
        PYTHONHASHSEED for consistent hashing across runs.
        """
        # Determine rank (works before/after dist.init_process_group).
        rank = int(os.environ.get("RANK", 0))
        try:
            if dist.is_initialized():
                rank = dist.get_rank()
        except (AttributeError, RuntimeError, ValueError, TypeError):
            pass

        final_seed = int(seed) + int(rank)

        # Python and env.
        os.environ["PYTHONHASHSEED"] = str(final_seed)
        random.seed(final_seed)

        # NumPy.
        np.random.seed(final_seed)

        # PyTorch (CPU & CUDA).
        torch.manual_seed(final_seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(final_seed)
            torch.cuda.manual_seed_all(final_seed)

    def _overwrite_config_from_args(self):
        """Overwrite certain config parameters from command line arguments."""
        # Overwrite model settings from command line arguments.
        # Overwrite the architecture if if is specified in command line
        # arguments.
        if self.mist_args.model is not None:
            self.config["model"]["architecture"] = self.mist_args.model

        # Overwrite the patch size if it is specified in command line arguments.
        if self.mist_args.patch_size is not None:
            self.config["model"]["params"]["patch_size"] = [
                int(dim) for dim in self.mist_args.patch_size
            ]

        # Set the patch size for inference to be the same as training.
        self.config["inference"]["inferer"]["params"]["patch_size"] = (
            self.config["model"]["params"]["patch_size"]
        )

        # Use pocket model if specified in command line arguments.
        if self.mist_args.pocket:
            self.config["model"]["params"]["use_pocket_model"] = True

        # Overwrite training parameters from command line arguments.
        # If the user specified to run only on certain folds, then update the
        # configuration with which folds to use.
        if self.mist_args.folds is not None:
            # Check that the folds are a subset of the enumeration of the
            # total number of folds.
            if not set(self.mist_args.folds).issubset(
                set(range(self.config["training"]["nfolds"]))
            ):
                raise ValueError(
                    "Folds specified in command line arguments must be a "
                    "subset of [0, 1, ..., nfolds-1]. Found folds: "
                    f"{self.mist_args.folds}."
                )
            self.config["training"]["folds"] = [
                int(fold) for fold in self.mist_args.folds
            ]

        # If the user specifies a number of epochs, then update the
        # configuration with the number of epochs.
        if self.mist_args.epochs is not None:
            self.config["training"]["epochs"] = int(self.mist_args.epochs)

        # If the user specifies a different batch size to use on each GPU,
        # then update the configuration with the new batch size.
        if self.mist_args.batch_size_per_gpu is not None:
            self.config["training"]["batch_size_per_gpu"] = int(
                self.mist_args.batch_size_per_gpu
            )

        # Overwrite the loss function and its parameters if specified in
        # command line arguments.
        # Overwrite the loss function name.
        if self.mist_args.loss is not None:
            self.config["training"]["loss"]["name"] = self.mist_args.loss

        # Overwrite the loss function parameters. These are the use of DTMs
        # and the composite loss weighting.
        if self.mist_args.use_dtms:
            self.config["training"]["loss"]["params"]["use_dtms"] = True

        if self.mist_args.composite_loss_weighting is not None:
            self.config["training"]["loss"]["params"]["composite_loss_weighting"] = (
                self.mist_args.composite_loss_weighting
            )

        # Overwrite the optimizer and its parameters if specified in command
        # line arguments.
        if self.mist_args.optimizer is not None:
            self.config["training"]["optimizer"] = self.mist_args.optimizer

        if self.mist_args.l2_penalty is not None:
            self.config["training"]["l2_penalty"] = float(
                self.mist_args.l2_penalty
            )

        # Overwrite the learning rate scheduler and its parameters if specified
        # in command line arguments.
        if self.mist_args.learning_rate is not None:
            self.config["training"]["learning_rate"] = float(
                self.mist_args.learning_rate
            )

        if self.mist_args.lr_scheduler is not None:
            self.config["training"]["lr_scheduler"] = (
                self.mist_args.lr_scheduler
            )

        # Overwrite the validation percentage if specified in command line.
        if self.mist_args.val_percent is not None:
            self.config["training"]["val_percent"] = float(
                self.mist_args.val_percent
            )

        # Write the updated configuration to the config.json file.
        io.write_json_file(self.config_json, self.config)

    def _update_num_gpus_in_config(self) -> None:
        """Get the number of GPUs and add it to the configuration."""
        # Fast, explicit CUDA checks.
        if not torch.cuda.is_available():
            raise ValueError(
                "CUDA is not available. Ensure the CUDA toolkit/driver matches "
                "your PyTorch build, and that you're running on a GPU host."
            )

        # If CUDA is available, check the number of GPUs. If the number of GPUs
        # is zero, raise an error.
        num_gpus = torch.cuda.device_count()
        if num_gpus <= 0:
            raise ValueError(
                "torch.cuda.is_available() is True but device_count() == 0. "
                "Check CUDA_VISIBLE_DEVICES or container runtime GPU flags"
            )

        # If there are GPUs available, update the configuration with the number
        # of GPUs.
        self.config["training"]["hardware"]["num_gpus"] = num_gpus
        io.write_json_file(self.config_json, self.config)

    def _use_dtms(self) -> bool:
        """Check if distance transform maps are used in the training."""
        # Check if the loss function uses distance transform maps.
        return self.config["training"]["loss"]["params"]["use_dtms"]

    def _setup_folds(self) -> None:
        """Setup data paths and parameters for a specific fold.

        Args:
            fold: The fold number to set up data for.
        """
        # Get fold setup from the paths dataframe. For each fold, we will
        # create a dictionary with the training and validation images and
        # labels. If we are using distance transform maps, we will also
        # create a dictionary with the training distance transform maps. We will
        # also determine the number of training steps per epoch, which is
        # max(250, len(train_images) // batch_size).
        training = self.config["training"]
        self.folds = {}
        for fold in range(training["nfolds"]):
            self.folds[fold] = {}
            train_ids = list(self.paths.loc[self.paths["fold"]!= fold]["id"])
            test_ids = list(self.paths.loc[self.paths["fold"] == fold]["id"])

            # Get list of training images and labels.
            train_images = training_utils.get_npy_paths(
                data_dir=self.numpy_dir / "images",
                patient_ids=train_ids,
            )
            train_labels = training_utils.get_npy_paths(
                data_dir= self.numpy_dir / "labels",
                patient_ids=train_ids,
            )

            # Get list of validation images and labels.
            val_images = training_utils.get_npy_paths(
                data_dir=self.numpy_dir / "images",
                patient_ids=test_ids,
            )
            val_labels = training_utils.get_npy_paths(
                data_dir=self.numpy_dir / "labels",
                patient_ids=test_ids,
            )

            # If we are using distance transform maps, get the list of training
            # distance transform maps.
            train_dtms = None
            if self._use_dtms():
                train_dtms = training_utils.get_npy_paths(
                    data_dir=self.numpy_dir / "dtms",
                    patient_ids=train_ids,
                )

            # Split training data into training and validation sets if the
            # validation percentage is greater than zero. The idea here is to
            # leave the original validation set as an unseen test set and use
            # the smaller partition of the training dataset as the validation
            # set to pick the best model.
            if training["val_percent"] > 0.0:
                split_inputs = [train_images, train_labels]
                if self._use_dtms():
                    split_inputs.append(train_dtms)

                splits = train_test_split(
                    *split_inputs,
                    test_size=training["val_percent"],
                    random_state=training["seed"],
                )

                # Unpack while handling optional DTMs.
                (
                    train_images, val_images, train_labels,
                    val_labels, *maybe_dtms
                ) = splits
                if self._use_dtms():
                    train_dtms, _ = maybe_dtms

            # Sanity check the fold data.
            training_utils.sanity_check_fold_data(
                fold=fold,
                use_dtms=self._use_dtms(),
                train_images=train_images,
                train_labels=train_labels,
                val_images=val_images,
                val_labels=val_labels,
                train_dtms=train_dtms,
            )

            # Save the fold configuration.
            self.folds[fold]["train_images"] = train_images
            self.folds[fold]["train_labels"] = train_labels
            self.folds[fold]["val_images"] = val_images
            self.folds[fold]["val_labels"] = val_labels
            self.folds[fold]["train_dtms"] = train_dtms
            self.folds[fold]["steps_per_epoch"] = max(
                training["min_steps_per_epoch"],
                math.ceil(len(train_images) / max(1, self.batch_size)),
            )

    def build_components(self, rank: int, world_size: int) -> Dict[str, Any]:
        """Build the model, loss function, and optimizer components."""
        training = self.config["training"]

        # Build the model based on the architecture and parameters specified in
        # the configuration file.
        model = get_model(
            self.config["model"]["architecture"],
            **self.config["model"]["params"]
        )

        use_ddp = world_size > 1
        # Make batch normalization compatible with DDP. This only matters if
        # the model uses batch normalization layers. None of the current MIST
        # models use batch normalization, but this is a good practice to
        # ensure compatibility with DDP if a new model is added in the future.
        if use_ddp:
            model = nn.SyncBatchNorm.convert_sync_batchnorm(model)

        # Send model to device.
        model.to(torch.device(f"cuda:{rank}"))

        # Set up model for distributed data parallel training.
        if use_ddp:
            model = DDP(model, device_ids=[rank])

        # Get loss function. First get the loss function from the registry.
        # We then wrap it in a DeepSupervisionLoss, which will handle
        # deep supervision if the model supports it.
        loss_function = get_loss(training["loss"]["name"])()
        loss_function = DeepSupervisionLoss(loss_function)

        # Some composite loss functions require a scheduler for the
        # composite loss weight. Get the scheduler if it is specified in the
        # configuration file.
        if training["loss"]["params"]["composite_loss_weighting"] is not None:
            # Get the alpha scheduler for the composite loss weight.
            # This is used to adjust the weight of the composite loss during
            # training.
            composite_loss_weighting = (
                get_alpha_scheduler(
                    training["loss"]["params"]["composite_loss_weighting"],
                    num_epochs=training["epochs"],
                )
            )
        else:
            composite_loss_weighting = None

        # Get the optimizer.
        eps = (
            TrainerConstants.AMP_EPS if training["amp"]
            else TrainerConstants.NO_AMP_EPS
        )
        optimizer = get_optimizer(
            name=training["optimizer"],
            params=model.parameters(),
            learning_rate=training["learning_rate"],
            weight_decay=training["l2_penalty"],
            eps=eps,
        )

        # Get learning rate scheduler.
        lr_scheduler = get_lr_scheduler(
            name=training["lr_scheduler"],
            optimizer=optimizer,
            epochs=training["epochs"],
        )

        # Get gradient scaler if AMP is enabled.
        scaler = torch.amp.GradScaler("cuda") if training["amp"] else None # type: ignore

        return {
            "model": model,
            "loss_function": loss_function,
            "composite_loss_weighting": composite_loss_weighting,
            "optimizer": optimizer,
            "lr_scheduler": lr_scheduler,
            "scaler": scaler,
            "epoch": 0,
            "global_step": 0,
            "best_val_loss": np.inf,
        }

    def setup(self, rank: int, world_size: int) -> None:
        """Initialize the process group for distributed training."""
        if dist.is_initialized() or world_size == 1:
            return

        # Set the environment variables for distributed training.
        hw = self.config["training"]["hardware"]
        os.environ["MASTER_ADDR"] = hw["master_addr"]
        os.environ["MASTER_PORT"] = str(hw["master_port"])
        dist.init_process_group(
            hw["communication_backend"], rank=rank, world_size=world_size
        )

    # Clean up processes after distributed training
    def cleanup(self) -> None:
        """Clean up processes after distributed training."""
        if dist.is_initialized():
            dist.destroy_process_group()

    def train_fold(self, fold: int, rank: int, world_size: int) -> None:
        """Generic training loop for a single fold."""
        # Set up for distributed training.
        use_ddp = world_size > 1
        torch.cuda.set_device(rank)
        self.setup(rank, world_size)

        # Set random seed for reproducibility.
        self._set_seed(self.config["training"]["seed"])

        # Get the fold data.
        fold_data = self.folds[fold]
        if use_ddp and len(fold_data["val_images"]) < world_size:
            raise ValueError(
                "Not enough validation data for the number of GPUs. "
                "Ensure that the validation set is large enough for the number "
                "of GPUs being used or reduce the number of GPUs."
            )
        val_steps = math.ceil(len(fold_data["val_images"]) / max(1, world_size))

        # Build components for the fold.
        state = self.build_components(rank=rank, world_size=world_size)

        # Build data loaders for the fold.
        train_loader, val_loader = self.build_dataloaders(
            fold_data=self.folds[fold], rank=rank, world_size=world_size,
        )

        # Only log metrics on first process (i.e., rank 0).
        if rank == 0:
            # Compute running averages for training and validation losses.
            running_train_loss = training_utils.RunningMean()
            running_val_loss = training_utils.RunningMean()

            # Set up tensorboard summary writer.
            logs_writer = SummaryWriter(str(self.logs_dir / f"fold_{fold}"))

            # Path and name for best model for this fold.
            model_name = str(self.models_dir / f"fold_{fold}.pt")

        # Stop training flag if we encounter nan or inf losses.
        stop_training = torch.tensor(
            [0], dtype=torch.int, device=f"cuda:{rank}"
        )

        # Start training for the specified number of epochs.
        for epoch in range(state["epoch"], self.config["training"]["epochs"]):
            # Update the epoch in the state.
            state["epoch"] = epoch

            # Set up model for training.
            state["model"].train()

            # Log progress on the first rank.
            if rank == 0:
                with progress_bar.TrainProgressBar(
                    current_epoch=epoch + 1,
                    fold=fold,
                    epochs= self.config["training"]["epochs"],
                    train_steps=fold_data["steps_per_epoch"],
                ) as pb:
                    for _ in range(fold_data["steps_per_epoch"]):
                        # Get a batch of training data.
                        batch = train_loader.next()[0]

                        # Compute loss and perform training step.
                        loss = self.training_step(state=state, data=batch)

                        # Update the global step in the state.
                        state["global_step"] += 1

                        # Detach and aggregate across all ranks (mean).
                        with torch.no_grad():
                            loss_det = loss.detach()
                            if use_ddp:
                                dist.all_reduce(loss_det, op=dist.ReduceOp.SUM)
                                mean_loss = (loss_det / world_size).item()
                            else:
                                mean_loss = loss_det.item()

                            # Check for NaN/Inf on rank 0
                            if not np.isfinite(mean_loss):
                                self.console.print(
                                    "[bold red]Stopping training: Detected NaN"
                                    "or inf loss value![/bold red]\n"
                                )
                                stop_training[0] = 1

                        # Update running average of training loss.
                        train_mean_loss = running_train_loss(mean_loss)

                        # Update progress bar.
                        pb.update(
                            loss=train_mean_loss,
                            lr=state["optimizer"].param_groups[0]["lr"]
                        )
            else:
                # For all other ranks, just perform the training step.
                for _ in range(fold_data["steps_per_epoch"]):
                    # Get a batch of training data.
                    batch = train_loader.next()[0]

                    # Compute loss and perform training step.
                    loss = self.training_step(state=state, data=batch)

                    # Update the global step in the state.
                    state["global_step"] += 1

                    # Aggregate training losses across ranks.
                    if use_ddp:
                        with torch.no_grad():
                            loss_det = loss.detach()
                            dist.all_reduce(loss_det, op=dist.ReduceOp.SUM)

            # Broadcast stop flag so all ranks exit together if needed.
            if use_ddp:
                dist.broadcast(stop_training, src=0)
            if stop_training.item() == 1:
                if rank == 0:
                    logs_writer.close()
                self.cleanup()
                return  # Exit training early.

            # Update learning rate scheduler.
            state["lr_scheduler"].step()

            # Wait for all processes to finish the training part of the epoch.
            if use_ddp:
                dist.barrier()

            # Start validation phase.
            state["model"].eval()
            with torch.no_grad():
                if rank == 0:
                    with progress_bar.ValidationProgressBar(val_steps) as pbv:
                        for _ in range(val_steps):
                            # Get a batch of validation data.
                            batch = val_loader.next()[0]

                            # Compute validation loss.
                            val_loss = self.validation_step(
                                state=state, data=batch
                            )

                            # Aggregate mean across ranks.
                            val_det = val_loss.detach()
                            if use_ddp:
                                dist.all_reduce(val_det, op=dist.ReduceOp.SUM)
                                mean_val = (val_det / world_size).item()
                            else:
                                mean_val = val_det.item()

                            # Update running average of validation loss.
                            val_mean_loss = running_val_loss(mean_val)

                            # Update progress bar.
                            pbv.update(loss=val_mean_loss)

                    # Log training and validation losses. Check if the
                    # validation loss is the best so far.
                    if val_mean_loss < state["best_val_loss"]:
                        self.console.print(
                            "[bold green]Validation loss IMPROVED from "
                            f"{state['best_val_loss']:.4f} to "
                            f"{val_mean_loss:.4f}[/bold green]\n"
                        )

                        # Update the best validation loss.
                        state["best_val_loss"] = val_mean_loss

                        # Save the model.
                        # Modify so we can load cleanly in non-DDP contexts.
                        to_save = (
                            state["model"].module
                            if hasattr(state["model"], "module")
                            else state["model"]
                        )
                        torch.save(to_save.state_dict(), model_name)
                    else:
                        self.console.print("Validation loss did not improve.\n")
                else:
                    # For all other ranks, just perform the validation step.
                    for _ in range(val_steps):
                        # Get a batch of validation data.
                        batch = val_loader.next()[0]

                        # Compute validation loss.
                        val_loss = self.validation_step(state=state, data=batch)

                        # Aggregate validation losses across ranks.
                        if use_ddp:
                            val_det = val_loss.detach()
                            dist.all_reduce(val_det, op=dist.ReduceOp.SUM)

            # Reset the dataloaders for the next epoch.
            train_loader.reset()
            val_loader.reset()

            # Log the running losses to tensorboard.
            if rank == 0:
                summary_data = {
                    "train": float(train_mean_loss),
                    "validation": float(val_mean_loss),
                }
                logs_writer.add_scalars("losses", summary_data, epoch + 1)
                logs_writer.flush()

                # Reset states of running losses for the next epoch.
                running_train_loss.reset_states()
                running_val_loss.reset_states()

            # Wait for all processes to finish before starting the next epoch.
            if use_ddp:
                dist.barrier()

        # Close the tensorboard writer.
        if rank == 0:
            logs_writer.close()

        # Clean up distributed processes.
        self.cleanup()

    def run_cross_validation(self, rank: int, world_size: int) -> None:
        """Run cross-validation for selected folds."""
        # Display the start of training message.
        if rank == 0:
            self.console.print("\n[bold]Starting training[/bold]\n")

        for fold in self.config["training"]["folds"]:
            # Train the model for the current fold.
            self.train_fold(fold=fold, rank=rank, world_size=world_size)

    def fit(self):
        """Fit the model using multiprocessing.

        This function uses multiprocessing to train the model on multiple GPUs.
        It uses the `torch.multiprocessing.spawn` function to create multiple
        instances of the training function, each on a separate GPU.
        """
        # Enable some performance optimizations.
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        torch.backends.cudnn.benchmark = True

        # Train model.
        world_size = torch.cuda.device_count()
        if world_size > 1:
            mp.spawn( # type: ignore
                self.run_cross_validation,
                args=(world_size,),
                nprocs=world_size,
                join=True,
            )
        # To enable pdb do not spawn multiprocessing for world_size = 1.
        else:
            self.run_cross_validation(0, world_size)
