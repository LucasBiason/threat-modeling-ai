"""Unit tests for app.services.rag_service."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from app.config import get_settings
from app.services.rag_service import RAGService, _CHROMA_PERSIST_SUBDIR


class TestRAGServiceInit:
    def test_init_stores_settings_and_no_retriever(self):
        settings = get_settings()
        svc = RAGService(settings)
        assert svc._settings is settings
        assert svc._retriever is None


class TestGetRetriever:
    def test_cache_hit_returns_existing_retriever(self):
        settings = get_settings()
        svc = RAGService(settings)
        sentinel = MagicMock()
        svc._retriever = sentinel
        assert svc.get_retriever() is sentinel

    def test_no_path_returns_none(self):
        settings = get_settings()
        svc = RAGService(settings)
        with patch.object(svc, "_resolve_knowledge_base_path", return_value=None):
            assert svc.get_retriever() is None

    def test_path_not_exists_returns_none(self):
        settings = get_settings()
        svc = RAGService(settings)
        fake_path = MagicMock(spec=Path)
        fake_path.exists.return_value = False
        with patch.object(svc, "_resolve_knowledge_base_path", return_value=fake_path):
            assert svc.get_retriever() is None

    @patch("app.services.rag_service.GoogleGenerativeAIEmbeddings")
    def test_setup_fail_returns_none(self, mock_embeddings):
        settings = get_settings()
        svc = RAGService(settings)
        fake_path = MagicMock(spec=Path)
        fake_path.exists.return_value = True
        fake_path.__truediv__ = MagicMock(return_value=MagicMock())
        mock_embeddings.side_effect = RuntimeError("embeddings fail")
        with patch.object(svc, "_resolve_knowledge_base_path", return_value=fake_path):
            assert svc.get_retriever() is None

    @patch("app.services.rag_service.GoogleGenerativeAIEmbeddings")
    def test_success_caches_and_returns_retriever(self, mock_embeddings):
        settings = get_settings()
        svc = RAGService(settings)
        fake_path = MagicMock(spec=Path)
        fake_path.exists.return_value = True
        persist_dir = MagicMock()
        fake_path.__truediv__ = MagicMock(return_value=persist_dir)

        mock_vs = MagicMock()
        mock_retriever = MagicMock()
        mock_vs.as_retriever.return_value = mock_retriever

        with (
            patch.object(svc, "_resolve_knowledge_base_path", return_value=fake_path),
            patch.object(svc, "_get_or_build_vectorstore", return_value=mock_vs),
        ):
            result = svc.get_retriever()
        assert result is mock_retriever
        assert svc._retriever is mock_retriever

    @patch("app.services.rag_service.GoogleGenerativeAIEmbeddings")
    def test_vectorstore_none_returns_none(self, mock_embeddings):
        settings = get_settings()
        svc = RAGService(settings)
        fake_path = MagicMock(spec=Path)
        fake_path.exists.return_value = True
        persist_dir = MagicMock()
        fake_path.__truediv__ = MagicMock(return_value=persist_dir)

        with (
            patch.object(svc, "_resolve_knowledge_base_path", return_value=fake_path),
            patch.object(svc, "_get_or_build_vectorstore", return_value=None),
        ):
            result = svc.get_retriever()
        assert result is None


class TestResolveKnowledgeBasePath:
    def test_from_settings(self):
        settings = get_settings()
        svc = RAGService(settings)
        fake_path = MagicMock(spec=Path)
        fake_path.exists.return_value = True
        svc._settings = MagicMock()
        svc._settings.knowledge_base_path = fake_path
        assert svc._resolve_knowledge_base_path() is fake_path

    def test_from_default(self):
        settings = get_settings()
        svc = RAGService(settings)
        svc._settings = MagicMock()
        svc._settings.knowledge_base_path = None
        with patch("app.services.rag_service._DEFAULT_RAG_DATA_DIR") as mock_default:
            mock_default.exists.return_value = True
            result = svc._resolve_knowledge_base_path()
        assert result is mock_default

    def test_none_when_nothing_exists(self):
        settings = get_settings()
        svc = RAGService(settings)
        svc._settings = MagicMock()
        svc._settings.knowledge_base_path = None
        with patch("app.services.rag_service._DEFAULT_RAG_DATA_DIR") as mock_default:
            mock_default.exists.return_value = False
            result = svc._resolve_knowledge_base_path()
        assert result is None


class TestGetOrBuildVectorstore:
    @patch("app.services.rag_service.Chroma")
    def test_load_from_disk(self, mock_chroma):
        settings = get_settings()
        svc = RAGService(settings)
        kb_path = MagicMock(spec=Path)
        persist_dir = MagicMock(spec=Path)
        persist_dir.mkdir = MagicMock()
        chroma_file = MagicMock()
        chroma_file.exists.return_value = True
        persist_dir.__truediv__ = MagicMock(return_value=chroma_file)
        embeddings = MagicMock()

        mock_vs = MagicMock()
        mock_chroma.return_value = mock_vs

        result = svc._get_or_build_vectorstore(kb_path, persist_dir, embeddings)
        assert result is mock_vs
        mock_chroma.assert_called_once_with(
            persist_directory=str(persist_dir),
            embedding_function=embeddings,
        )

    @patch("app.services.rag_service.Chroma")
    @patch("app.services.rag_service.RecursiveCharacterTextSplitter")
    @patch("app.services.rag_service.TextLoader")
    def test_rebuild_from_md(self, mock_loader_cls, mock_splitter_cls, mock_chroma):
        settings = get_settings()
        svc = RAGService(settings)
        kb_path = MagicMock(spec=Path)
        persist_dir = MagicMock(spec=Path)
        persist_dir.mkdir = MagicMock()
        chroma_file = MagicMock()
        chroma_file.exists.return_value = False
        persist_dir.__truediv__ = MagicMock(return_value=chroma_file)

        md_file = MagicMock(spec=Path)
        md_file.parents = []
        md_file.__eq__ = lambda self, other: False

        skipped_file = MagicMock(spec=Path)
        skipped_file.parents = [persist_dir]

        kb_path.rglob.return_value = [skipped_file, md_file]

        mock_doc = MagicMock()
        mock_loader = MagicMock()
        mock_loader.load.return_value = [mock_doc]
        mock_loader_cls.return_value = mock_loader

        mock_splitter = MagicMock()
        mock_splitter.split_documents.return_value = [mock_doc]
        mock_splitter_cls.return_value = mock_splitter

        mock_vs = MagicMock()
        mock_chroma.from_documents.return_value = mock_vs
        embeddings = MagicMock()

        result = svc._get_or_build_vectorstore(kb_path, persist_dir, embeddings)
        assert result is mock_vs
        mock_chroma.from_documents.assert_called_once()

    def test_no_md_files_returns_none(self):
        settings = get_settings()
        svc = RAGService(settings)
        kb_path = MagicMock(spec=Path)
        persist_dir = MagicMock(spec=Path)
        persist_dir.mkdir = MagicMock()
        chroma_file = MagicMock()
        chroma_file.exists.return_value = False
        persist_dir.__truediv__ = MagicMock(return_value=chroma_file)
        kb_path.rglob.return_value = []
        embeddings = MagicMock()

        result = svc._get_or_build_vectorstore(kb_path, persist_dir, embeddings)
        assert result is None

    @patch("app.services.rag_service.Chroma")
    def test_load_from_disk_fail_triggers_rebuild_no_md(self, mock_chroma):
        settings = get_settings()
        svc = RAGService(settings)
        kb_path = MagicMock(spec=Path)
        persist_dir = MagicMock(spec=Path)
        persist_dir.mkdir = MagicMock()
        chroma_file = MagicMock()
        chroma_file.exists.return_value = True
        persist_dir.__truediv__ = MagicMock(return_value=chroma_file)
        embeddings = MagicMock()

        mock_chroma.side_effect = RuntimeError("corrupt db")
        kb_path.rglob.return_value = []

        result = svc._get_or_build_vectorstore(kb_path, persist_dir, embeddings)
        assert result is None

    @patch("app.services.rag_service.Chroma")
    @patch("app.services.rag_service.TextLoader")
    def test_loader_fail_skips_file(self, mock_loader_cls, mock_chroma):
        settings = get_settings()
        svc = RAGService(settings)
        kb_path = MagicMock(spec=Path)
        persist_dir = MagicMock(spec=Path)
        persist_dir.mkdir = MagicMock()
        chroma_file = MagicMock()
        chroma_file.exists.return_value = False
        persist_dir.__truediv__ = MagicMock(return_value=chroma_file)

        md_file = MagicMock(spec=Path)
        md_file.parents = []
        md_file.name = "test.md"
        md_file.__eq__ = lambda self, other: False
        kb_path.rglob.return_value = [md_file]

        mock_loader = MagicMock()
        mock_loader.load.side_effect = RuntimeError("read error")
        mock_loader_cls.return_value = mock_loader
        embeddings = MagicMock()

        result = svc._get_or_build_vectorstore(kb_path, persist_dir, embeddings)
        assert result is None
