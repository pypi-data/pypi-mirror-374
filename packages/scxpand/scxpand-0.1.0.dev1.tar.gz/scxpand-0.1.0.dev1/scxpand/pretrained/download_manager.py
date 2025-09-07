"""Download manager for pre-trained models using Pooch.

This module handles downloading pre-trained models using the Pooch library,
which provides robust caching, integrity checking, and progress tracking.
"""

from pathlib import Path

import pooch

from scxpand.util.logger import get_logger

from .model_registry import get_pretrained_model_info


logger = get_logger()


def download_pretrained_model(
    model_name: str | None = None,
    model_url: str | None = None,
    cache_dir: Path | None = None,
) -> Path:
    """Download a pre-trained model and return the path to the extracted model.

    Uses Pooch for robust caching, integrity checking, and automatic extraction.
    Supports both registry models and direct URLs, including DOI URLs.

    Args:
        model_name: Name of pre-trained model from registry (alternative to model_url)
        model_url: Direct URL to model file (alternative to model_name)
                  Supports HTTP/HTTPS URLs and DOI format (e.g., "doi:10.5281/zenodo.1234567")
        cache_dir: Custom cache directory (uses Pooch default if None)

    Returns:
        Path to the extracted model directory or file

    Raises:
        ValueError: If neither model_name nor model_url is provided, or if both are provided

    Examples:
        >>> # Registry model
        >>> model_path = download_pretrained_model(
        ...     model_name="autoencoder_pan_cancer"
        ... )
        >>>
        >>> # Direct URL
        >>> model_path = download_pretrained_model(
        ...     model_url="https://zenodo.org/records/7625517/files/model.zip?download=1"
        ... )
        >>>
        >>> # DOI URL (Pooch handles this automatically)
        >>> model_path = download_pretrained_model(
        ...     model_url="doi:10.5281/zenodo.7625517"
        ... )
    """
    # Validate inputs
    if model_name is None and model_url is None:
        raise ValueError("Either model_name or model_url must be provided")

    if model_name is not None and model_url is not None:
        raise ValueError("Cannot specify both model_name and model_url. Use one or the other.")

    # Set up cache directory
    cache_path = str(cache_dir) if cache_dir else pooch.os_cache("scxpand")

    if model_name is not None:
        # Use registry model
        model_info = get_pretrained_model_info(model_name)

        if not model_info.url:
            raise ValueError(
                f"Download URL not configured for model '{model_name}'. "
                "Please contact the maintainers or use a local model."
            )

        download_url = model_info.url
        known_hash = model_info.sha256

        logger.info(f"Downloading registry model '{model_name}' from: {download_url}")
    else:
        # Use direct URL
        download_url = model_url
        known_hash = None  # No checksum available for direct URLs

        logger.info(f"Downloading model from URL: {model_url}")

    # Let Pooch handle everything - it will:
    # 1. Download the file if not cached
    # 2. Verify hash if provided
    # 3. Auto-detect and extract archives
    # 4. Return path to extracted content
    try:
        model_path = pooch.retrieve(
            url=download_url,
            known_hash=known_hash,
            path=cache_path,
            progressbar=True,
            # Let Pooch auto-detect the processor based on file extension
            processor=pooch.Untar() if download_url.endswith((".tar", ".tar.gz", ".tgz")) else pooch.Unzip(),
        )
    except Exception as e:
        raise FileNotFoundError(f"Failed to download model from {download_url}: {e}") from e

    result_path = Path(model_path)

    # If Pooch returned a file path, return its parent directory
    # (since we want the extracted directory, not the archive file)
    if result_path.is_file():
        result_path = result_path.parent

    logger.info(f"Model successfully downloaded and cached at: {result_path}")
    return result_path
