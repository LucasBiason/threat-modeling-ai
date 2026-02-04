#!/usr/bin/env python3
"""
Verifica se o dataset Roboflow está correto (paths, data.yaml, train, imagens/labels).

Uso: python scripts/verify_dataset_roboflow.py
     ou: make verify-dataset-roboflow
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from download import DATASET_ROBOFLOW_DIR
except ImportError:
    DATASET_ROBOFLOW_DIR = PROJECT_ROOT / "notebooks" / "dataset" / "roboflow"


def main():
    errors = []
    if not DATASET_ROBOFLOW_DIR.exists():
        errors.append(f"Diretório não existe: {DATASET_ROBOFLOW_DIR}")
    data_yaml = DATASET_ROBOFLOW_DIR / "data.yaml"
    if not data_yaml.exists():
        errors.append("data.yaml não encontrado")
    train_img = DATASET_ROBOFLOW_DIR / "train" / "images"
    train_lbl = DATASET_ROBOFLOW_DIR / "train" / "labels"
    if not train_img.exists():
        errors.append("train/images/ não existe")
    if not train_lbl.exists():
        errors.append("train/labels/ não existe")

    if errors:
        print("ERROS:", *errors, sep="\n")
        return 1

    imgs = list(train_img.glob("*.jpg")) + list(train_img.glob("*.png"))
    lbls = list(train_lbl.glob("*.txt"))
    print(f"Train: {len(imgs)} imagens, {len(lbls)} labels")
    if len(imgs) == 0:
        errors.append("Nenhuma imagem em train/images")
    if len(imgs) != len(lbls):
        errors.append(f"Imagens ({len(imgs)}) e labels ({len(lbls)}) em quantidade diferente")

    import yaml
    with open(data_yaml) as f:
        cfg = yaml.safe_load(f)
    names = cfg.get("names", [])
    if isinstance(names, dict):
        names = list(names.values()) if names else []
    print(f"Classes no data.yaml: {len(names)}")
    if not names:
        errors.append("Nenhuma classe em data.yaml")

    try:
        from PIL import Image
        import numpy as np
        first_img = imgs[0]
        img = Image.open(first_img).convert("RGB")
        arr = np.array(img)
        print(f"Imagem de teste: {first_img.name}, shape {arr.shape}")
    except ImportError as e:
        print("AVISO: PIL/numpy não disponíveis:", e)
    except Exception as e:
        errors.append(f"Erro ao abrir imagem: {e}")

    if errors:
        print("ERROS:", *errors, sep="\n")
        return 1

    print("\n==> Dataset Roboflow OK. Pronto para uso.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
