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
"""Inference runners for MIST segmentation pipeline.

This module contains high-level entry points for running full-resolution
3D segmentation inference using trained MIST models. It includes runners
for fold-based evaluation and general test-time prediction from CSV input.
"""
import argparse
import os
from typing import Any, Dict, Optional, Union, List
import ants
import numpy as np
import pandas as pd
import rich
import torch

# MIST imports.
from mist.utils import progress_bar, io
from mist.inference import inference_utils
from mist.inference.inference_constants import InferenceConstants as ic
from mist.inference.predictor import Predictor
from mist.data_loading import dali_loader
from mist.models import model_loader
from mist.inference.ensemblers.ensembler_registry import get_ensembler
from mist.inference.tta.strategies import get_strategy
from mist.inference.inferers.inferer_registry import get_inferer
from mist.postprocessing.postprocessor import Postprocessor
from mist.preprocessing import preprocess
from mist.preprocessing import preprocessing_utils
from mist.training import training_utils


def predict_single_example(
    preprocessed_image: torch.Tensor,
    original_ants_image: ants.core.ants_image.ANTsImage,
    mist_configuration: Dict[str, Any],
    predictor: Predictor,
    foreground_bounding_box: Optional[Dict[str, int]]=None,
) -> ants.core.ants_image.ANTsImage:
    """Predict on a single example using a Predictor instance.

    Args:
        preprocessed_image: Input image as a PyTorch tensor (1, C, D, H, W).
        original_ants_image: Original ANTs image for spatial restoration.
        mist_configuration: Configuration dictionary with MIST parameters.
        predictor: A callable Predictor instance.
        foreground_bounding_box: Optional crop bounding box.

    Returns:
        ANTs image of the final prediction, in original spatial space.
    """
    # Training vs original labels.
    n_classes = mist_configuration["model"]["params"]["out_channels"]
    training_labels: List[int] = list(range(n_classes))
    original_labels: List[int] = mist_configuration["dataset_info"]["labels"]

    # Run prediction via Predictor (handles TTA + ensembling internally).
    prediction = predictor(preprocessed_image)

    # Convert to discrete labels, remove batch dimension, and move to CPU.
    prediction = torch.argmax(prediction, dim=ic.ARGMAX_AXIS)
    prediction = prediction.squeeze(dim=ic.BATCH_AXIS)
    prediction = prediction.to(torch.float32).cpu().numpy()

    # Ensure bounding box is defined if cropping was used.
    if (
        mist_configuration["preprocessing"]["crop_to_foreground"]
        and foreground_bounding_box is None
    ):
        foreground_bounding_box = preprocessing_utils.get_fg_mask_bbox(
            original_ants_image
        )

    # Restore original spacing, orientation, and header.
    prediction = inference_utils.back_to_original_space(
        raw_prediction=prediction,
        original_ants_image=original_ants_image,
        target_spacing=mist_configuration["preprocessing"]["target_spacing"],
        training_labels=training_labels,
        foreground_bounding_box=foreground_bounding_box,
    )

    # Remap labels to match original dataset.
    if training_labels != original_labels:
        prediction = inference_utils.remap_mask_labels(
            prediction.numpy(), original_labels
        )
        prediction = original_ants_image.new_image_like(data=prediction) # type: ignore
    return prediction.astype("uint8")


