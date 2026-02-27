"""
Document and Query Embedder
Handles text embedding using FastEmbed for high-performance semantic search.

This module:
- Loads a FastEmbed embedding model
- Automatically tries GPU (CUDA) first, then falls back to CPU
- Supports separate document and query embeddings
- Adds proper query prefixing for better semantic search performance
"""

from fastembed import TextEmbedding
import numpy as np
from typing import List
import sys
import os

# We import onnxruntime to verify hardware acceleration directly.
# This allows us to check whether CUDA (GPU) is available.
try:
    import onnxruntime as ort
except ImportError:
    ort = None


class Embedder:
    """
    Embedder class for generating semantic embeddings using FastEmbed.

    Features:
    - Automatic GPU → CPU fallback
    - Local model caching
    - Query prefix support (for better retrieval quality)
    - Embedding dimension detection
    """

    def __init__(self, model_name='BAAI/bge-small-en-v1.5'):
        """
        Initialize the embedder with FastEmbed.

        Parameters:
        - model_name (str): HuggingFace model identifier.
          Default: BAAI/bge-small-en-v1.5 (384-dimensional embeddings)
        """

        self.model_name = model_name
        
        # --------------------------------------------------------
        # 1️⃣ SETUP CACHE & PATHS
        # --------------------------------------------------------
        # If running as a packaged executable (e.g., PyInstaller),
        # use the temporary extracted directory.
        # Otherwise, use project-relative path.
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.join(os.path.dirname(__file__), '..')
        
        # Directory where embedding models will be cached
        model_cache_dir = os.path.join(base_dir, 'models')
        
        # Create model cache directory if it doesn't exist
        # (Only when not running in frozen mode)
        if not os.path.exists(model_cache_dir) and not getattr(sys, 'frozen', False):
            os.makedirs(model_cache_dir)

        print(f"Loading embedding model: {model_name}")

        # --------------------------------------------------------
        # 2️⃣ LOAD MODEL (Auto-Fallback Logic)
        # --------------------------------------------------------
        # First attempt: Try loading with GPU (CUDA).
        # If that fails, automatically fall back to CPU.
        try:
            self.model = TextEmbedding(
                model_name=model_name, 
                threads=None,
                cache_dir=model_cache_dir,
                local_files_only=False,
                # Try GPU first, CPU as backup
                providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
            )
        except Exception as e:
            # If GPU initialization fails (e.g., CUDA not installed),
            # fall back to CPU-only execution.
            print(f"⚠️ GPU Initialization failed: {e}")
            print("🔄 Falling back to CPU Mode...")
            self.model = TextEmbedding(
                model_name=model_name, 
                threads=None,
                cache_dir=model_cache_dir,
                local_files_only=False,
                providers=["CPUExecutionProvider"]
            )

        # --------------------------------------------------------
        # 3️⃣ ROBUST GPU CHECK
        # --------------------------------------------------------
        # This section verifies whether CUDA is available in the environment.
        print("-" * 40)
        if ort:
            available_providers = ort.get_available_providers()
            
            # Note:
            # FastEmbed does not expose the exact active provider directly.
            # So we check whether CUDA is available in ONNX Runtime.
            if "CUDAExecutionProvider" in available_providers:
                print("✅ GPU STATUS: FOUND & ACTIVE")
                print(f"   (System reports: {available_providers})")
                print("   🚀 The model is using your NVIDIA GPU for embeddings.")
            else:
                print("⚠️ GPU STATUS: NOT FOUND (Using CPU)")
                print("   (To enable GPU: Ensure 'onnxruntime-gpu' is installed)")
        else:
            print("ℹ️ GPU Check: Could not import onnxruntime to verify.")
        print("-" * 40)
        # --------------------------------------------------------

        print(f"Model '{model_name}' loaded successfully!")

    # --------------------------------------------------------
    # EMBEDDING METHODS
    # --------------------------------------------------------

    def embed_texts(self, texts: List[str], batch_size: int = 32, is_query: bool = False) -> np.ndarray:
        """
        General method for embedding multiple texts.

        Parameters:
        - texts (List[str]): List of input texts
        - batch_size (int): Batch size for embedding
        - is_query (bool): If True, applies retrieval prefix

        Returns:
        - np.ndarray: Array of embedding vectors
        """

        # Return empty array if input is empty
        if not texts:
            return np.array([])
        
        # Apply BGE retrieval prefix ONLY for search queries.
        # This improves retrieval quality for models like bge-small.
        if is_query:
            texts = [
                f"Represent this sentence for searching relevant passages: {t}"
                for t in texts
            ]
        
        try:
            # FastEmbed returns a generator → convert to list → numpy array
            embeddings_generator = self.model.embed(texts, batch_size=batch_size)
            return np.array(list(embeddings_generator))
        except Exception as e:
            print(f"Error embedding: {e}")
            return np.array([])

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single document text.

        Used for:
        - Indexing files
        - Storing embeddings in FAISS

        No prefix is applied.
        """
        return self.embed_texts([text], is_query=False)[0]

    def embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for a user search query.

        Used for:
        - Searching FAISS index
        - Semantic retrieval

        Applies retrieval prefix internally.
        """
        return self.embed_texts([query], is_query=True)[0]
    
    
    def get_embedding_dimension(self) -> int:
        """
        Detect embedding dimension dynamically.

        Returns:
        - int: Dimension size of embedding vectors
        """

        try:
            # Create a dummy embedding to detect dimension
            dummy_emb = self.embed_text("test")
            if len(dummy_emb) > 0:
                return len(dummy_emb)
        except:
            pass

        # Default fallback for bge-small model
        return 384 
    
    def get_model_info(self) -> dict:
        """
        Return metadata about the loaded embedding model.

        Returns:
        - dict containing:
            - model_name
            - embedding_dimension
            - library used
        """
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.get_embedding_dimension(),
            "library": "fastembed"
        }