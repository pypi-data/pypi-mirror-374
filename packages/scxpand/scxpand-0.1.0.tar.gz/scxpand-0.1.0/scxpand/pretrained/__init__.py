"""Pre-trained model management for scXpand.

This module provides functionality to download and manage pre-trained models
from Google Drive, including automatic model loading for inference.
"""

from .download_manager import download_pretrained_model
from .inference_api import run_inference_with_pretrained
from .model_registry import PRETRAINED_MODELS, get_pretrained_model_info


__all__ = [
    "PRETRAINED_MODELS",
    "download_pretrained_model",
    "get_pretrained_model_info",
    "run_inference_with_pretrained",
]
