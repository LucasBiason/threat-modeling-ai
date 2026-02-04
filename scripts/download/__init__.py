"""
Módulo de download de datasets do Threat Modeling AI.

Scripts:
  - dataset_roboflow: AWS/Azure System Diagrams (Roboflow). Requer ROBOFLOW_API_KEY.
  - dataset_kaggle:   Software Architecture Dataset (Kaggle, ~33 GB). Requer kaggle CLI.
"""

from pathlib import Path

# Corrigido: parent.parent.parent vai de download/ -> scripts/ -> raiz do projeto
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
DATASET_ROBOFLOW_DIR = NOTEBOOKS_DIR / "dataset" / "roboflow"
DATASET_KAGGLE_DIR = NOTEBOOKS_DIR / "dataset" / "kaggle"
