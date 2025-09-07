from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from sklearn.metrics import auc, roc_curve

from scxpand.util.general_util import to_np
from scxpand.util.logger import get_logger


logger = get_logger()
# Global plotting configuration
plt.rcParams.update(
    {
        "font.size": 14,
        "axes.labelsize": 14,
        "axes.titlesize": 16,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "legend.fontsize": 12,
        "lines.linewidth": 2.5,
        "figure.titlesize": 16,
        "figure.figsize": (10, 8),
    }
)


def plot_roc_curve(
    labels,
    probs_pred,
    show_plot: bool = False,
    plot_save_dir: Path | None = None,
    plot_name: str = "roc_curve",
    title: str = "Receiver Operating Characteristic (ROC) Curve",
) -> float:
    """Plot ROC curve for binary classification and calculate AUROC.

    Creates a publication-ready ROC curve plot showing model performance
    across all classification thresholds. Optionally saves the plot to disk.

    Args:
        labels: True binary labels (0 or 1).
        probs_pred: Predicted probabilities [0-1] from model.
        show_plot: Whether to display plot interactively.
        plot_save_dir: Directory to save plot. If None, plot is not saved.
        plot_name: Filename for saved plot (without extension).
        title: Plot title text.

    Returns:
        AUROC score (Area Under the ROC Curve).


    """
    probs_pred = to_np(probs_pred).astype(float)
    labels = to_np(labels).astype(int)

    if labels.sum() == 0 or labels.sum() == len(labels):
        logger.info(f"No positive labels found for {plot_name}. Returning NaN and skipping plot.")
        return np.nan

    fpr, tpr, _ = roc_curve(y_true=labels, y_score=probs_pred)
    auroc = auc(fpr, tpr)

    if plot_save_dir or show_plot:
        plt.figure(figsize=(6, 6))
        plt.plot(fpr, tpr, color="darkorange", lw=2, label=f"AUC = {auroc:.2f}")
        plt.plot([0, 1], [0, 1], color="navy", lw=2, linestyle="--")
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.0])
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title(title)
        plt.legend(loc="lower right")
        if plot_save_dir:
            save_path = Path(plot_save_dir) / f"{plot_name}.png"
            save_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path)
        if show_plot:
            plt.show()
        plt.close("all")

    return auroc
