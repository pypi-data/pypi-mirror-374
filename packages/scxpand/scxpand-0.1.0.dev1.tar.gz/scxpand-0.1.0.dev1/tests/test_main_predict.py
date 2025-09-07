"""Tests for the predict and list_pretrained_models functions in main.py."""

from unittest.mock import Mock, patch

import pytest

from scxpand.main import list_pretrained_models, predict


class TestPredictCommand:
    """Tests for the unified predict command."""

    def test_predict_local_model_success(self):
        """Test predict with local model path."""
        with (
            patch("scxpand.main.run_inference") as mock_run_inference,
            patch("scxpand.main.load_eval_indices") as mock_load_indices,
        ):
            # Setup mocks
            mock_load_indices.return_value = [0, 1, 2, 3, 4]

            predict(
                data_path="data/test.h5ad",
                model_path="results/mlp",
                model_type="mlp",
                eval_row_inds="eval_indices.txt",
            )

            # Verify unified inference function was called
            mock_run_inference.assert_called_once()
            call_kwargs = mock_run_inference.call_args[1]
            assert call_kwargs["model_path"] == "results/mlp"
            assert call_kwargs["data_path"] == "data/test.h5ad"
            assert call_kwargs["eval_row_inds"] == [0, 1, 2, 3, 4]
            assert call_kwargs["model_type"] == "mlp"

            mock_load_indices.assert_called_once_with("eval_indices.txt")

    def test_predict_registry_model_success(self):
        """Test predict with registry model name."""
        with patch("scxpand.main.run_inference") as mock_run_inference:
            predict(
                data_path="data/test.h5ad",
                model_name="autoencoder_pan_cancer",
                batch_size=512,
            )

            # Verify unified inference function was called
            mock_run_inference.assert_called_once()
            call_kwargs = mock_run_inference.call_args[1]
            assert call_kwargs["model_name"] == "autoencoder_pan_cancer"
            assert call_kwargs["model_url"] is None
            assert call_kwargs["model_path"] is None
            assert call_kwargs["data_path"] == "data/test.h5ad"
            assert call_kwargs["batch_size"] == 512

    def test_predict_url_model_success(self):
        """Test predict with URL model."""
        with patch("scxpand.main.run_inference") as mock_run_inference:
            predict(
                data_path="data/test.h5ad",
                model_url="https://zenodo.org/records/7625517/files/model.zip?download=1",
                save_path="custom/save/path",
            )

            # Verify unified inference function was called
            mock_run_inference.assert_called_once()
            call_kwargs = mock_run_inference.call_args[1]
            assert call_kwargs["model_name"] is None
            assert call_kwargs["model_url"] == "https://zenodo.org/records/7625517/files/model.zip?download=1"
            assert call_kwargs["model_path"] is None
            assert call_kwargs["data_path"] == "data/test.h5ad"
            assert call_kwargs["save_path"] == "custom/save/path"

    def test_predict_no_model_source_error(self):
        """Test predict raises error when no model source is provided."""
        with pytest.raises(ValueError, match="Must specify one model source"):
            predict(data_path="data/test.h5ad")

    def test_predict_multiple_model_sources_error(self):
        """Test predict raises error when multiple model sources are provided."""
        with pytest.raises(ValueError, match="Cannot specify multiple model sources"):
            predict(
                data_path="data/test.h5ad",
                model_path="results/mlp",
                model_name="autoencoder_pan_cancer",
            )

    def test_predict_multiple_model_sources_all_three_error(self):
        """Test predict raises error when all three model sources are provided."""
        with pytest.raises(ValueError, match="Cannot specify multiple model sources"):
            predict(
                data_path="data/test.h5ad",
                model_path="results/mlp",
                model_name="autoencoder_pan_cancer",
                model_url="https://zenodo.org/records/7625517/files/model.zip?download=1",
            )

    def test_predict_registry_model_with_custom_save_path(self):
        """Test predict with registry model sets default save path correctly."""
        with patch("scxpand.main.run_inference") as mock_run_inference:
            predict(
                data_path="data/test.h5ad",
                model_name="mlp_pan_cancer",
            )

            # Verify default save path for registry model
            call_kwargs = mock_run_inference.call_args[1]
            assert call_kwargs["save_path"] == "results/mlp_pan_cancer_predictions"

    def test_predict_url_model_with_no_default_save_path(self):
        """Test predict with URL model doesn't set default save path."""
        with patch("scxpand.main.run_inference") as mock_run_inference:
            predict(
                data_path="data/test.h5ad",
                model_url="https://zenodo.org/records/7625517/files/model.zip?download=1",
            )

            # Verify no default save path for URL model (user must specify)
            call_kwargs = mock_run_inference.call_args[1]
            assert call_kwargs["save_path"] is None

    def test_predict_local_model_without_model_type(self):
        """Test predict with local model without explicit model type."""
        with patch("scxpand.main.run_inference") as mock_run_inference:
            predict(
                data_path="data/test.h5ad",
                model_path="results/mlp",
            )

            # Verify unified inference function was called without model type validation
            mock_run_inference.assert_called_once()
            call_kwargs = mock_run_inference.call_args[1]
            assert call_kwargs["model_type"] is None

    def test_predict_local_model_with_eval_indices_none(self):
        """Test predict with local model and no eval indices."""
        with patch("scxpand.main.run_inference") as mock_run_inference:
            predict(
                data_path="data/test.h5ad",
                model_path="results/mlp",
                model_type="mlp",
                eval_row_inds=None,
            )

            # Verify eval_row_inds is None
            call_kwargs = mock_run_inference.call_args[1]
            assert call_kwargs["eval_row_inds"] is None


