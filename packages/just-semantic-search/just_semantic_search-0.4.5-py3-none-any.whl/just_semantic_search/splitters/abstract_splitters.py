from just_semantic_search.embeddings import EmbeddingModelParams
from sentence_transformers import SentenceTransformer
from typing import List, TypeAlias, TypeVar, Generic, Optional, Any, Callable, Union
import numpy as np
from pathlib import Path
import re
from abc import ABC, abstractmethod
from transformers import PreTrainedTokenizer
from just_semantic_search.document import ArticleDocument, Document, IDocument
from multiprocessing import Pool, cpu_count
import torch
import time
from eliot import log_call, log_message, start_action
from just_semantic_search.utils.models import get_sentence_transformer_model_name
from pydantic import BaseModel, ConfigDict, Field

from just_semantic_search.document import Document, IDocument
from sentence_transformers import SentenceTransformer
from typing import Generic, List, Optional, TypeAlias
import re
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from transformers import PreTrainedTokenizer
from pathlib import Path
# Define type variables for input and output types
CONTENT = TypeVar('CONTENT')  # Generic content type


class AbstractSplitter(ABC, BaseModel, Generic[CONTENT, IDocument]):
    """Abstract base class for splitting content into documents with optional embedding."""
    
    #model: SentenceTransformer
    max_seq_length: Optional[int] = None
    model_name: Optional[str] = None
    write_token_counts: bool = Field(default=True)
    batch_size: int = Field(default=32)
    normalize_embeddings: bool = Field(default=False)
    #extra_embed_arguments: dict = Field(default_factory=dict)
    
    
    @property
    def document_type(self) -> type[IDocument]:
        return Document

    model_config = ConfigDict(arbitrary_types_allowed=True)  # Needed for SentenceTransformer type


    @abstractmethod
    def split(self, content: CONTENT, embed: bool = True, source: str | None = None, **kwargs) -> List[IDocument]:
        """Split content into documents and optionally embed them."""
        pass

    @abstractmethod
    def _content_from_path(self, file_path: Path) -> CONTENT:
        """Load content from a file path."""
        pass

    def split_file(self, file_path: Path | str, embed: bool = True, path_as_source: bool = True, **kwargs) -> List[IDocument]:
        """Convenience method to split content directly from a file."""
        if isinstance(file_path, str):
            file_path = Path(file_path)
            
        with start_action(action_type="processing_file", file_path=str(file_path.absolute())) as action:
            content: CONTENT = self._content_from_path(file_path)
            documents = self.split(content, embed, 
                               source=str(file_path.absolute()) if path_as_source else file_path.name,
                               **kwargs)
            action.add_success_fields(num_documents=len(documents))
            return documents

    def split_folder(self, folder_path: Path | str, embed: bool = True, path_as_source: bool = True, filter: Optional[Callable[[Path], bool]] = None, **kwargs) -> List[IDocument]:
        """Split all files in a folder into documents.
        
        Args:
            folder_path: Path to the folder containing files to split
            embed: Whether to embed the documents
            path_as_source: Whether to use the file path as the source
            filter: Optional function that takes a file path and returns True if the file should be processed
            **kwargs: Additional arguments to pass to split_file
        """
        with start_action(action_type="split_folder", folder_path=str(folder_path.absolute()), embed=embed, path_as_source=path_as_source) as action:
            start_time = time.time()
            folder_path = Path(folder_path) if isinstance(folder_path, str) else folder_path
        
            # Log the folder path separately as a string
            action.log(message_type="processing_folder", folder_path=str(folder_path.absolute()))
            
            if not folder_path.exists() or not folder_path.is_dir():
                raise ValueError(f"Invalid folder path: {folder_path}")

            documents = []
            for file_path in folder_path.iterdir():
                if file_path.is_file() and (filter is None or filter(file_path)):
                    documents.extend(self.split_file(file_path, embed, path_as_source, **kwargs))
            
            elapsed_time = time.time() - start_time
            action.log(
                message_type="folder_processing_complete",
                processing_time_seconds=elapsed_time,
                num_documents=len(documents)
            )
                    
            return documents
    
    @abstractmethod
    def embed_content(self, content: CONTENT, **kwargs) -> np.ndarray:
        # will be used to embed content with corresponding model. Maybe we need to make a model wrapper class?
        pass

    @abstractmethod
    def get_tokens_and_chunks(self, content: CONTENT) -> tuple[List[str], List[str]]:
        # used to tokenize content and also get chunks
        # often resolved from mixings
        pass

    @log_call(
        action_type="split_folder_with_batches", 
        include_args=["batch_size", "embed", "path_as_source", "num_processes"],
        include_result=False
    )
    def split_folder_with_batches(
        self, 
        folder_path: Path | str, 
        batch_size: int = 20,
        embed: bool = True, 
        path_as_source: bool = True,
        num_processes: Optional[int] = None,
        filter: Optional[Callable[[Path], bool]] = None,
        **kwargs
    ) -> List[List[IDocument]]:
        """
        NOTE: SO FAR I DID NOT MANAGED TO GET BENEFITS FROM THIS METHOD. PROBABLY DEFAULT SENTENCE TRANSFORMER BATCH SIZE IS ENOUGH.
        """
        start_time = time.time()
        folder_path = Path(folder_path) if isinstance(folder_path, str) else folder_path
        
        # Log the folder path separately as a string
        log_message(message_type="processing_batched_folder", folder_path=str(folder_path.absolute()))
        
        # Validate inputs
        if not folder_path.exists() or not folder_path.is_dir():
            raise ValueError(f"The folder_path '{folder_path}' does not exist or is not a directory.")
        if batch_size <= 0:
            raise ValueError("batch_size must be a positive integer.")
            
        # Setup processing
        cuda_devices = torch.cuda.device_count() if torch.cuda.is_available() else 0
        if num_processes is None:
            num_processes = min(cpu_count(), max(1, cuda_devices))
        if num_processes < 1:
            raise ValueError("num_processes must be at least 1.")
            
        # Collect and process files
        file_paths = [f for f in folder_path.iterdir() if f.is_file() and (filter is None or filter(f))]
        if not file_paths:
            return []
            
        # Process files
        if num_processes > 1 and cuda_devices > 0:
            with Pool(num_processes) as pool:
                from functools import partial
                process_file = partial(
                    self.split_file, 
                    embed=embed, 
                    path_as_source=path_as_source, 
                    **kwargs
                )
                all_docs = pool.map(process_file, file_paths)
                all_docs = [doc for file_docs in all_docs for doc in file_docs]
        else:
            all_docs = [
                doc
                for file_path in file_paths
                for doc in self.split_file(file_path, embed, path_as_source, **kwargs)
            ]
        
        # Group into batches
        batches = []
        current_batch = []
        for doc in all_docs:
            current_batch.append(doc)
            if len(current_batch) >= batch_size:
                batches.append(current_batch)
                current_batch = []
        
        if current_batch:
            batches.append(current_batch)
        
        elapsed_time = time.time() - start_time
        log_message(
            message_type="batched_folder_processing_complete",
            processing_time_seconds=elapsed_time,
            num_batches=len(batches),
            total_documents=sum(len(batch) for batch in batches)
        )
            
        return batches


