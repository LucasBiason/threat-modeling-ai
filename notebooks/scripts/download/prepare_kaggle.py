#!/usr/bin/env python3
"""
Prepara a base Kaggle: download (ou extração de ZIP), conversao VOC->YOLO e verificacao.

Requer kaggle CLI (credenciais em ~/.kaggle/kaggle.json) ou passe o caminho do ZIP.
Destino: notebooks/dataset/kaggle/. Um unico comando faz tudo.

Uso: python -m notebooks.scripts.download.prepare_kaggle
     python -m notebooks.scripts.download.prepare_kaggle /caminho/para/dataset.zip
     ou: make download-kaggle
"""

import os
import random
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))
from notebooks.scripts.train import paths  # noqa: E402

DATASET_KAGGLE_DIR = paths.DATASET_KAGGLE_DIR
PROJECT_ROOT = paths.PROJECT_ROOT

_env = PROJECT_ROOT / "configs" / ".env"
if _env.exists():
    from dotenv import load_dotenv

    load_dotenv(_env)

KAGGLE_SLUG = "carlosrian/software-architecture-dataset"
RAW_DIR = DATASET_KAGGLE_DIR / "raw"


def _parse_voc_xml(xml_path: Path) -> tuple[list[tuple], int, int]:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    size = root.find("size")
    w = int(size.find("width").text) if size is not None else 1
    h = int(size.find("height").text) if size is not None else 1
    objs = []
    for obj in root.findall("object"):
        name = obj.find("name")
        bnd = obj.find("bndbox")
        if name is not None and bnd is not None:
            xmin = float(bnd.find("xmin").text)
            ymin = float(bnd.find("ymin").text)
            xmax = float(bnd.find("xmax").text)
            ymax = float(bnd.find("ymax").text)
            objs.append((name.text, xmin, ymin, xmax, ymax))
    return objs, w, h


def _voc_to_yolo_bbox(
    xmin: float, ymin: float, xmax: float, ymax: float, w: int, h: int
) -> tuple:
    xc = (xmin + xmax) / 2 / w
    yc = (ymin + ymax) / 2 / h
    bw = (xmax - xmin) / w
    bh = (ymax - ymin) / h
    return (xc, yc, bw, bh)


def _convert_voc_to_yolo(voc_dir: Path, dest_dir: Path) -> bool:
    voc_dir = voc_dir.resolve()
    dest_dir = dest_dir.resolve()
    data_yaml = dest_dir / "data.yaml"
    train_img = dest_dir / "train" / "images"
    if (
        data_yaml.exists()
        and train_img.exists()
        and len(list(train_img.glob("*.*"))) > 0
    ):
        print("Dataset YOLO ja existe em", dest_dir)
        return True
    if not voc_dir.exists():
        print("Erro: pasta VOC nao existe:", voc_dir)
        return False
    png_files = list(voc_dir.glob("*.png")) + list(voc_dir.glob("*.jpg"))
    if not png_files:
        for sub in voc_dir.iterdir():
            if sub.is_dir():
                png_files = list(sub.glob("*.png")) + list(sub.glob("*.jpg"))
                if png_files:
                    voc_dir = sub
                    break
    if not png_files:
        print("Erro: nenhuma imagem .png/.jpg em", voc_dir)
        return False
    classes_seen: set[str] = set()
    for img_path in png_files:
        xml_path = img_path.with_suffix(".xml")
        if xml_path.exists():
            objs, _, _ = _parse_voc_xml(xml_path)
            for cls_name, *_ in objs:
                classes_seen.add(cls_name)
    class_names = sorted(classes_seen)
    class_to_idx = {c: i for i, c in enumerate(class_names)}
    train_img = dest_dir / "train" / "images"
    train_lbl = dest_dir / "train" / "labels"
    valid_img = dest_dir / "valid" / "images"
    valid_lbl = dest_dir / "valid" / "labels"
    for d in [train_img, train_lbl, valid_img, valid_lbl]:
        d.mkdir(parents=True, exist_ok=True)
    png_files = sorted(png_files)
    random.seed(42)
    random.shuffle(png_files)
    n_val = max(1, int(len(png_files) * 0.15))
    valid_files = png_files[:n_val]
    train_files = png_files[n_val:]

    def process_split(files: list, img_dir: Path, lbl_dir: Path) -> None:
        for img_path in files:
            xml_path = img_path.with_suffix(".xml")
            if not xml_path.exists():
                continue
            objs, w, h = _parse_voc_xml(xml_path)
            if not objs:
                continue
            dest_img = img_dir / img_path.name
            dest_lbl = lbl_dir / (img_path.stem + ".txt")
            try:
                shutil.copy2(img_path, dest_img)
            except Exception as e:
                print("  Aviso: nao copiou", img_path.name, e)
                continue
            lines = []
            for cls_name, xmin, ymin, xmax, ymax in objs:
                cls_idx = class_to_idx.get(cls_name, 0)
                xc, yc, bw, bh = _voc_to_yolo_bbox(xmin, ymin, xmax, ymax, w, h)
                lines.append(f"{cls_idx} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n")
            with open(dest_lbl, "w") as f:
                f.writelines(lines)

    process_split(train_files, train_img, train_lbl)
    process_split(valid_files, valid_img, valid_lbl)
    nc = len(class_names)
    if nc == 0:
        print("Erro: nenhuma classe encontrada nos XMLs")
        return False
    with open(data_yaml, "w") as f:
        f.write(f"path: {dest_dir}\n")
        f.write("train: train/images\n")
        f.write("val: valid/images\n")
        f.write(f"nc: {nc}\n")
        f.write(f"names: {class_names}\n")
    print(
        "Convertido:",
        len(train_files),
        "train,",
        len(valid_files),
        "valid. Classes:",
        nc,
    )
    return True


