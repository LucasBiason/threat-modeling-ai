"""RAG service — base de conhecimento em disco (Chroma persist) e retriever com cache por processo."""

from pathlib import Path
from typing import Any

from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from threat_modeling_shared.logging import get_logger

from app.config import Settings

logger = get_logger("services.rag")

# Pasta padrão da base RAG (relativo ao app)
_DEFAULT_RAG_DATA_DIR = Path(__file__).resolve().parent.parent / "rag_data"
# Subpasta para persistência do Chroma (cache confiável em disco)
_CHROMA_PERSIST_SUBDIR = "chroma_db"


class RAGService:
    """
    Serviço RAG com persistência em disco (Chroma).
    Retriever é construído uma vez por processo e reutilizado (propriedade com cache).
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._retriever: Any = None  # cache por processo (lazy)

    def get_retriever(self) -> Any | None:
        """
        Retorna o retriever RAG (construído uma vez e cacheado).
        Usa Chroma persistido em disco para cache confiável entre reinícios.
        """
        if self._retriever is not None:
            return self._retriever
        kb_path = self._resolve_knowledge_base_path()
        if not kb_path or not kb_path.exists():
            logger.warning(
                "Knowledge base path not found (%s). Running without RAG.",
                kb_path,
            )
            return None
        persist_dir = kb_path / _CHROMA_PERSIST_SUBDIR
        try:
            embeddings = GoogleGenerativeAIEmbeddings(
                model=self._settings.embedding_model,
                google_api_key=self._settings.google_api_key,
            )
            vectorstore = self._get_or_build_vectorstore(
                kb_path=kb_path,
                persist_dir=persist_dir,
                embeddings=embeddings,
            )
            if vectorstore is None:
                return None
            self._retriever = vectorstore.as_retriever()
            return self._retriever
        except Exception as e:
            logger.error("RAG setup failed: %s", e)
            return None

    def _resolve_knowledge_base_path(self) -> Path | None:
        if (
            self._settings.knowledge_base_path
            and self._settings.knowledge_base_path.exists()
        ):
            return self._settings.knowledge_base_path
        if _DEFAULT_RAG_DATA_DIR.exists():
            return _DEFAULT_RAG_DATA_DIR
        return None

    def _get_or_build_vectorstore(
        self,
        kb_path: Path,
        persist_dir: Path,
        embeddings: GoogleGenerativeAIEmbeddings,
    ) -> Any | None:
        """Carrega Chroma do disco se existir; senão constrói a partir dos .md e persiste."""
        persist_dir.mkdir(parents=True, exist_ok=True)
        chroma_sqlite = persist_dir / "chroma.sqlite3"
        if chroma_sqlite.exists():
            try:
                return Chroma(
                    persist_directory=str(persist_dir),
                    embedding_function=embeddings,
                )
            except Exception as e:
                logger.warning("Chroma load from disk failed, rebuilding: %s", e)
        # Construir a partir dos .md
        md_files = list(kb_path.rglob("*.md"))
        if not md_files:
            return None
        all_docs = []
        for file_path in md_files:
            if file_path == persist_dir or persist_dir in file_path.parents:
                continue
            try:
                loader = TextLoader(str(file_path), encoding="utf-8")
                all_docs.extend(loader.load())
            except Exception as e:
                logger.warning("Failed to load %s: %s", file_path.name, e)
        if not all_docs:
            return None
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self._settings.rag_chunk_size,
            chunk_overlap=self._settings.rag_chunk_overlap,
        )
        chunks = splitter.split_documents(all_docs)
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=str(persist_dir),
        )
        return vectorstore
