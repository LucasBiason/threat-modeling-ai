"""Paths centralizados para experimentos."""

from pathlib import Path

# Raiz do projeto (train/paths.py -> p=train, p.p=scripts, p.p.p=notebooks, p.p.p.p=raiz)
_here = Path(__file__).resolve().parent
PROJECT_ROOT = _here.parent.parent.parent
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# Estrutura padronizada (dataset, outputs e models em notebooks/)
DATASET_DIR = NOTEBOOKS_DIR / "dataset"
OUTPUTS_DIR = NOTEBOOKS_DIR / "outputs"
MODELS_DIR = NOTEBOOKS_DIR / "models"

# Por fonte
DATASET_ROBOFLOW_DIR = DATASET_DIR / "roboflow"
DATASET_KAGGLE_DIR = DATASET_DIR / "kaggle"
OUTPUTS_ROBOFLOW_DIR = OUTPUTS_DIR / "roboflow"
OUTPUTS_KAGGLE_DIR = OUTPUTS_DIR / "kaggle"
MODELS_ROBOFLOW_DIR = MODELS_DIR / "roboflow"
MODELS_KAGGLE_DIR = MODELS_DIR / "kaggle"