class TestListPretrainedModelsCommand:
    """Tests for the list_pretrained_models command."""

    def test_list_pretrained_models_success(self):
        """Test list_pretrained_models displays all models correctly."""
        mock_models = {
            "model1": Mock(
                model_type=Mock(value="autoencoder"),
                version="1.0.0",
                url="https://example.com/model1.tar.gz",
                sha256="abc123",
            ),
            "model2": Mock(
                model_type=Mock(value="mlp"),
                version="2.0.0",
                url="",
                sha256=None,
            ),
        }

        with (
            patch("scxpand.main.PRETRAINED_MODELS", mock_models),
            patch("scxpand.main.logger") as mock_logger,
        ):
            list_pretrained_models()

            # Verify logger calls
            assert mock_logger.info.call_count >= 2  # At least header and models

            # Check that model information was logged
            logged_messages = [call.args[0] for call in mock_logger.info.call_args_list]

            # Should contain header
            assert any("Available pre-trained models:" in msg for msg in logged_messages)

            # Should contain model names
            assert any("model1" in msg for msg in logged_messages)
            assert any("model2" in msg for msg in logged_messages)

            # Should contain model types
            assert any("autoencoder" in msg for msg in logged_messages)
            assert any("mlp" in msg for msg in logged_messages)

            # Should contain version info
            assert any("1.0.0" in msg for msg in logged_messages)
            assert any("2.0.0" in msg for msg in logged_messages)

            # Should contain URL status
            assert any("URL configured: Yes" in msg for msg in logged_messages)
            assert any("URL configured: No" in msg for msg in logged_messages)

            # Should contain checksum status
            assert any("Checksum available: Yes" in msg for msg in logged_messages)
            assert any("Checksum available: No" in msg for msg in logged_messages)

    def test_list_pretrained_models_empty_registry(self):
        """Test list_pretrained_models with empty model registry."""
        with (
            patch("scxpand.main.PRETRAINED_MODELS", {}),
            patch("scxpand.main.logger") as mock_logger,
        ):
            list_pretrained_models()

            # Should still show header
            logged_messages = [call.args[0] for call in mock_logger.info.call_args_list]
            assert any("Available pre-trained models:" in msg for msg in logged_messages)