def test_on_fold(
    mist_args: argparse.Namespace,
    fold_number: int,
    device: Optional[Union[str, torch.device]]=None,
) -> None:
    """Run inference on the test set for a given fold.

    This function runs sliding-window inference on all test samples assigned to
    a particular fold using the trained model for that fold. Predictions are
    restored to original space and saved as NIfTI files.

    Args:
        mist_args: Parsed MIST CLI arguments as an argparse.Namespace.
        fold_number: The fold number to run inference on.
        device: The device to use for inference. Default is "cuda".

    Returns:
        None. Saves predictions to ./results/predictions/train/raw/ directory.

    Raises:
        FileNotFoundError: If an input image is missing.
        RuntimeError or ValueError: If prediction fails during execution.
    """
    # Set device to CPU or GPU.
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")

    # Extract the results directory from the MIST arguments.
    results_dir = os.path.join(mist_args.results)
    numpy_dir = os.path.join(mist_args.numpy)
    models_dir = os.path.join(results_dir, "models")
    config_path = os.path.join(results_dir, "config.json")
    config = io.read_json_file(config_path)

    # Get dataframe with paths for test images.
    train_df = pd.read_csv(os.path.join(results_dir, "train_paths.csv"))
    test_df = train_df.loc[train_df["fold"] == fold_number]

    # Construct paths to preprocessed .npy image volumes.
    test_image_paths = training_utils.get_npy_paths(
        data_dir=os.path.join(numpy_dir, "images"),
        patient_ids=list(test_df["id"]),
    )

    # Get bounding box data.
    foreground_bounding_boxes = pd.read_csv(
        os.path.join(results_dir, "fg_bboxes.csv")
    )

    # Get DALI loader for streaming preprocessed numpy files.
    test_loader = dali_loader.get_test_dataset(
        image_paths=test_image_paths,
        seed=config["training"]["seed"],
        num_workers=config["training"]["hardware"]["num_cpu_workers"],
    )

    # Load model.
    weights_path = os.path.join(models_dir, f"fold_{fold_number}.pt")
    model = model_loader.load_model_from_config(weights_path, config)
    model.eval()
    model.to(device)

    # Create Predictor instance.
    # Inferer, ensembler, and TTA transforms are set up for sliding window
    # inference. This is the default mode of operation for MIST, but future
    # versions may allow for other modes.
    inferer_name = config["inference"]["inferer"]["name"]
    inferer_params = config["inference"]["inferer"]["params"]
    ensembler_strategy = config["inference"]["ensemble"]["strategy"]
    tta_enabled = config["inference"]["tta"]["enabled"]
    tta_strategy = config["inference"]["tta"]["strategy"]

    # Add device to inferer parameters.
    inferer_params["device"] = device
    inferer = get_inferer(inferer_name)(**inferer_params)
    ensembler = get_ensembler(ensembler_strategy)
    if tta_enabled:
        tta_transforms = get_strategy(tta_strategy)()
    else:
        tta_transforms = get_strategy("none")()
    predictor = Predictor(
        models=[model],
        inferer=inferer,
        ensembler=ensembler,
        tta_transforms=tta_transforms,
        device=device,
    )

    # Create output directory.
    output_directory = os.path.join(results_dir, "predictions", "train", "raw")
    os.makedirs(output_directory, exist_ok=True)

    # Progress bar and error messages.
    console = rich.console.Console()
    error_messages = []

    # Begin inference loop.
    with (
        torch.no_grad(),
        progress_bar.get_progress_bar(f'Testing on fold {fold_number}') as pb
    ):
        for image_index in pb.track(range(len(test_df))):
            patient = test_df.iloc[image_index].to_dict()
            patient_id = patient["id"]
            filename = os.path.join(output_directory, f"{patient_id}.nii.gz")
            try:
                # Get image paths from patient dictionary. Load the original
                # image using ANTs. If this is a multi-modality image, we need
                # load the first image in the list. MIST already checks that
                # the images are the same size and spacing.
                image_paths = [
                    v for k, v in patient.items()
                    if k not in ic.PATIENT_DF_IGNORED_COLUMNS
                ]
                original_ants_image = ants.image_read(image_paths[0])

                # DALI loader is assumed to yield batches in the same order as
                # test_df. This is enforced upstream and is not checked here.
                data = test_loader.next()[0]
                preprocessed_image = data["image"]

                # Retrieve the foreground bounding box.
                if (
                    config["preprocessing"]["crop_to_foreground"]
                    and not config["preprocessing"]["skip"]
                ):
                    foreground_bounding_box = (
                        foreground_bounding_boxes.loc[
                            foreground_bounding_boxes["id"] == patient_id
                        ].iloc[0]
                    )
                    foreground_bounding_box = foreground_bounding_box.to_dict()
                else:
                    foreground_bounding_box = None

                # Perform prediction and restoration to original space.
                prediction = predict_single_example(
                    preprocessed_image=preprocessed_image,
                    original_ants_image=original_ants_image,
                    mist_configuration=config,
                    predictor=predictor,
                    foreground_bounding_box=foreground_bounding_box,
                )
            except (FileNotFoundError, RuntimeError, ValueError) as e:
                error_messages.append(
                    f"[red][Error] Prediction failed for {patient_id}: "
                    f"{str(e)}[/red]"
                )
            else:
                # Write prediction as .nii.gz file.
                ants.image_write(prediction, filename)

    # Print error messages if any occurred during inference.
    if error_messages:
        for error in error_messages:
            console.print(error)


