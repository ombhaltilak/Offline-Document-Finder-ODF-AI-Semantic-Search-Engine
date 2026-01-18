"""
Vector Search Engine (LanceDB + GPU Support)
Handles high-performance, disk-based similarity search using LanceDB.
Automatically selects GPU (CUDA) if available, otherwise falls back to CPU.
"""

import lancedb
import os
import time
import importlib.util
from fastembed import TextEmbedding

# --- CONFIGURATION ---
# State-of-the-Art local model.
MODEL_NAME = "mixedbread-ai/mxbai-embed-large-v1" 

class VectorSearch:
    def __init__(self):
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
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + chunk_size
            if end >= text_len:
                chunks.append(text[start:])
                break
            
            # Find a natural break point
            break_point = -1
            for sep in ['\n\n', '\n', '. ', ' ']:
                idx = text.rfind(sep, start, end)
                if idx != -1 and idx > start + (chunk_size // 2):
                    break_point = idx + len(sep)
                    break
            
            if break_point != -1:
                chunks.append(text[start:break_point])
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
            
            count += 1
            if progress_callback:
                progress_callback(count, metadata.get('filename', ''))
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
        except Exception as e:
            print(f"Error writing batch to LanceDB: {e}")

    def search(self, query, top_k=10, filter_metadata=None):
        """Search LanceDB using Hybrid logic (Vector + Keyword Boost)."""
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
                    
                if query_lower in content_text.lower():
                    final_score += 0.15
                    boost_applied = True
                
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
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
            
    def get_stats(self):
        """Get database statistics."""
        count = 0
        if self.table_name in self.db.table_names():
            if self.table is None:
                self.table = self.db.open_table(self.table_name)
            count = len(self.table)
        return {"count": count, "path": self.db_path}
    
    def get_all_ids(self):
        """Get set of all document IDs currently in the index."""
        try:
            if self.table_name not in self.db.table_names(): return set()
            if self.table is None: self.table = self.db.open_table(self.table_name)
                
            tbl = self.table.search().limit(100000).select(["id"]).to_arrow()
            all_ids = tbl["id"].to_pylist()
            
            file_ids = set()
            for sid in all_ids:
                if '_chunk_' in sid:
                    file_ids.add(sid.split('_chunk_')[0])
                else:
                    file_ids.add(sid)
            return file_ids
        except Exception as e:
            print(f"Error getting IDs: {e}")
            return set()

    def clear(self):
        """Delete the table."""
        try:
            if self.table_name in self.db.table_names():
                self.db.drop_table(self.table_name)
                self.table = None
            print("Index cleared.")
        except Exception as e:
            print(f"Error clearing index: {e}")
