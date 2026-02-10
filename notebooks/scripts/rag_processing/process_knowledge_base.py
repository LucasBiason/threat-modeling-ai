#!/usr/bin/env python3
"""
Processa a base de conhecimento RAG: input_files → output_files → threat-analyzer/app/rag_data.

Converte PDF, DOCX, imagens etc. para Markdown usando Docling.
Arquivos .md são copiados diretamente. Saída em output_files/stride e output_files/dread.
Em seguida, copia output_files para threat-analyzer/app/rag_data (consumido pelo analyzer).

Requer: make setup-notebooks (docling já está em notebooks/requirements.txt)

Uso:
  python -m notebooks.scripts.rag_processing.process_knowledge_base
  ou: make process-rag-kb
"""

import shutil
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Paths
KB_DIR = _PROJECT_ROOT / "notebooks" / "knowledge-base"
INPUT_STRIDE = KB_DIR / "input_files" / "stride"
INPUT_DREAD = KB_DIR / "input_files" / "dread"
OUTPUT_STRIDE = KB_DIR / "output_files" / "stride"
OUTPUT_DREAD = KB_DIR / "output_files" / "dread"
# Destino no threat-analyzer (app/rag_data; conteúdo não versionado, pasta sim via .gitkeep)
RAG_DATA_DIR = _PROJECT_ROOT / "threat-analyzer" / "app" / "rag_data"

DOCLING_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".pptx",
    ".xlsx",
    ".html",
    ".htm",
    ".png",
    ".jpg",
    ".jpeg",
    ".tiff",
}
MARKDOWN_EXTENSIONS = {".md"}


def needs_docling(path: Path) -> bool:
    """Indica se o arquivo precisa ser convertido com Docling."""
    return path.suffix.lower() in DOCLING_EXTENSIONS


def is_markdown(path: Path) -> bool:
    """Indica se o arquivo já é Markdown."""
    return path.suffix.lower() in MARKDOWN_EXTENSIONS


def process_file(source: Path, output_dir: Path, converter) -> bool:
    """Processa um arquivo: Docling para formatos complexos, cópia para MD."""
    try:
        if is_markdown(source):
            dest = output_dir / source.name
            shutil.copy2(source, dest)
            print(f"  OK Copiado MD: {source.name}")
            return True
        if needs_docling(source):
            result = converter.convert(str(source))
            md_content = result.document.export_to_markdown()
            dest = output_dir / (source.stem + ".md")
            dest.write_text(md_content, encoding="utf-8")
            print(f"  OK Convertido: {source.name} -> {dest.name}")
            return True
    except Exception as e:
        print(f"  ERRO em {source.name}: {e}")
        return False
    return False


def process_folder(input_dir: Path, output_dir: Path, label: str, converter) -> None:
    """Processa todos os arquivos suportados de uma pasta."""
    if not input_dir.exists():
        print(f"{label}: pasta {input_dir} não existe.")
        return
    output_dir.mkdir(parents=True, exist_ok=True)
    files = [
        f for f in input_dir.iterdir() if f.is_file() and not f.name.startswith(".")
    ]
    print(f"\n--- {label} ({len(files)} arquivos) ---")
    for f in sorted(files):
        if needs_docling(f) or is_markdown(f):
            process_file(f, output_dir, converter)
        else:
            print(f"  Ignorado (formato nao suportado): {f.name}")


def main() -> int:
    """Processa input_files e gera output_files para STRIDE e DREAD."""
    from docling.document_converter import DocumentConverter

    print("==> Processando base de conhecimento RAG (input_files → output_files)...")
    print(f"    Projeto: {_PROJECT_ROOT}")

    converter = DocumentConverter()
    process_folder(INPUT_STRIDE, OUTPUT_STRIDE, "STRIDE", converter)
    process_folder(INPUT_DREAD, OUTPUT_DREAD, "DREAD", converter)

    # Comprimir output_files em um unico arquivo para instalacao no backend
    output_files_dir = KB_DIR / "output_files"
    archive_path = KB_DIR / "rag_knowledge_base.tar.gz"
    if output_files_dir.exists():
        import tarfile

        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(output_files_dir, arcname=output_files_dir.name)
        print(f"\nArquivo unico gerado: {archive_path}")

        # Copiar output_files para threat-analyzer/app/rag_data (consumido pelo analyzer em runtime)
        RAG_DATA_DIR.mkdir(parents=True, exist_ok=True)
        for subdir in ("stride", "dread"):
            src = output_files_dir / subdir
            dst = RAG_DATA_DIR / subdir
            if src.exists():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                print(f"  Copiado para analyzer: app/rag_data/{subdir}/")
        print("\nBase RAG disponivel em threat-analyzer/app/rag_data/")

    print(
        "\nProcessamento concluido. Saidas em output_files/stride e output_files/dread."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
