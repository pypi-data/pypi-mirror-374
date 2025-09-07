# scXpand



<div align="center">
  <br/>
  <img src="docs/_static/images/scXpand_symbol.jpeg" alt="scXpand Logo" width="300"/>
  <br/>
  <br/>
  <h3>Pan-cancer detection of T-cell clonal expansion from single-cell RNA sequencing without paired single-cell TCR sequencing</h3>
  <br/>
  <p>
    <a href="https://scxpand.readthedocs.io">Documentation</a> •
    <a href="#installation">Installation</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="docs/usage_examples.rst">Usage Examples</a> •
    <a href="docs/data_format.rst">Data Format</a> •
    <a href="docs/output_format.rst">Output Format</a> •
    <a href="#model-architectures">Model Architectures</a> •
    <a href="#citation">Citation</a>
  </p>
</div>

<div style="width: 100vw; margin-left: calc(-50vw + 50%); margin-right: calc(-50vw + 50%); margin-top: 20px; margin-bottom: 40px; padding: 0 40px;">
  <img src="docs/_static/images/scXpand_datasets.jpeg" alt="scXpand Datasets Overview" style="width: 100%; height: auto; display: block; margin: 0; padding: 0;"/>
</div>

A framework for predicting T-cell clonal expansion from single-cell RNA sequencing data.

**Manuscript in preparation** - detailed methodology and benchmarks coming soon.

**[View full documentation](https://scxpand.readthedocs.io)** for comprehensive guides and API reference.


## Features

- **Multiple Model Architectures**: Autoencoder, MLP, LightGBM, Logistic Regression, and SVM for comprehensive analysis
- **Scalable Processing**: Handles millions of cells with memory-efficient data streaming from disk during training
- **Automated Hyperparameter Optimization**: Built-in Optuna integration for model tuning

## Installation

```bash
pip install scxpand
```

## Quick Start

```python
import scxpand

# List available pre-trained models
scxpand.list_pretrained_models()

# Run inference with automatic model download
results = scxpand.run_inference_with_pretrained(
    model_name="autoencoder_pan_cancer",
    data_path="your_data.h5ad"
)
```

Or via command line:

```bash
# Pre-trained model inference (curated models)
scxpand predict --data_path your_data.h5ad --model_name autoencoder_pan_cancer

# Direct DOI inference (any Zenodo model - seamless sharing!)
scxpand predict --data_path your_data.h5ad --model_doi 10.5281/zenodo.1234567

# Local model inference
scxpand predict --data_path your_data.h5ad --model_path results/my_model
```

## Development

For development installation and model training, see the [documentation](https://scxpand.readthedocs.io/en/latest/installation.html).

## Model Architectures

scXpand provides multiple model architectures to suit different use cases and data characteristics:

#### Autoencoder-based Classifiers

Architecture featuring an encoder with auxiliary decoder for reconstruction and classifier head for expansion prediction. This approach leverages representation learning to capture complex patterns in single-cell data.

#### Multi-Layer Perceptron (MLP)

Standard feed-forward neural networks for direct expansion prediction.

#### LightGBM

Gradient boosting for classification tasks with excellent performance on tabular data.

#### Linear Models

Classical machine learning approaches including logistic regression and support vector machines.

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

## Citation

If you use scXpand in your research, please cite:

```bibtex
@article{scxpand2024,
  title={scXpand: Pan-cancer detection of T-cell clonal expansion from single-cell RNA sequencing without paired single-cell TCR sequencing},
  author={[Your Name]},
  journal={[Journal Name]},
  year={2024},
  doi={[DOI]}
}
```

This project was created in favor of the scientific community worldwide, with a special dedication to the cancer research community.
We hope you’ll find this repository helpful, and we warmly welcome any requests or suggestions - please don’t hesitate to reach out!

<p align="center">
  <a href="https://mapmyvisitors.com/web/1byyd">
     <img src="https://mapmyvisitors.com/map.png?d=yRhTNMKyBcxvPwQsz-rFDDwHhMjSeVYRSYtxm4oUNdY&cl=ffffff">
   </a>
</p>
<p align="center">
  <a href="#">
     <img src="https://visitor-badge.laobi.icu/badge?page_id=ronamit.scxpand&left_text=scXpand%20Visitors" alt="Visitors" />
   </a>
</p>
