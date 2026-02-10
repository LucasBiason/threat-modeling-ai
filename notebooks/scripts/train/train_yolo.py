#!/usr/bin/env python3
"""
Treina YOLO fora do Jupyter. Saida em notebooks/outputs/{roboflow|kaggle}/.
Os notebooks usam best.pt onde ele e gerado (outputs/{fonte}/weights/best.pt).

Uso:
  python -m notebooks.scripts.train.train_yolo --dataset roboflow
  python -m notebooks.scripts.train.train_yolo --dataset kaggle --epochs 200
"""
import argparse

import torch
from ultralytics import YOLO

from notebooks.scripts.train import paths


def train_yolo(dataset_type: str, epochs: int = 200, imgsz: int = 416, batch: int = 2, device: str | None = None):
    if dataset_type == "roboflow":
        data_yaml = paths.DATASET_ROBOFLOW_DIR / "data.yaml"
        out_dir = paths.OUTPUTS_ROBOFLOW_DIR
    elif dataset_type == "kaggle":
        data_yaml = paths.DATASET_KAGGLE_DIR / "data.yaml"
        out_dir = paths.OUTPUTS_KAGGLE_DIR
    else:
        raise ValueError("dataset_type deve ser 'roboflow' ou 'kaggle'")

    if not data_yaml.exists():
        print(f"Erro: data.yaml nao encontrado em {data_yaml}")
        return

    if device is None:
        device = "0" if torch.cuda.is_available() else "cpu"

    print(f"Device: {device} | Dataset: {dataset_type} | Config: {data_yaml}")

    model_path = paths.MODELS_DIR / "yolo11n.pt"
    model = YOLO(str(model_path) if model_path.exists() else "yolo11n.pt")

    model.train(
        data=str(data_yaml),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        name=dataset_type,
        device=device,
        project=str(paths.OUTPUTS_DIR),
        exist_ok=True,
    )

    print(f"Treino concluido. Saida em {out_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Treina YOLO (Roboflow ou Kaggle)")
    parser.add_argument("--dataset", type=str, default="roboflow", choices=["roboflow", "kaggle"])
    parser.add_argument("--epochs", type=int, default=200)
    parser.add_argument("--imgsz", type=int, default=416)
    parser.add_argument("--batch", type=int, default=2)
    parser.add_argument("--device", type=str, default=None)
    args = parser.parse_args()
    train_yolo(
        dataset_type=args.dataset,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
    )
