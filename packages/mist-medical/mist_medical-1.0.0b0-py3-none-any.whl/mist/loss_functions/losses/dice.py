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
"""Soft Dice loss function for segmentation tasks."""
import torch

# MIST imports.
from mist.loss_functions.base import SegmentationLoss
from mist.loss_functions.loss_registry import register_loss


@register_loss(name="dice")
class DiceLoss(SegmentationLoss):
    """Soft Dice loss function for segmentation tasks.

    For each class, the Dice loss is defined as:
        L(x, y) = ||x - y||^2 / (||x||^2 + ||y||^2 + smooth)

    We then take the mean of the Dice loss across all classes. By default, the
    Dice loss function includes the background class.

    Attributes:
        smooth: A small constant to prevent division by zero.
    """
    def __init__(self, exclude_background: bool=False):
        """Initialize Dice loss.

        Args:
            exclude_background: If True, the background class (class 0) is
                excluded from the loss computation.
        """
        super().__init__(exclude_background=exclude_background)
        self.smooth = 1e-6

    def forward(
        self,
        y_true: torch.Tensor,
        y_pred: torch.Tensor,
    ) -> torch.Tensor:
        """Compute the Dice loss.

        Args:
            y_true: Ground truth tensor of shape (B, H, W, D).
            y_pred: Raw model output tensor of shape (B, C, H, W, D).

        Returns:
            Dice loss as a scalar tensor.
        """
        y_true, y_pred = self.preprocess(y_true, y_pred)

        numerator = torch.sum(
            torch.square(y_true - y_pred), dim=self.spatial_dims
        )
        denominator = (
            torch.sum(torch.square(y_true), dim=self.spatial_dims) +
            torch.sum(torch.square(y_pred), dim=self.spatial_dims) +
            self.smooth
        )

        loss = numerator / denominator            # Per class.
        loss = torch.mean(loss, dim=1)            # Mean over classes.
        return torch.mean(loss)                   # Mean over batch.
