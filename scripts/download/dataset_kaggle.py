#!/usr/bin/env python3
"""
Download do dataset Software Architecture (Kaggle).

Link da página do dataset (baixar manualmente se o CLI travar):
  https://www.kaggle.com/datasets/carlosrian/software-architecture-dataset

Na página: faça login, clique em "Download" e salve o ZIP. Depois:
  make extract-dataset-kaggle ZIP=/caminho/para/arquivo.zip
  (extrai em notebooks/dataset/kaggle/raw/)

Via CLI: pip install kaggle, credenciais em ~/.kaggle/kaggle.json ou KAGGLE_* em configs/.env.
Dataset ~33 GB. Dados brutos (VOC) em dataset/kaggle/raw/. Rode make convert-voc-to-yolo após o download.

Uso:
  python -m download.dataset_kaggle              # download via Kaggle CLI
  python -m download.dataset_kaggle arquivo.zip  # extrai ZIP baixado manualmente
"""
import os
import subprocess
import sys
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
env_file = PROJECT_ROOT / "configs" / ".env"
if env_file.exists():
    load_dotenv(env_file)

from download import DATASET_KAGGLE_DIR, NOTEBOOKS_DIR

KAGGLE_SLUG = "carlosrian/software-architecture-dataset"
KAGGLE_DATASET_URL = "https://www.kaggle.com/datasets/carlosrian/software-architecture-dataset"


def extract_zip(zip_path: Path, dest_dir: Path) -> bool:
    """Extrai ZIP em dest_dir. Retorna True se ok."""
    if not zip_path.exists() or not zip_path.suffix.lower() == ".zip":
        return False
    dest_dir.mkdir(parents=True, exist_ok=True)
    print("==> Extraindo", zip_path.name, "em", dest_dir)
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(dest_dir)
    print("==> Extração concluída.")
    return True


def main():
    print("==> Dataset Kaggle: Software Architecture Dataset (~33 GB)")
    print("==> Página (download manual):", KAGGLE_DATASET_URL)
    print("==> Destino:", DATASET_KAGGLE_DIR)

    # Se passou um caminho de ZIP, extrair em raw/
    raw_dir = DATASET_KAGGLE_DIR / "raw"
    if len(sys.argv) >= 2:
        zip_path = Path(sys.argv[1]).resolve()
        if zip_path.suffix.lower() == ".zip":
            raw_dir.mkdir(parents=True, exist_ok=True)
            if extract_zip(zip_path, raw_dir):
                print("==> Rode make convert-voc-to-yolo para converter VOC -> YOLO")
                return 0
            return 1
        print("Uso: python -m download.dataset_kaggle [caminho/para/dataset.zip]")
        return 1

    data_yaml = DATASET_KAGGLE_DIR / "data.yaml"
    if data_yaml.exists():
        print("==> Dataset YOLO já existe em", DATASET_KAGGLE_DIR)
        return 0

    # Credenciais: ~/.kaggle/kaggle.json ou env
    has_env = os.environ.get("KAGGLE_USERNAME") or os.environ.get("KAGGLE_KEY")
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    if not has_env and not kaggle_json.exists():
        print("Erro: Configure Kaggle API. Opções:")
        print("  1) Coloque kaggle.json em ~/.kaggle/")
        print("  2) Ou defina KAGGLE_USERNAME e KAGGLE_KEY em configs/.env")
        return 1

    raw_dir.mkdir(parents=True, exist_ok=True)

    print("==> Baixando e extraindo (pode demorar)...")
    try:
        subprocess.run(
            [
                "kaggle", "datasets", "download",
                "-d", KAGGLE_SLUG,
                "-p", str(raw_dir),
                "--unzip",
            ],
            check=True,
        )
        print("==> Concluído em", raw_dir)
        print("==> Rode make convert-voc-to-yolo para converter VOC -> YOLO")
        return 0
    except FileNotFoundError:
        print("Erro: comando 'kaggle' não encontrado. Instale: pip install kaggle")
        return 1
    except subprocess.CalledProcessError as e:
        print("Erro no download Kaggle:", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
