"""
<<<<<<< HEAD
Vector Search Engine (LanceDB + GPU Support)
Handles high-performance, disk-based similarity search using LanceDB.
Automatically selects GPU (CUDA) if available, otherwise falls back to CPU.
"""

import lancedb
import os
=======
Vector Search Engine
Handles ChromaDB-based similarity search for document retrieval.

This module:
- Stores document embeddings inside ChromaDB
- Splits large documents into chunks
- Performs semantic + lexical hybrid search
- Supports metadata filtering
- Handles safe and forced database reset
"""

import chromadb
from chromadb.config import Settings  # <--- Essential for Reset Permission
import os
import sys
import shutil
import gc
>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
import time
import importlib.util
from fastembed import TextEmbedding

# --- CONFIGURATION ---
# State-of-the-Art local model.
MODEL_NAME = "mixedbread-ai/mxbai-embed-large-v1" 


class VectorSearch:
    def __init__(self):
<<<<<<< HEAD
        """Initialize the vector search engine with LanceDB and auto-GPU detection."""
        
        # 1. Initialize Embedder with Smart Device Detection
        print(f"Loading embedding model: {MODEL_NAME}...")
        
        # Default to CPU
        providers = ["CPUExecutionProvider"]
        device_label = "CPU"

        # Check for NVIDIA GPU (CUDA) support via ONNX Runtime
        try:
            import onnxruntime as ort
            available_providers = ort.get_available_providers()
            if "CUDAExecutionProvider" in available_providers:
                providers = ["CUDAExecutionProvider"]
                device_label = "GPU (NVIDIA CUDA)"
        except ImportError:
            pass # onnxruntime not installed, standard CPU fallback

        print(f"Targeting Hardware: {device_label}")

        try:
            # Initialize FastEmbed with the selected provider
            self.model = TextEmbedding(
                model_name=MODEL_NAME,
                providers=providers
            )
            self.embedder = self.model
            print(f"Model '{MODEL_NAME}' loaded successfully on {device_label}!")
            
        except Exception as e:
            print(f"Error loading model {MODEL_NAME} on {device_label}: {e}")
            print("Falling back to default BGE-Small on CPU...")
            try:
                self.model = TextEmbedding("BAAI/bge-small-en-v1.5", providers=["CPUExecutionProvider"])
                self.embedder = self.model
            except Exception as fallback_error:
                print(f"Critical error loading fallback model: {fallback_error}")

        # 2. Setup Database Path
        # Logic: If running as .exe, store next to it. If script, store in project root.
        import sys
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
            
        self.db_path = os.path.join(base_dir, 'data', 'lancedb')
        
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)

        # 3. Connect to LanceDB
        self.db = lancedb.connect(self.db_path)
        
        # 4. Open or Create Table
        self.table_name = "documents"
        self.table = None
        
        if self.table_name in self.db.table_names():
            self.table = self.db.open_table(self.table_name)
            print(f"Connected to existing LanceDB table at {self.db_path}")
        else:
            print(f"LanceDB initialized at {self.db_path} (Table will be created on first index)")

    def _recursive_text_split(self, text, chunk_size=1000, chunk_overlap=100):
        """Split text with a safety valve to prevent infinite loops on long strings."""
        if not text: return []
=======
        """Initialize the vector search engine with ChromaDB."""
        
        # Initialize embedding model (used for indexing + querying)
        self.embedder = Embedder()
        
        # --------------------------------------------------------
        # Determine database storage path
        # --------------------------------------------------------
        # If packaged (PyInstaller), use executable directory
        # Otherwise use project root directory
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.join(os.path.dirname(__file__), '..')
            
        # Persistent ChromaDB folder
        self.db_path = os.path.join(base_dir, 'data', 'chroma_db')
        
        # Initialize the database
        self._init_db()

    def _init_db(self):
        """
        Initialize ChromaDB client and collection.

        - Creates database folder if missing
        - Enables reset permissions
        - Uses cosine similarity space (HNSW)
        """
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)
            
        # PersistentClient ensures embeddings are stored on disk
        self.client = chromadb.PersistentClient(
            path=self.db_path,
            settings=Settings(allow_reset=True)  # Required to allow reset()
        )
        
        # Create or load collection
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}  # Cosine similarity search
        )
        print(f"VectorSearch initialized at {self.db_path}")

    def _recursive_text_split(self, text, chunk_size=1000, chunk_overlap=100):
        """
        Split long text into overlapping chunks.

        - chunk_size: max characters per chunk
        - chunk_overlap: overlap between chunks to preserve context
        - Tries to split intelligently at:
          paragraphs → lines → sentences → spaces
        """
        if not text:
            return []

>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + chunk_size

            if end >= text_len:
                chunks.append(text[start:])
                break
<<<<<<< HEAD
            
            # Find a natural break point
=======

>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
            break_point = -1

            # Try to split at natural boundaries
            for sep in ['\n\n', '\n', '. ', ' ']:
                idx = text.rfind(sep, start, end)
                if idx != -1 and idx > start + (chunk_size // 2):
                    break_point = idx + len(sep)
                    break

            if break_point != -1:
                chunks.append(text[start:break_point])
<<<<<<< HEAD
                start = break_point - chunk_overlap 
            else:
                # --- SAFETY FIX: Force split if no natural separator found ---
                # This handles massive hex dumps or code strings without spaces
                chunks.append(text[start:end])
                start = end - chunk_overlap
        
        return chunks
    
    def add_documents(self, documents_generator, batch_size=16, progress_callback=None):
        """Add documents to LanceDB with Error Skipping."""
        batch_data = []
        count = 0
        
        for doc in documents_generator:
            # --- 🛡️ ERROR HANDLING START ---
            try:
                content = doc['content']
                base_id = doc['id']
                metadata = doc['metadata']
                file_path = metadata.get('source', 'Unknown File')

                # DEBUG: Print what we are working on (so you know if it hangs)
                file_path = doc['metadata'].get('source', 'Unknown Path')
                print(f"Processing: {file_path}")

                chunks = self._recursive_text_split(content)
                
                if chunks:
                    # Embed chunks (Safe Batching)
                    embeddings = list(self.model.embed(chunks, batch_size=batch_size))
                
                    for i, chunk in enumerate(chunks):
                        chunk_id = f"{base_id}_chunk_{i}"
                        row = {
                            "id": chunk_id,
                            "vector": embeddings[i].tolist(),
                            "content": chunk,
                            "filename": metadata.get('filename', ''),
                            "source": metadata.get('source', ''),
                            "chunk_index": i,
                            "created_at": time.time()
                        }
                        batch_data.append(row)

            except Exception as e:
                # 🛑 THIS IS THE SKIP LOGIC
                print(f"\n⚠️ SKIPPING CORRUPT FILE: {doc.get('metadata', {}).get('source', 'Unknown')}")
                print(f"   Reason: {e}\n")
                continue 
            # --- 🛡️ ERROR HANDLING END ---

            # Process Batch (Write to Database)
            # We do this OUTSIDE the try/except so valid data from previous files gets saved
            if len(batch_data) >= batch_size:
                self._upsert_batch(batch_data)
                batch_data = []
=======
                start = break_point - chunk_overlap
            else:
                chunks.append(text[start:end])
                start = end - chunk_overlap

        return chunks
    
    def add_documents(self, documents_generator, batch_size=100, progress_callback=None):
        """
        Add documents to ChromaDB.

        - Accepts generator of documents
        - Splits content into chunks
        - Processes in batches
        - Supports progress callback
        """
        batch_ids, batch_documents, batch_metadatas = [], [], []
        count = 0
        
        for item in documents_generator:
            
            # Support tuple-based input OR dictionary-based input
            if isinstance(item, tuple):
                base_id, content, file_path = item
                metadata = {"source": file_path, "filename": os.path.basename(file_path)}
            else:
                content = item['content']
                base_id = item['id']
                metadata = item['metadata']
            
            # Split into semantic chunks
            chunks = self._recursive_text_split(content)

            for i, chunk in enumerate(chunks):
                chunk_id = f"{base_id}_chunk_{i}"

                batch_ids.append(chunk_id)
                batch_documents.append(chunk)

                # Copy metadata per chunk
                chunk_meta = metadata.copy()
                chunk_meta['chunk_index'] = i
                batch_metadatas.append(chunk_meta)
            
            # Process in batches for performance
            if len(batch_ids) >= batch_size:
                self._process_batch(batch_ids, batch_documents, batch_metadatas)
                batch_ids, batch_documents, batch_metadatas = [], [], []
>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
            
            count += 1

            # Optional progress tracking
            if progress_callback:
                progress_callback(count, metadata.get('filename', ''))
<<<<<<< HEAD
            elif count % 10 == 0:
                print(f"Processed {count} documents...")

        # Process remaining
        if batch_data:
            self._upsert_batch(batch_data)
            
        print(f"Finished adding {count} documents to LanceDB.")
    def _upsert_batch(self, data):
        """Helper to insert/upsert data into LanceDB."""
        if not data: return

        try:
            if self.table is None and self.table_name not in self.db.table_names():
                self.table = self.db.create_table(self.table_name, data=data)
            elif self.table is None:
                self.table = self.db.open_table(self.table_name)
                self.table.add(data)
            else:
                try:
                    self.table.merge_insert("id") \
                        .when_matched_update_all() \
                        .when_not_matched_insert_all() \
                        .execute(data)
                except:
                    self.table.add(data)
=======
            elif count % 100 == 0:
                print(f"Processed {count} documents...")

        # Process remaining batch
        if batch_ids:
            self._process_batch(batch_ids, batch_documents, batch_metadatas)

        print(f"Finished adding {count} documents.")

    def _process_batch(self, ids, documents, metadatas):
        """
        Embed and upsert a batch of documents into ChromaDB.
        """
        try:
            embeddings = self.embedder.embed_texts(documents)

            # Upsert = insert or update if ID already exists
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings.tolist()
            )
>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
        except Exception as e:
            print(f"Error writing batch to LanceDB: {e}")

    def search(self, query, top_k=10, filter_metadata=None):
<<<<<<< HEAD
        """Search LanceDB using Hybrid logic (Vector + Keyword Boost)."""
=======
        """
        Perform hybrid search:
        - Semantic similarity (cosine distance)
        - Lexical boosting (filename, content, sheet name)
        """
>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
        try:
            if self.table is None:
                if self.table_name in self.db.table_names():
                    self.table = self.db.open_table(self.table_name)
                else:
                    return []

            # 1. Embed Query (Uses GPU if available)
            query_embedding = list(self.model.embed([query]))[0]
            
            # 2. Vector Search
            candidates = self.table.search(query_embedding) \
                .metric("cosine") \
                .limit(top_k * 3) \
                .to_list()
            
            if not candidates:
                return []

<<<<<<< HEAD
            # 3. Hybrid Re-ranking
            query_lower = query.lower().strip()
            final_results = []

            for item in candidates:
                distance = item['_distance']
                base_score = 1 - distance
                
                content_text = item['content']
                filename = item['filename'].lower()
                
                boost_applied = False
                final_score = base_score
                
                if query_lower in filename:
                    final_score += 0.25
                    boost_applied = True
                    
=======
            # Generate query embedding
            query_embedding = self.embedder.embed_query(query)

            # Retrieve more candidates than needed (for re-ranking)
            candidate_k = top_k * 3

            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=candidate_k,
                where=filter_metadata
            )

            if not results['ids']:
                return []
            
            ids = results['ids'][0]
            distances = results['distances'][0]
            metadatas = results['metadatas'][0]
            documents = results['documents'][0]

            candidates = []
            query_lower = query.lower().strip()
            
            for i in range(len(ids)):
                
                # Convert cosine distance to similarity
                base_score = 1 - (distances[i])
                final_score = base_score

                content_text = documents[i] or ""
                metadata = metadatas[i] or {}
                filename = metadata.get('filename', '').lower()
                
                # ------------------------------------------------
                # LEXICAL BOOSTING
                # ------------------------------------------------
                # Boost if query appears in filename
                if query_lower in filename:
                    final_score += 0.25
                
                # Excel-specific boosting (sheet name match)
                sheet_name = metadata.get('sheet_name', '').lower()
                if sheet_name and query_lower in sheet_name:
                    final_score += 0.15 

                # Boost if query appears in chunk text
>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
                if query_lower in content_text.lower():
                    final_score += 0.15
                
<<<<<<< HEAD
                final_score = min(1.0, max(0.0, final_score))
                
                final_results.append({
                    'id': item['id'],
                    'similarity': float(final_score),
                    'content': content_text,
                    'metadata': {'filename': item['filename'], 'source': item['source']},
                    'file_path': item['source'],
                    'filename': item['filename']
                })
            
            final_results.sort(key=lambda x: x['similarity'], reverse=True)
            return final_results[:top_k]
            
=======
                # Cap score at 1.0
                final_score = min(1.0, final_score)
                
                candidates.append({
                    'id': ids[i],
                    'similarity': max(0.0, float(final_score)),
                    'content': content_text,
                    'metadata': metadata,
                    'file_path': metadata.get('source'),
                    'filename': metadata.get('filename', 'Unknown'),
                    'type': metadata.get('type', 'Unknown')
                })

            # Sort by final similarity score
            candidates.sort(key=lambda x: x['similarity'], reverse=True)

            return candidates[:top_k]

>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
        except Exception as e:
            print(f"Search error: {e}")
            return []
            
    def get_stats(self):
<<<<<<< HEAD
        """Get database statistics."""
        count = 0
        if self.table_name in self.db.table_names():
            if self.table is None:
                self.table = self.db.open_table(self.table_name)
            count = len(self.table)
        return {"count": count, "path": self.db_path}
=======
        """
        Return basic collection statistics.
        """
        return {
            "count": self.collection.count(),
            "path": self.db_path
        }
>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
    
    def get_all_ids(self):
        """
        Retrieve all base document IDs (without chunk suffix).
        Useful for incremental indexing.
        """
        try:
<<<<<<< HEAD
            if self.table_name not in self.db.table_names(): return set()
            if self.table is None: self.table = self.db.open_table(self.table_name)
                
            tbl = self.table.search().limit(100000).select(["id"]).to_arrow()
            all_ids = tbl["id"].to_pylist()
            
            file_ids = set()
            for sid in all_ids:
=======
            if self.collection.count() == 0:
                return set()

            result = self.collection.get(include=[]) 
            all_server_ids = result['ids']

            file_ids = set()

            for sid in all_server_ids:
>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
                if '_chunk_' in sid:
                    file_ids.add(sid.split('_chunk_')[0])
                else:
                    file_ids.add(sid)
<<<<<<< HEAD
=======

>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
            return file_ids

        except Exception as e:
            print(f"Error getting IDs: {e}")
            return set()

<<<<<<< HEAD
    def clear(self):
        """Delete the table."""
        try:
            if self.table_name in self.db.table_names():
                self.db.drop_table(self.table_name)
                self.table = None
            print("Index cleared.")
=======
    # --- CLEAN DATABASE LOGIC ---
    def clear_database(self):
        """
        Reset the database safely.

        Strategy:
        1️⃣ Try official client.reset()
        2️⃣ If it fails (Windows lock issue), perform hard folder deletion
        """
        print("Resetting database...")
        
        # Method 1: Official reset
        try:
            self.client.reset()
            print("✅ Database reset via client.reset()")

            # Recreate collection after reset
            self.collection = self.client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
            return True

>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
        except Exception as e:
            print(f"⚠️ Standard reset failed: {e}")
            print("🚀 Attempting nuclear folder deletion...")

        # Method 2: Force deletion
        try:
            # Stop internal system (release file locks)
            if hasattr(self.client, '_system'):
                self.client._system.stop()
            
            # Remove references
            self.client = None
            self.collection = None

            gc.collect()
            time.sleep(1.0)  # Allow OS to release handles
            
            # Delete physical database folder
            if os.path.exists(self.db_path):
                shutil.rmtree(self.db_path)
                print("✅ Physical folder deleted.")
            
            # Rebuild database
            self._init_db()
            return True
            
        except Exception as e:
            print(f"❌ Critical Error during hard clean: {e}")

            # Last fallback: attempt reinitialization
            try:
                self._init_db()
            except:
                pass

            return False