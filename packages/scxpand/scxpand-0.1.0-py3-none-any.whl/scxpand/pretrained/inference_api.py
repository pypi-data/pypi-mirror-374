"""Simplified inference API for pre-trained models.

This module provides a high-level API for running inference with pre-trained models,
handling automatic model downloading and loading.
"""

from pathlib import Path
from typing import Union

import anndata as ad

from scxpand.core.prediction import run_prediction_pipeline
from scxpand.util.logger import get_logger
from scxpand.util.model_type import load_model_type

from .download_manager import download_pretrained_model
from .model_registry import get_pretrained_model_info


logger = get_logger()


def run_inference_with_pretrained(
    model_name: str | None = None,
    model_url: str | None = None,
    data_path: Union[str, Path] | None = None,
    adata: ad.AnnData | None = None,
    save_path: Union[str, Path] | None = None,
    batch_size: int | None = None,
    num_workers: int = 4,
    evaluate_metrics: bool = True,
) -> dict:
    """Run inference using a pre-trained model with automatic download.

    This is the unified function for running inference with pre-trained models.
    It handles automatic model downloading, loading, and inference in a single call.
    Works with both file-based and in-memory data.

    Args:
        model_name: Name of pre-trained model from registry (alternative to model_url)
        model_url: Direct URL to model ZIP file (alternative to model_name)
        data_path: Path to input data file (h5ad format) - alternative to adata
        adata: In-memory AnnData object - alternative to data_path
        save_path: Directory to save prediction results (optional)
        batch_size: Batch size for inference (uses model default if None)
        num_workers: Number of workers for data loading
        evaluate_metrics: Whether to compute evaluation metrics

    Returns:
        Dictionary containing prediction results and evaluation metrics

    Raises:
        ValueError: If neither model_name nor model_doi provided, or neither data_path nor adata provided
        FileNotFoundError: If data_path does not exist

    Examples:
        >>> import scxpand
        >>>
        >>> # Registry model inference
        >>> results = scxpand.run_inference_with_pretrained(
        ...     model_name="pan_cancer_autoencoder", data_path="my_data.h5ad"
        ... )
        >>>
        >>> # Direct URL inference (any external model)
        >>> results = scxpand.run_inference_with_pretrained(
        ...     model_url="https://your-platform.com/model.zip",
        ...     data_path="my_data.h5ad",
        ... )
        >>>
        >>> # In-memory inference
        >>> import scanpy as sc
        >>> adata = sc.read_h5ad("my_data.h5ad")
        >>> results = scxpand.run_inference_with_pretrained(
        ...     model_name="pan_cancer_autoencoder", adata=adata
        ... )
    """
    # Validate inputs
    if model_name is None and model_url is None:
        raise ValueError("Either model_name or model_url must be provided")

    if model_name is not None and model_url is not None:
        raise ValueError("Cannot specify both model_name and model_url. Use one or the other.")

    if adata is None and data_path is None:
        raise ValueError("Either adata or data_path must be provided")

    if data_path is not None:
        data_path = Path(data_path)
        if not data_path.exists():
            raise FileNotFoundError(f"Data file not found: {data_path}")

    # Handle model information and download
    if model_name is not None:
        # Use registry model
        model_info = get_pretrained_model_info(model_name)
        logger.info(f"Using registry model: {model_info.name}")
        logger.info(f"Model version: {model_info.version}")
        logger.info("Model type will be auto-detected from model_type.txt")

        # Download using registry
        model_path = download_pretrained_model(model_name=model_name)

        # Model type will be auto-detected from model_type.txt file
    else:
        # Use direct URL
        logger.info(f"Using direct URL: {model_url}")

        # Download using URL
        model_path = download_pretrained_model(model_url=model_url)

        # For URL models, model type will be auto-detected from model_type.txt file
        model_info = None

    # Set default batch size if not provided
    if batch_size is None:
        batch_size = 1024  # Default batch size

    logger.info(f"Running inference with batch size: {batch_size}")

    # Run the unified prediction pipeline
    results = run_prediction_pipeline(
        model_path=model_path,
        data_path=data_path,
        adata=adata,
        save_path=save_path,
        batch_size=batch_size,
        num_workers=num_workers,
        evaluate_metrics=evaluate_metrics,
    )

    # Load actual model type from model_type.txt file
    actual_model_type = load_model_type(model_path)

    # Add model metadata to results
    if model_info is not None:
        # Registry model
        results["model_info"] = {
            "model_name": model_info.name,  # Registry identifier (e.g., "pan_cancer_mlp")
            "model_type": actual_model_type,
            "version": model_info.version,
            "source": "registry",
        }
    else:
        # URL model
        results["model_info"] = {
            "url": model_url,
            "model_type": actual_model_type,
            "source": "external_url",
        }

    logger.info("Inference completed successfully")
    return results
