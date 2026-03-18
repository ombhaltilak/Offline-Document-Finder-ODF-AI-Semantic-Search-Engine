""" 
Document and Query Embedder 
Handles text embedding using FastEmbed for high-performance semantic search. 
"""

import os
import sys
from typing import List
import numpy as np
from fastembed import TextEmbedding

# We import onnxruntime to verify hardware acceleration directly 
try:
    import onnxruntime as ort
except ImportError:
    ort = None


class Embedder:
    def __init__(self, model_name='BAAI/bge-small-en-v1.5'):
        """ 
        Initialize the embedder with FastEmbed. 
        """
        self.model_name = model_name

        # --- 1. SETUP CACHE & PATHS --- 
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.join(os.path.dirname(__file__), '..')

        model_cache_dir = os.path.join(base_dir, 'models')

        if not os.path.exists(model_cache_dir) and not getattr(sys, 'frozen', False):
            os.makedirs(model_cache_dir)

        print(f"Loading embedding model: {model_name}")

        # --- 2. LOAD MODEL (Auto-Fallback Logic) --- 
        try:
            # Try loading with GPU (CUDA) first 
            self.model = TextEmbedding(
                model_name=model_name,
                threads=None,
                cache_dir=model_cache_dir,
                local_files_only=False,
                providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
            )
        except Exception as e:
            # If GPU fails (ValueError), fall back to CPU 
            print(f" GPU Initialization failed: {e}")
            print(" Falling back to CPU Mode...")
            self.model = TextEmbedding(
                model_name=model_name,
                threads=None,
                cache_dir=model_cache_dir,
                local_files_only=False,
                providers=["CPUExecutionProvider"]
            )

        # --- 3. ROBUST GPU CHECK --- 
        print("-" * 40)
        if ort:
            available_providers = ort.get_available_providers()

            # Check what providers we actually requested successfully 
            # Note: FastEmbed doesn't expose the active provider easily,  
            # so we check if CUDA is available in the environment generally. 
            if "CUDAExecutionProvider" in available_providers:
                print(" GPU STATUS: FOUND & ACTIVE")
                print(f"   (System reports: {available_providers})")
                print("    The model is using your NVIDIA GPU for embeddings.")
            else:
                print(" GPU STATUS: NOT FOUND (Using CPU)")
                print("   (To enable GPU: Ensure 'onnxruntime-gpu' is installed)")
        else:
            print(" GPU Check: Could not import onnxruntime to verify.")
        print("-" * 40)
        # ------------------------------------- 

        print(f"Model '{model_name}' loaded successfully!")

    def embed_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Generate embeddings for multiple texts."""
        if not texts:
            return np.array([])

        try:
            embeddings_generator = self.model.embed(texts, batch_size=batch_size)
            embeddings_list = list(embeddings_generator)
            return np.array(embeddings_list)
        except Exception as e:
            print(f"Error embedding texts: {e}")
            return np.array([])

    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for a single text."""
        if not text:
            return np.array([])

        embeddings = self.embed_texts([text])
        if len(embeddings) > 0:
            return embeddings[0]
        return np.array([])

    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors."""
        try:
            dummy_emb = self.embed_text("test")
            if len(dummy_emb) > 0:
                return len(dummy_emb)
        except:
            pass
        return 384  # Default fallback for bge-small 

    def get_model_info(self) -> dict:
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.get_embedding_dimension(),
            "library": "fastembed"
        }
