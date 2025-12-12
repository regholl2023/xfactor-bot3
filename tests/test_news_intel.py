"""Tests for News Intelligence module."""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch


class TestLocalFileWatcher:
    """Tests for LocalFileWatcher."""

    @pytest.fixture
    def watcher(self):
        from src.news_intel.local_file_watcher import LocalFileWatcher
        return LocalFileWatcher(base_path=tempfile.mkdtemp())

    def test_initialization(self, watcher):
        """Test that watcher initializes properly."""
        assert watcher.base_path is not None
        assert watcher.incoming_path is not None
        assert watcher.processed_path is not None

    def test_paths_exist(self, watcher):
        """Test that paths are pathlib.Path objects."""
        assert isinstance(watcher.base_path, Path)
        assert isinstance(watcher.incoming_path, Path)


class TestDocumentParser:
    """Tests for DocumentParser."""

    @pytest.fixture
    def parser(self):
        from src.news_intel.local_file_watcher import DocumentParser
        return DocumentParser()

    @pytest.mark.asyncio
    async def test_parse_csv(self, parser):
        """Test parsing CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("symbol,headline,sentiment\n")
            f.write("AAPL,Apple announces new iPhone,0.8\n")
            f.flush()
            try:
                result = await parser.parse(Path(f.name))
                assert result is not None
                assert result.file_type in ["csv", "csv_structured"]
            finally:
                os.unlink(f.name)

    @pytest.mark.asyncio
    async def test_parse_txt(self, parser):
        """Test parsing text file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Breaking News: TSLA hits new high\n")
            f.flush()
            try:
                result = await parser.parse(Path(f.name))
                assert result is not None
                assert result.file_type == "txt"
                assert "TSLA" in result.content
            finally:
                os.unlink(f.name)


class TestParsedDocument:
    """Tests for ParsedDocument dataclass."""

    def test_parsed_document_creation(self):
        """Test creating a ParsedDocument."""
        from src.news_intel.local_file_watcher import ParsedDocument
        
        doc = ParsedDocument(
            file_name="test.csv",
            file_type="csv",
            content="test content",
            page_count=1,
            metadata={"source": "test"}
        )
        
        assert doc.file_name == "test.csv"
        assert doc.file_type == "csv"
        assert doc.is_structured == False

    def test_parsed_document_with_structured_data(self):
        """Test ParsedDocument with structured data."""
        from src.news_intel.local_file_watcher import ParsedDocument
        
        doc = ParsedDocument(
            file_name="test.csv",
            file_type="csv_structured",
            content="test content",
            structured_data=[{"symbol": "AAPL", "rating": "Buy"}]
        )
        
        assert doc.is_structured == True
        assert len(doc.structured_data) == 1


class TestSafeGetSymbol:
    """Tests for safe_get_symbol helper function."""

    def test_with_valid_symbol(self):
        """Test extracting valid symbol."""
        import pandas as pd
        from src.news_intel.local_file_watcher import safe_get_symbol
        
        row = pd.Series({"symbol": "AAPL", "price": 175.0})
        result = safe_get_symbol(row)
        assert result == "AAPL"

    def test_with_nan_symbol(self):
        """Test handling NaN symbol."""
        import pandas as pd
        import numpy as np
        from src.news_intel.local_file_watcher import safe_get_symbol
        
        row = pd.Series({"symbol": np.nan, "price": 175.0})
        result = safe_get_symbol(row)
        assert result is None

    def test_with_ticker_fallback(self):
        """Test falling back to ticker column."""
        import pandas as pd
        from src.news_intel.local_file_watcher import safe_get_symbol
        
        row = pd.Series({"ticker": "NVDA", "price": 500.0})
        result = safe_get_symbol(row)
        assert result == "NVDA"
