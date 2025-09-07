"""Registry for pre-trained models and their metadata.

This module defines the available pre-trained models, their Google Drive links,
and associated metadata for automatic download and inference.
"""

from dataclasses import dataclass
from typing import Dict

from scxpand.util.classes import ModelType


@dataclass
class PretrainedModelInfo:
    """Information about a pre-trained model."""

    name: str
    model_type: ModelType
    url: str  # Can be Google Drive direct download URL or any other URL
    version: str
    sha256: str | None = None  # Optional checksum for file integrity


# Registry of available pre-trained models
PRETRAINED_MODELS: Dict[str, PretrainedModelInfo] = {
    "autoencoder_pan_cancer": PretrainedModelInfo(
        name="autoencoder_pan_cancer",
        model_type=ModelType.AUTOENCODER,
        url="",  # To be filled with direct download URL (Google Drive or other)
        version="1.0.0",
        sha256=None,  # Optional: add SHA256 hash for integrity checking
    ),
    "mlp_pan_cancer": PretrainedModelInfo(
        name="mlp_pan_cancer",
        model_type=ModelType.MLP,
        url="",  # To be filled with direct download URL
        version="1.0.0",
        sha256=None,
    ),
    "lightgbm_pan_cancer": PretrainedModelInfo(
        name="lightgbm_pan_cancer",
        model_type=ModelType.LIGHTGBM,
        url="",  # To be filled with direct download URL
        version="1.0.0",
        sha256=None,
    ),
    "logistic_pan_cancer": PretrainedModelInfo(
        name="logistic_pan_cancer",
        model_type=ModelType.LOGISTIC,
        url="",  # To be filled with Zenodo direct download URL
        version="1.0.0",
        sha256=None,
    ),
}


def get_pretrained_model_info(model_name: str) -> PretrainedModelInfo:
    """Get information about a pre-trained model.

    Args:
        model_name: Name of the pre-trained model

    Returns:
        PretrainedModelInfo object containing model metadata

    Raises:
        ValueError: If model_name is not found in registry
    """
    if model_name not in PRETRAINED_MODELS:
        available_models = ", ".join(PRETRAINED_MODELS.keys())
        raise ValueError(f"Pre-trained model '{model_name}' not found. Available models: {available_models}")

    return PRETRAINED_MODELS[model_name]
