#!/usr/bin/env python3
"""
Prepara a base Roboflow: download, extracao e verificacao em um unico comando.

Requer ROBOFLOW_API_KEY em configs/.env ou no ambiente.
Destino: notebooks/dataset/roboflow/ (formato YOLO).

Uso: python -m notebooks.scripts.download.prepare_roboflow
     ou: make download-roboflow
"""

import os
import shutil
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))
from notebooks.scripts.train import paths  # noqa: E402

DATASET_ROBOFLOW_DIR = paths.DATASET_ROBOFLOW_DIR
PROJECT_ROOT = paths.PROJECT_ROOT

# Carregar configs/.env se existir (notebooks/lab)
_env = PROJECT_ROOT / "configs" / ".env"
if _env.exists():
    from dotenv import load_dotenv

    load_dotenv(_env)

DOWNLOAD_TMP = paths.NOTEBOOKS_DIR / "dataset_tmp"
ROBOFLOW_WORKSPACE = "yago-ja7nb"
ROBOFLOW_PROJECT = "aws-and-azure-system-diagrams"


def _verify() -> int:
    """Verifica integridade do dataset Roboflow."""
    errors = []
    if not DATASET_ROBOFLOW_DIR.exists():
        errors.append(f"Diretorio nao existe: {DATASET_ROBOFLOW_DIR}")
    data_yaml = DATASET_ROBOFLOW_DIR / "data.yaml"
    if not data_yaml.exists():
        errors.append("data.yaml nao encontrado")
    train_img = DATASET_ROBOFLOW_DIR / "train" / "images"
    train_lbl = DATASET_ROBOFLOW_DIR / "train" / "labels"
    if not train_img.exists():
        errors.append("train/images/ nao existe")
    if not train_lbl.exists():
        errors.append("train/labels/ nao existe")
    if errors:
        print("ERROS:", *errors, sep="\n")
        return 1
    imgs = list(train_img.glob("*.jpg")) + list(train_img.glob("*.png"))
    lbls = list(train_lbl.glob("*.txt"))
    print(f"Train: {len(imgs)} imagens, {len(lbls)} labels")
    if len(imgs) == 0:
        errors.append("Nenhuma imagem em train/images")
    if len(imgs) != len(lbls):
        errors.append(
            f"Imagens ({len(imgs)}) e labels ({len(lbls)}) em quantidade diferente"
        )
    if errors:
        print("ERROS:", *errors, sep="\n")
        return 1
    import yaml

    with open(data_yaml) as f:
        cfg = yaml.safe_load(f)
    names = cfg.get("names", [])
    if isinstance(names, dict):
        names = list(names.values()) if names else []
    print(f"Classes no data.yaml: {len(names)}")
    if not names:
        errors.append("Nenhuma classe em data.yaml")
    if errors:
        print("ERROS:", *errors, sep="\n")
        return 1
    print("Dataset Roboflow OK. Pronto para uso.")
    return 0


def _download() -> int:
    """Download do dataset em formato YOLOv8."""
    if (DATASET_ROBOFLOW_DIR / "data.yaml").exists() and (
        DATASET_ROBOFLOW_DIR / "train"
    ).exists():
        print("Dataset ja presente em", DATASET_ROBOFLOW_DIR)
        return 0
    api_key = os.environ.get("ROBOFLOW_API_KEY", "").strip()
    if not api_key:
        print(
            "Erro: ROBOFLOW_API_KEY nao definido. Defina em configs/.env ou no ambiente."
        )
        return 1
    if DOWNLOAD_TMP.exists():
        shutil.rmtree(DOWNLOAD_TMP)
    DATASET_ROBOFLOW_DIR.parent.mkdir(parents=True, exist_ok=True)
    DATASET_ROBOFLOW_DIR.mkdir(parents=True, exist_ok=True)
    for name in ("images", "labels"):
        path = DATASET_ROBOFLOW_DIR / name
        if path.exists() and path.is_dir():
            shutil.rmtree(path)
    print("Baixando em formato YOLOv8...")
    from roboflow import Roboflow

    rf = Roboflow(api_key=api_key)
    project = rf.workspace(ROBOFLOW_WORKSPACE).project(ROBOFLOW_PROJECT)
    project.version(1).download("yolov8", location=str(DOWNLOAD_TMP))
    for item in DOWNLOAD_TMP.iterdir():
        dest = DATASET_ROBOFLOW_DIR / item.name
        if dest.exists():
            shutil.rmtree(dest) if dest.is_dir() else dest.unlink()
        shutil.move(str(item), str(DATASET_ROBOFLOW_DIR))
    DOWNLOAD_TMP.rmdir()
    print("Download concluido em", DATASET_ROBOFLOW_DIR)
    return 0


def main() -> int:
    print("==> Dataset: AWS and Azure System Diagrams (Roboflow)")
    print("==> Destino:", DATASET_ROBOFLOW_DIR)
    if _download() != 0:
        return 1
    return _verify()


if __name__ == "__main__":
    sys.exit(main())