class SentenceTransformerMixin(BaseModel):
    """
    Mixin class providing SentenceTransformer embedding functionality.
    Can be combined with different splitter implementations.
    """
    model: SentenceTransformer
    tokenizer: Optional[Union[PreTrainedTokenizer, object]] = None
    model_params: EmbeddingModelParams = Field(default_factory=EmbeddingModelParams)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)  # Needed for SentenceTransformer type
    
    def model_post_init(self, __context) -> None:
        if self.tokenizer is None:
            self.tokenizer = self.model.tokenizer
        if hasattr(self, 'max_seq_length') and self.max_seq_length is None:
            self.max_seq_length = self.model.max_seq_length
        if hasattr(self, 'model_name') and self.model_name is None:
            model_value = get_sentence_transformer_model_name(self.model)
            self.model_name = model_value.split("/")[-1].split("\\")[-1] if "/" in model_value or "\\" in model_value else model_value

    def get_tokens_and_chunks(self, text: str, metadata_overhead: int = 0) -> tuple[List[str], List[str]]:
        # Get the tokenizer from the model
        tokenizer = self.model.tokenizer

        # Tokenize the entire text
        tokens = tokenizer.tokenize(text)

        # Adjust max_seq_length for metadata overhead
        effective_max_length = self.max_seq_length - metadata_overhead

        # Split tokens into chunks of effective_max_length
        token_chunks = [tokens[i:i + effective_max_length] for i in range(0, len(tokens), effective_max_length)]
        
        # Convert token chunks back to text
        text_chunks = [tokenizer.convert_tokens_to_string(chunk) for chunk in token_chunks]
        return token_chunks, text_chunks
    

    def embed_content(self, content: str, **kwargs) -> np.ndarray:
        kwargs.update(self.model_params.retrival_passage)
        return self.model.encode(content, convert_to_numpy=True, **kwargs)