def infer_from_dataframe(
    paths_dataframe: pd.DataFrame,
    output_directory: str,
    mist_configuration: Dict[str, Any],
    models_directory: str,
    postprocessing_strategy_filepath: Optional[str]=None,
    device: Optional[Union[str, torch.device]]=None,
) -> None:
    """Run test-time inference on a set of input images.

    This function performs sliding-window inference on a set of images defined
    in a pandas dataframe. It supports ensembling, test-time augmentation, and
    optional postprocessing. Each prediction is restored to its original
    spatial space using header and spacing information from the input image.

    Args:
        paths_dataframe: A pandas dataframe each row corresponds to a patient
            and contains columns for different image paths. If the dataframe has
            columns "mask" or "fold", the information in these columns is
            ignored.
        output_directory: The destination directory where predictions will be
            saved as NIfTI files.
        mist_configuration: Dictionary containing MIST configuration parameters.
            This should include the patch size, target spacing, and other
            relevant parameters.
        models_directory: Directory containing the trained models. The models
            should be in the format "model_fold_0.pt", "model_fold_1.pt", etc.
            The model_config.json file should also be in this directory.
        postprocessing_strategy_filepath: Optional path to a JSON file
            containing postprocessing strategies. If provided, the strategies
            will be applied to the predictions.
        device: The device to use for inference. Default is "cuda".

    Returns:
        None. Saves all predictions to the specified output directory.

    Raises:
        FileNotFoundError: If the paths CSV, configuration file, or model files,
            or the optional postprocess strategy files cannot be found. Also
            raises if the input image is missing.
        RuntimeError or ValueError: If inference or postprocessing fails.
    """
    # Set device to CPU or GPU.
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")

    # Load models from the specified directory.
    models_list = inference_utils.load_test_time_models(
        models_dir=models_directory,
        mist_config=mist_configuration,
        device=device,
    )

    # Set up the predictor for inference.
    # Inferer, ensembler, and TTA transforms are set up for sliding window
    # inference. This is the default mode of operation for MIST, but future
    # versions may allow for other modes.
    inferer_name = mist_configuration["inference"]["inferer"]["name"]
    inferer_params = mist_configuration["inference"]["inferer"]["params"]
    ensembler_strategy = mist_configuration["inference"]["ensemble"]["strategy"]
    tta_enabled = mist_configuration["inference"]["tta"]["enabled"]
    tta_strategy = mist_configuration["inference"]["tta"]["strategy"]

    # Add device to inferer parameters.
    inferer_params["device"] = device
    inferer = get_inferer(inferer_name)(**inferer_params)
    ensembler = get_ensembler(ensembler_strategy)
    if tta_enabled:
        tta_transforms = get_strategy(tta_strategy)()
    else:
        tta_transforms = get_strategy("none")()
    predictor = Predictor(
        models=models_list,
        inferer=inferer,
        ensembler=ensembler,
        tta_transforms=tta_transforms,
        device=device,
    )

    # If a postprocess strategy file is provided, check if it exists and
    # initialize the postprocessor.
    postprocessor = None
    if postprocessing_strategy_filepath is not None:
        if not os.path.exists(postprocessing_strategy_filepath):
            raise FileNotFoundError(
                "Postprocess strategy file not found: "
                f"{postprocessing_strategy_filepath}"
            )
        postprocessor = Postprocessor(
            strategy_path=postprocessing_strategy_filepath,
        )

    # Create destination directory if it does not exist.
    os.makedirs(output_directory, exist_ok=True)

    # Set up rich progress bar.
    console = rich.console.Console()
    error_messages = []

    # Start inference loop.
    with progress_bar.get_progress_bar("Running inference") as pb:
        for patient_index in pb.track(range(len(paths_dataframe))):
            patient = paths_dataframe.iloc[patient_index].to_dict()
            patient_id = patient["id"]
            prediction_filename = os.path.join(
                output_directory, f"{patient_id}.nii.gz"
            )
            try:
                # Validate the input patient data.
                anchor_image, image_paths = (
                    inference_utils.validate_inference_images(patient)
                )

                # Preprocess the input images using the MIST preprocessing
                # pipeline. This will handle normalization, cropping, and
                # resizing as per the MIST configuration. If the skip flag is
                # set, normalization will not be applied.
                preprocessed_example = preprocess.preprocess_example(
                    config=mist_configuration,
                    image_paths_list=image_paths,
                )

                # Convert the preprocessed image to a PyTorch tensor and move it
                # to the device.
                preprocessed_image = np.transpose( # type: ignore
                    preprocessed_example["image"], # type: ignore
                    axes=ic.NUMPY_TO_TORCH_TRANSPOSE_AXES
                )
                preprocessed_image = np.expand_dims(
                    preprocessed_image, axis=ic.NUMPY_TO_TORCH_EXPAND_DIMS_AXES
                )
                preprocessed_image = torch.Tensor(preprocessed_image.copy())
                preprocessed_image = preprocessed_image.to(torch.float32)
                preprocessed_image = preprocessed_image.to(device)


                # Perform prediction and restoration to original space.
                prediction = predict_single_example(
                    preprocessed_image=preprocessed_image,
                    original_ants_image=anchor_image,
                    mist_configuration=mist_configuration,
                    predictor=predictor,
                    foreground_bounding_box=preprocessed_example["fg_bbox"], # type: ignore
                )

                # Apply postprocessing if a strategy is provided.
                if postprocessor is not None:
                    prediction, postprocessing_error_messages = (
                        postprocessor.apply_strategy_to_single_example(
                            patient_id=patient_id,
                            mask=prediction,
                        )
                    )

                    # If there are any error messages from postprocessing, add
                    # them to the error messages list.
                    if postprocessing_error_messages:
                        error_messages.extend(postprocessing_error_messages)
            except (FileNotFoundError, RuntimeError, ValueError) as e:
                error_messages.append(
                    f"[red][Error] Prediction failed for {patient_id}: "
                    f"{str(e)}[/red]"
                )
                continue
            else:
                # Write prediction as .nii.gz file.
                ants.image_write(prediction, prediction_filename)

    # Print a summary of the inference results. If there are any error or
    # warning messages, print them. Otherwise, print a success message.
    if error_messages:
        console.print(
            rich.text.Text( # type: ignore
                "Inference completed with the following messages:",
                style="bold underline"
            )
        )
        for message in error_messages:
            console.print(message)
    else:
        console.print(
            "[green]Inference completed successfully![/green]"
        )
