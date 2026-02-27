# Offline Document Finder (ODF)

**"Search Like You Think"** – A Local-First, AI-Powered Document Search Engine.

## 🚀 Problem Solved

Traditional file search is broken. It relies on **lexical (keyword) matching**, meaning if you name a file `2024_Fiscal_Review.pdf` and search for "Budget Report", you'll find nothing.

ODF solves this by using **Semantic Search**. It reads your documents, understands the *concepts* inside them (via high-dimensional vector embeddings), and lets you search using natural language.

* **User Intent**: "I need the notes from the meeting about the new marketing strategy."
* **ODF Result**: Finds `Q3_Strategy_v2.docx` (even if the word "marketing" isn't in the filename).

---

## 🏗️ Architecture

ODF is engineered as a **Native Desktop Overlay** utilizing a "Local-First" AI stack. It is designed to be resource-efficient, leveraging disk-based storage to avoid RAM bottlenecks.

### 1. The Frontend (Presentation Layer)

* **Framework**: `CustomTkinter` (Modern UI wrapper).
* **Design System**:
* **Floating Overlay**: Borderless window (`overrideredirect=True`) that sits on top (`-topmost`).
* **Theme**: Ultra-Dark Mode (`#1e1e1e` background) with accessible contrast.
* **Responsiveness**: Asynchronous UI updates via background threading to prevent freezing.


* **Global Access**: Background daemon listens for `Ctrl+K` to toggle visibility instantly over any application.

### 2. The Engine (Ingestion Layer)

* **Parallel Processing**: Uses `ThreadPoolExecutor` to scan directories and read files concurrently.
* **Incremental Indexing**: Implements **MD5 Hashing** (Path + Modification Time).
* *Benefit*: If a file hasn't changed, ODF skips re-reading it, making subsequent syncs instant.


* **Parsers**:
* `pdfminer.six` (High-fidelity PDF text extraction).
* `python-docx` (Word document parsing).
* Recursive Chunking: Splits text into **1000-character segments** (with 100-char overlap) to preserve context.



### 3. The "Brain" (AI & Storage)

* **Inference Engine**: `ONNX Runtime` via `FastEmbed`.
* **Hardware Aware**: Automatically detects NVIDIA GPUs. If found, it switches to `CUDAExecutionProvider` for massive speedups (4x-10x). If not, it falls back to optimized CPU inference.


* **Embedding Model**: `Mixedbread AI (mxbai-embed-large-v1)`.
* **Specs**: 335M parameters, **1024 dimensions**.
* *Why?* Much deeper semantic understanding than standard 384-dim models.


* **Vector Database**: `LanceDB` (Disk-Based Vector Store).
* **Zero-Copy Access**: Stores vectors on the SSD/HDD using Apache Arrow format, meaning it **does not** load the entire index into RAM. This solves the memory crash issues common with FAISS.



---

## 🧠 Hybrid Retrieval Logic

ODF doesn't just trust the AI blindly. It uses a **Hybrid Ranking Algorithm** to balance conceptual understanding with exact precision.

### The Workflow:

1. **Semantic Retrieval**:
* The user's query is vectorized (converted to numbers).
* LanceDB retrieves the **Top-30** conceptually similar candidates using Cosine Similarity.


2. **Lexical Boosting (Re-Ranking)**:
* The system scans these 30 candidates for exact keywords.
* **Filename Match**: Adds **+0.25** to the score (Strong boost).
* **Content Match**: Adds **+0.15** to the score (Moderate boost).


3. **Final Sort**: The list is re-ordered based on the boosted scores, and the **Top-10** are displayed.

**Why?**

* Searching *"Invoice"* (Concept) finds `Billing_Statement.pdf`.
* Searching *"INV-2024-001"* (Specific ID) forces that exact file to the top, even if the AI thinks another file is "conceptually" similar.

---

## 🔒 Privacy & Performance

* **100% Offline**: No data leaves your machine. No API keys required.
* **Disk-Based Storage**: Unlike in-memory databases that eat RAM, LanceDB keeps the footprint low (~150MB RAM even with thousands of docs).
* **Hardware Acceleration**: Utilizes NVIDIA CUDA cores for ingestion if available, making indexing significantly faster.

---

## 🛠️ Installation & Usage

### Prerequisites

* Python 3.10+
* (Optional) NVIDIA GPU with CUDA Toolkit installed

### Setup

1. **Clone the Repo**:
```bash
git clone https://github.com/yourusername/odf.git
cd odf

```


2. **Install Dependencies**:
```bash
pip install -r requirements.txt

```


3. **Run the App**:
```bash
python main.py

```



### How to Use

1. **Toggle**: Press **Ctrl+K** anywhere to open the search bar.
2. **Index**: Click the **"Index"** button and select a folder (e.g., `Documents/Work`). Watch the progress bar as it processes.
3. **Search**: Type natural queries (e.g., *"How do I fix the server error?"*).
4. **Open**: Click any result to open the file instantly.

---

*Powered by [LanceDB](https://lancedb.com/), [ONNX Runtime](https://onnxruntime.ai/), and [FastEmbed](https://qdrant.github.io/fastembed/).*
