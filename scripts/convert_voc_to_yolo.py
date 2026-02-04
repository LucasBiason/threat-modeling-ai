#!/usr/bin/env python3
"""
Converte dataset Pascal VOC (PNG + XML) para formato YOLO (images + labels .txt).

Estrutura esperada:
  dataset/kaggle/raw/  <- dados brutos VOC (PNG + XML)
  dataset/kaggle/      <- saída YOLO (train/, valid/, data.yaml)

Uso: python scripts/convert_voc_to_yolo.py [pasta_voc] [pasta_destino]
  ou: python scripts/convert_voc_to_yolo.py
      (usa notebooks/dataset/kaggle/raw -> notebooks/dataset/kaggle)
"""
import xml.etree.ElementTree as ET
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
KAGGLE_DIR = NOTEBOOKS_DIR / "dataset" / "kaggle"
DEFAULT_VOC = KAGGLE_DIR / "raw"
DEFAULT_DEST = KAGGLE_DIR


def parse_voc_xml(xml_path: Path) -> tuple[list[tuple], int, int]:
    """Retorna ([(class_name, xmin, ymin, xmax, ymax), ...], width, height)."""
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


def voc_to_yolo_bbox(xmin: float, ymin: float, xmax: float, ymax: float, w: int, h: int) -> tuple:
    """Converte bbox VOC (absoluto) para YOLO (normalizado centro, largura, altura)."""
    xc = (xmin + xmax) / 2 / w
    yc = (ymin + ymax) / 2 / h
    bw = (xmax - xmin) / w
    bh = (ymax - ymin) / h
    return (xc, yc, bw, bh)


def convert(voc_dir: Path, dest_dir: Path) -> bool:
    """Converte pasta VOC para YOLO. Retorna True se ok."""
    voc_dir = voc_dir.resolve()
    dest_dir = dest_dir.resolve()
    if not voc_dir.exists():
        print(f"Erro: pasta VOC não existe: {voc_dir}")
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
        print(f"Erro: nenhuma imagem .png/.jpg em {voc_dir}")
        return False

    classes_seen: set[str] = set()
    for img_path in png_files:
        xml_path = img_path.with_suffix(".xml")
        if xml_path.exists():
            objs, _, _ = parse_voc_xml(xml_path)
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

    import random
    png_files = sorted(png_files)
    random.seed(42)
    random.shuffle(png_files)
    n_val = max(1, int(len(png_files) * 0.15))
    valid_files = png_files[:n_val]
    train_files = png_files[n_val:]

    def process_split(files: list, img_dir: Path, lbl_dir: Path) -> None:
        import shutil
        for img_path in files:
            xml_path = img_path.with_suffix(".xml")
            if not xml_path.exists():
                continue
            objs, w, h = parse_voc_xml(xml_path)
            if not objs:
                continue
            dest_img = img_dir / img_path.name
            dest_lbl = lbl_dir / (img_path.stem + ".txt")
            try:
                shutil.copy2(img_path, dest_img)
            except Exception as e:
                print(f"  Aviso: não copiou {img_path.name}: {e}")
                continue
            lines = []
            for cls_name, xmin, ymin, xmax, ymax in objs:
                cls_idx = class_to_idx.get(cls_name, 0)
                xc, yc, bw, bh = voc_to_yolo_bbox(xmin, ymin, xmax, ymax, w, h)
                lines.append(f"{cls_idx} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n")
            with open(dest_lbl, "w") as f:
                f.writelines(lines)

    process_split(train_files, train_img, train_lbl)
    process_split(valid_files, valid_img, valid_lbl)
    nc = len(class_names)
    if nc == 0:
        print("Erro: nenhuma classe encontrada nos XMLs")
        return False
    data_yaml = dest_dir / "data.yaml"
    with open(data_yaml, "w") as f:
        f.write(f"path: {dest_dir}\n")
        f.write("train: train/images\n")
        f.write("val: valid/images\n")
        f.write(f"nc: {nc}\n")
        f.write(f"names: {class_names}\n")

    print(f"OK Convertido: {len(train_files)} train, {len(valid_files)} valid")
    print(f"   Classes: {nc} -> {class_names[:10]}{'...' if len(class_names) > 10 else ''}")
    print(f"   data.yaml: {data_yaml}")
    return True


def main() -> int:
    voc_dir = Path(sys.argv[1]) if len(sys.argv) >= 2 else DEFAULT_VOC
    dest_dir = Path(sys.argv[2]) if len(sys.argv) >= 3 else DEFAULT_DEST
    if convert(voc_dir, dest_dir):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