def _find_data_yaml(base: Path) -> Path | None:
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


def _verify() -> int:
    if not DATASET_KAGGLE_DIR.exists():
        print("ERRO: Diretorio nao existe:", DATASET_KAGGLE_DIR)
        return 1
    data_root = _find_data_yaml(DATASET_KAGGLE_DIR)
    if not data_root:
        print("ERRO: data.yaml nao encontrado em", DATASET_KAGGLE_DIR)
        return 1
    train_images = data_root / "train" / "images"
    train_labels = data_root / "train" / "labels"
    if not train_images.exists() or not train_labels.exists():
        print("ERRO: train/images ou train/labels nao existem")
        return 1
    n_img = len(list(train_images.glob("*.*")))
    n_lbl = len(list(train_labels.glob("*.txt")))
    print("Train:", n_img, "imagens,", n_lbl, "labels")
    if n_img == 0 or n_img != n_lbl:
        print("ERRO: quantidade de imagens e labels inconsistente")
        return 1
    print("Dataset Kaggle OK. Pronto para uso.")
    return 0


def _download_or_extract() -> int:
    if len(sys.argv) >= 2:
        zip_path = Path(sys.argv[1]).resolve()
        if zip_path.suffix.lower() == ".zip" and zip_path.exists():
            RAW_DIR.mkdir(parents=True, exist_ok=True)
            print("Extraindo", zip_path.name)
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(RAW_DIR)
            print("Extracao concluida.")
            return 0
        print(
            "Uso: python -m notebooks.scripts.download.prepare_kaggle [caminho/para/dataset.zip]"
        )
        return 1
    if (DATASET_KAGGLE_DIR / "data.yaml").exists():
        print("Dataset YOLO ja existe em", DATASET_KAGGLE_DIR)
        return 0
    has_env = os.environ.get("KAGGLE_USERNAME") or os.environ.get("KAGGLE_KEY")
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    if not has_env and not kaggle_json.exists():
        print(
            "Erro: Configure Kaggle API (kaggle.json em ~/.kaggle/ ou KAGGLE_USERNAME/KAGGLE_KEY)"
        )
        return 1
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print("Baixando e extraindo (pode demorar)...")
    try:
        subprocess.run(
            [
                "kaggle",
                "datasets",
                "download",
                "-d",
                KAGGLE_SLUG,
                "-p",
                str(RAW_DIR),
                "--unzip",
            ],
            check=True,
        )
        print("Download concluido em", RAW_DIR)
    except FileNotFoundError:
        print("Erro: comando 'kaggle' nao encontrado. Instale: pip install kaggle")
        return 1
    except subprocess.CalledProcessError as e:
        print("Erro no download Kaggle:", e)
        return 1
    return 0


def main() -> int:
    print("==> Dataset Kaggle: Software Architecture Dataset")
    print("==> Destino:", DATASET_KAGGLE_DIR)
    if _download_or_extract() != 0:
        return 1
    if not _find_data_yaml(DATASET_KAGGLE_DIR):
        if not _convert_voc_to_yolo(RAW_DIR, DATASET_KAGGLE_DIR):
            return 1
    return _verify()


if __name__ == "__main__":
    sys.exit(main())
