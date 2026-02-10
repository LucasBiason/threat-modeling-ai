"""
Scripts para experimentos do Threat Modeling AI.

Módulos: download, train (treinamento YOLO).
"""

# Re-exporta paths do módulo train para compatibilidade
from notebooks.scripts.train.paths import (
    DATASET_DIR,
    DATASET_KAGGLE_DIR,
    DATASET_ROBOFLOW_DIR,
    MODELS_DIR,
    MODELS_KAGGLE_DIR,
    MODELS_ROBOFLOW_DIR,
    NOTEBOOKS_DIR,
    OUTPUTS_DIR,
    OUTPUTS_KAGGLE_DIR,
    OUTPUTS_ROBOFLOW_DIR,
    PROJECT_ROOT,
)

__all__ = [
    "PROJECT_ROOT",
    "NOTEBOOKS_DIR",
    "DATASET_DIR",
    "OUTPUTS_DIR",
    "MODELS_DIR",
    "DATASET_ROBOFLOW_DIR",
    "DATASET_KAGGLE_DIR",
    "OUTPUTS_ROBOFLOW_DIR",
    "OUTPUTS_KAGGLE_DIR",
    "MODELS_ROBOFLOW_DIR",
    "MODELS_KAGGLE_DIR",
]
