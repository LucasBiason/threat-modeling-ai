#!/usr/bin/env python3
"""
Download do dataset AWS and Azure System Diagrams (Roboflow).

Requer ROBOFLOW_API_KEY em configs/.env ou no ambiente.
Salva em notebooks/dataset/roboflow/ (formato YOLOv8).

Uso:
  python -m download.dataset_roboflow
"""
import os
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from download import DATASET_ROBOFLOW_DIR

# Carregar configs/.env antes de usar roboflow
from dotenv import load_dotenv
env_file = PROJECT_ROOT / "configs" / ".env"
if env_file.exists():
    load_dotenv(env_file)
else:
    print("Aviso: configs/.env não encontrado. Use ROBOFLOW_API_KEY no ambiente.")

ROBOFLOW_WORKSPACE = "yago-ja7nb"
ROBOFLOW_PROJECT = "aws-and-azure-system-diagrams"
DOWNLOAD_TMP = PROJECT_ROOT / "dataset_tmp"


def dataset_ja_baixado():
    return (DATASET_ROBOFLOW_DIR / "data.yaml").exists() and (DATASET_ROBOFLOW_DIR / "train").exists()


def remover_placeholders_dataset():
    for name in ("images", "labels"):
        path = DATASET_ROBOFLOW_DIR / name
        if path.exists() and path.is_dir():
            shutil.rmtree(path)
            print("==> Removido placeholder", path)


def mover_tmp_para_dataset():
    if not DOWNLOAD_TMP.exists():
        return
    remover_placeholders_dataset()
    for item in DOWNLOAD_TMP.iterdir():
        dest = DATASET_ROBOFLOW_DIR / item.name
        if dest.exists():
            if dest.is_dir():
                shutil.rmtree(dest)
            else:
                dest.unlink()
        shutil.move(str(item), str(DATASET_ROBOFLOW_DIR))
    DOWNLOAD_TMP.rmdir()
    print("==> Conteúdo em", DATASET_ROBOFLOW_DIR)


def main():
    print("==> Dataset: AWS and Azure System Diagrams (Roboflow)")
    print("==> Destino:", DATASET_ROBOFLOW_DIR)

    if dataset_ja_baixado():
        print("==> Dataset já presente em", DATASET_ROBOFLOW_DIR)
        return 0

    api_key = os.environ.get("ROBOFLOW_API_KEY", "").strip()
    if not api_key:
        print("Erro: ROBOFLOW_API_KEY não definido. Defina em configs/.env ou no ambiente.")
        return 1

    if DOWNLOAD_TMP.exists():
        shutil.rmtree(DOWNLOAD_TMP)
    DATASET_ROBOFLOW_DIR.parent.mkdir(parents=True, exist_ok=True)
    DATASET_ROBOFLOW_DIR.mkdir(parents=True, exist_ok=True)

    print("==> Baixando em formato YOLOv8...")
    from roboflow import Roboflow

    rf = Roboflow(api_key=api_key)
    project = rf.workspace(ROBOFLOW_WORKSPACE).project(ROBOFLOW_PROJECT)
    project.version(1).download("yolov8", location=str(DOWNLOAD_TMP))

    mover_tmp_para_dataset()
    print("==> Download concluído em", DATASET_ROBOFLOW_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
