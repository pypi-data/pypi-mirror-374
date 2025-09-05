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
"""Registry for segmentation metrics used in evaluation."""
from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional, List
import numpy as np

# MIST imports.
from mist.metrics import segmentation_metrics
from mist.metrics import lesion_wise_metrics


class Metric(ABC):
    """Base class for all metrics."""
    name: str  # Unique identifier.
    best: float  # Ideal value for this metric.
    worst: float  # Worst-case fallback value.

    @abstractmethod
    def __call__(
        self,
        truth: np.ndarray,
        pred: np.ndarray,
        spacing: Tuple[float, float, float],
        **kwargs
    ) -> Optional[float]:
        """Compute the metric.

        Args:
            truth: Ground truth segmentation.
            pred: Predicted segmentation.
            spacing: Voxel spacing in mm (tuple of 3 floats).
            **kwargs: Additional parameters for metric computation.

        Returns:
            Computed metric value, or None if not computable.
        """
        pass # pylint: disable=unnecessary-pass # pragma: no cover


# Global registry for metrics.
METRIC_REGISTRY: Dict[str, Metric] = {}


def register_metric(cls):
    """Decorator to register a metric class."""
    instance = cls()
    METRIC_REGISTRY[instance.name] = instance
    return cls


def get_metric(name: str) -> Metric:
    """Retrieve a metric by name."""
    if name not in METRIC_REGISTRY:
        raise ValueError(f"Metric '{name}' is not registered.")
    return METRIC_REGISTRY[name]


def list_registered_metrics() -> List[str]:
    """List all registered metrics."""
    return sorted(METRIC_REGISTRY.keys())


@register_metric
class DiceCoefficient(Metric):
    """Dice coefficient metric."""
    name = "dice"
    best = 1.0
    worst = 0.0

    def __call__(self, truth, pred, spacing, **kwargs):
        return segmentation_metrics.compute_dice_coefficient(truth, pred)


@register_metric
class Hausdorff95(Metric):
    """95th percentile Hausdorff distance metric."""
    name = "haus95"
    best = 0.0
    worst = float("inf") # Will be dynamically overridden.

    def __call__(self, truth, pred, spacing, **kwargs):
        distances = segmentation_metrics.compute_surface_distances(
            truth, pred, spacing
        )
        return segmentation_metrics.compute_robust_hausdorff(
            distances, percent=95
        )


@register_metric
class SurfaceDice(Metric):
    """Surface Dice metric."""
    name = "surf_dice"
    best = 1.0
    worst = 0.0

    def __call__(self, truth, pred, spacing, **kwargs):
        distances = segmentation_metrics.compute_surface_distances(
            truth, pred, spacing
        )
        return segmentation_metrics.compute_surface_dice_at_tolerance(
            distances, tolerance_mm=kwargs.get("tolerance", 1.0)
        )


@register_metric
class AverageSurfaceDistance(Metric):
    """Average surface distance metric."""
    name = "avg_surf"
    best = 0.0
    worst = float("inf") # Will be dynamically overridden.

    def __call__(self, truth, pred, spacing, **kwargs):
        distances = segmentation_metrics.compute_surface_distances(
            truth, pred, spacing
        )
        return segmentation_metrics.compute_average_surface_distance(distances)


@register_metric
class LesionWiseDice(Metric):
    """Lesion-wise Dice coefficient metric."""
    name = "lesion_wise_dice"
    best = 1.0
    worst = 0.0

    def __call__(self, truth, prediction, spacing, **kwargs):
        result = lesion_wise_metrics.compute_lesion_wise_metrics(
            prediction,
            truth,
            spacing=spacing,
            metrics=["dice"],
            reduction="mean",
        )
        return result.get("lesion_wise_dice", self.worst)


@register_metric
class LesionWiseHausdorff95(Metric):
    """Lesion-wise 95th percentile Hausdorff distance metric."""
    name = "lesion_wise_haus95"
    best = 0.0
    worst = float("inf") # Will be dynamically overridden.

    def __call__(self, truth, prediction, spacing, **kwargs):
        result = lesion_wise_metrics.compute_lesion_wise_metrics(
            prediction,
            truth,
            spacing=spacing,
            metrics=["haus95"],
            reduction="mean",
        )
        return result.get("lesion_wise_haus95", self.worst)

@register_metric
class LesionWiseSurfaceDice(Metric):
    """Lesion-wise surface Dice metric at configurable tolerance."""
    name = "lesion_wise_surf_dice"
    best = 1.0
    worst = 0.0

    def __call__(self, truth, prediction, spacing, **kwargs):
        tolerance = kwargs.get("tolerance", 1.0)
        result = lesion_wise_metrics.compute_lesion_wise_metrics(
            prediction,
            truth,
            spacing=spacing,
            metrics=["surface_dice"],
            surface_dice_tolerance_mm=tolerance,
            reduction="mean",
        )
        return result.get("lesion_wise_surf_dice", self.worst)
