#!/usr/bin/env python3
"""
Verificação de integridade e testes no dataset Kaggle (Software Architecture Dataset).

Uso: python3 scripts/verify_dataset_kaggle.py
- Localiza data.yaml em dataset/kaggle
- Verifica estrutura train/valid (images + labels)
- Testa leitura de amostra de imagens e labels
- Opcional: teste de carregamento YOLO (ultralytics)
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
DATASET_KAGGLE_DIR = NOTEBOOKS_DIR / "dataset" / "kaggle"


def find_data_yaml(base: Path) -> Path | None:
    """Retorna o diretório que contém data.yaml (raiz ou primeira subpasta)."""
    if (base / "data.yaml").exists():
        return base
    for sub in sorted(base.iterdir()):
        if sub.is_dir() and (sub / "data.yaml").exists():
            return sub
        if sub.is_dir():
            for sub2 in sorted(sub.iterdir()):
                if sub2.is_dir() and (sub2 / "data.yaml").exists():
                    return sub2
    return None


def main() -> int:
    print("==> Verificação do dataset Kaggle (notebooks/dataset/kaggle)")
    print("=" * 60)

    if not DATASET_KAGGLE_DIR.exists():
        print("ERRO: Diretório não existe:", DATASET_KAGGLE_DIR)
        print("Execute: make download-dataset-kaggle ou make convert-voc-to-yolo (se VOC em raw/)")
        return 1

    data_root = find_data_yaml(DATASET_KAGGLE_DIR)
    if not data_root:
        print("ERRO: data.yaml não encontrado em", DATASET_KAGGLE_DIR)
        print("Dataset incompleto ou download ainda em andamento.")
        return 1

    print("OK data.yaml em:", data_root)

    # Estrutura YOLO esperada
    train_images = data_root / "train" / "images"
    train_labels = data_root / "train" / "labels"
    valid_images = data_root / "valid" / "images"
    valid_labels = data_root / "valid" / "labels"
    # Alguns datasets usam "val" em vez de "valid"
    if not valid_images.exists():
        valid_images = data_root / "val" / "images"
        valid_labels = data_root / "val" / "labels"

    errors = []
    if not train_images.exists():
        errors.append(f"train/images não existe: {train_images}")
    if not train_labels.exists():
        errors.append(f"train/labels não existe: {train_labels}")

    if errors:
        for e in errors:
            print("ERRO:", e)
        return 1

    n_train_img = len(list(train_images.glob("*.*"))) if train_images.exists() else 0
    n_train_lbl = len(list(train_labels.glob("*.txt"))) if train_labels.exists() else 0
    n_valid_img = len(list(valid_images.glob("*.*"))) if valid_images.exists() else 0
    n_valid_lbl = len(list(valid_labels.glob("*.txt"))) if valid_labels.exists() else 0

    print("OK train/images:", n_train_img, "| train/labels:", n_train_lbl)
    if valid_images.exists():
        print("OK valid/images:", n_valid_img, "| valid/labels:", n_valid_lbl)

    # Ler data.yaml
    import yaml
    yaml_path = data_root / "data.yaml"
    with open(yaml_path) as f:
        cfg = yaml.safe_load(f)
    nc = cfg.get("nc") or cfg.get("names", [])
    if isinstance(nc, list):
        nc = len(nc)
    names = cfg.get("names", [])
    print("OK classes (nc):", nc, "| names:", names[:5] if len(names) > 5 else names)

    # Teste de leitura de imagens (amostra)
    images_list = list(train_images.glob("*.jpg"))[:5] or list(train_images.glob("*.png"))[:5]
    if images_list:
        opened = False
        try:
            from PIL import Image
            for img_path in images_list:
                try:
                    im = Image.open(img_path)
                    im.verify()
                except Exception as e:
                    errors.append(f"Imagem inválida {img_path.name}: {e}")
            if not any("Imagem" in e for e in errors):
                print("OK amostra de imagens (PIL):", len(images_list), "arquivos")
                opened = True
        except ImportError:
            pass
        if not opened:
            try:
                import cv2
                for img_path in images_list:
                    im = cv2.imread(str(img_path))
                    if im is None:
                        errors.append(f"cv2 não leu: {img_path.name}")
                if not any("cv2" in e for e in errors):
                    print("OK amostra de imagens (cv2):", len(images_list), "arquivos")
            except ImportError:
                print("AVISO: PIL e cv2 não disponíveis; pulando teste de abertura de imagens.")

    # Amostra de labels (formato YOLO: classe x_center y_center w h normalizados)
    label_files = list(train_labels.glob("*.txt"))[:5]
    for lbl_path in label_files:
        try:
            with open(lbl_path) as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        cls, x, y, w, h = parts[0], parts[1], parts[2], parts[3], parts[4]
                        for v in (float(x), float(y), float(w), float(h)):
                            if not (0 <= v <= 1):
                                errors.append(f"Label fora de [0,1]: {lbl_path.name} -> {v}")
        except Exception as e:
            errors.append(f"Label {lbl_path.name}: {e}")
    if not any("Label" in e for e in errors):
        print("OK amostra de labels (formato YOLO):", len(label_files), "arquivos")

    if errors:
        for e in errors:
            print("ERRO:", e)
        return 1

    # Teste opcional: carregar dataset com Ultralytics
    try:
        from ultralytics.data.utils import check_det_dataset
        from ultralytics.utils import LOGGER
        # check_det_dataset espera o path do yaml
        data_yaml = str(yaml_path)
        check_det_dataset(data_yaml)
        print("OK Ultralytics: dataset válido para YOLO.")
    except ImportError:
        print("AVISO: ultralytics não instalado; teste YOLO omitido.")
    except Exception as e:
        print("AVISO: Ultralytics check_det_dataset:", e)

    print("=" * 60)
    print("==> Integridade e testes concluídos com sucesso.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
