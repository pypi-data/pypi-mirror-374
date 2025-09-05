from abc import ABC, abstractmethod
from typing import List, Dict, Any, Generator, Set
from pathlib import Path
from .data_models import Document


class BaseChunker(ABC):
    """Abstract base class for document chunkers."""

    name: str

    def __init__(self, **kwargs: Dict[str, Any]):
        """Initialize the chunker with configuration parameters."""
        self.config = kwargs

    @abstractmethod
    def chunk(self, document: Document) -> Document:
        """Chunk a single document and return it with chunks populated."""
        pass

    @abstractmethod
    def chunk_batch(self, documents: List[Document]) -> List[Document]:
        """Chunk a batch of documents and return them with chunks populated."""
        pass


class BaseLLM(ABC):
    """Abstract base class for language models."""

    def __init__(self, **kwargs: Dict[str, Any]):
        """Initialize the LLM with configuration parameters."""
        self.config = kwargs

    @abstractmethod
    def load(self):
        """Load the model."""
        pass

    @abstractmethod
    def run(self, messages: List[Dict[str, str]]) -> str:
        """Run the model and return the complete response."""
        pass

    @abstractmethod
    def stream(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """Stream the model response. Returns a generator of response chunks."""
        pass


class BaseVectorizer(ABC):
    """Abstract base class for text vectorizers."""

    name: str
    dimension: int

    def __init__(self, **kwargs: Dict[str, Any]):
        """Initialize the vectorizer with configuration parameters."""
        self.config = kwargs

    @abstractmethod
    def vectorize(self, text: str):
        """Vectorize a single text string."""
        pass

    @abstractmethod
    def vectorize_batch(self, texts: List[str]):
        """Vectorize a batch of text strings."""
        pass


class BaseLoader(ABC):
    """Abstract base class for document loaders."""

    name: str
    supported_formats: Set[str] = set()  

    def __init__(self, **kwargs: Dict[str, Any]):
        """Initialize the loader with configuration parameters."""
        self.config = kwargs

    def _validate_file_format(self, file_path: Path) -> bool:
        """Validate if the file format is supported by this loader."""
        if not self.supported_formats:
            return True  # If no formats specified, assume all are supported
        
        file_extension = file_path.suffix.lower().lstrip('.')
        return file_extension in self.supported_formats

    def _raise_unsupported_format_error(self, file_path: Path):
        """Raise an error for unsupported file format."""
        file_extension = file_path.suffix.lower().lstrip('.')
        raise ValueError(
            f"Unsupported file format '{file_extension}' for {self.name} loader. "
            f"Supported formats: {', '.join(sorted(self.supported_formats))}"
        )

    @abstractmethod
    def load_files_from_dir(self, path: str) -> List[Document]:
        """Load documents from a directory path."""
        pass
