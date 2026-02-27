# 🔍 Offline Document Finder (ODF)

> **Search Like You Think — 100% Offline AI Document Search**

Offline Document Finder (ODF) is a local-first, AI-powered desktop application that enables semantic search across your personal documents.

Instead of relying only on filenames or exact keyword matches, ODF understands the **meaning** of your content using vector embeddings and retrieves results intelligently.

---

## 🚀 The Problem ODF Solves

Traditional file search:

- Matches exact words only  
- Fails when filenames don’t contain your search term  
- Cannot understand context  

ODF:

- Understands semantic meaning  
- Converts documents into vector embeddings  
- Uses similarity-based retrieval  
- Works entirely offline  

### Example

Search:

> meeting notes about marketing strategy  

ODF can return:

> Q3_Strategy_v2.docx  

—even if the word *“marketing”* does not appear in the filename.

---

## 🧠 Core Technologies

ODF combines modern AI tools with a lightweight desktop interface.

### 🔹 ChromaDB (Local Vector Database)

Used to store document embeddings persistently.

- Disk-based storage  
- Fast similarity search  
- No RAM-heavy in-memory indexing  

Embeddings are stored locally in:

```
data/chroma_db/
```

---

### 🔹 Semantic Embeddings

- Documents are converted into high-dimensional numeric vectors  
- User queries are converted into vectors  
- Similarity scoring retrieves the most relevant results  

---

### 🔹 Desktop UI (Tkinter-Based)

- Lightweight Python GUI  
- Native desktop window  
- Minimal system resource usage  

---

### 🔹 Global Hotkey Support

Registered using the `keyboard` Python library.

```
Ctrl + K
```

Press it from anywhere to instantly toggle the search window.

---

## 🏗️ System Architecture

### 1️⃣ Application Startup

When `main.py` runs:

1. Ensures a local `models/` directory exists  
2. Initializes the `SearchWindow`  
3. Registers global hotkey (`Ctrl + K`)  
4. Starts the Tkinter main event loop  
5. Runs until manually closed  

---

### 2️⃣ Document Indexing Flow

1. User selects a folder  
2. Documents are read  
3. Text is extracted  
4. Content is chunked (if enabled)  
5. Each chunk is converted into embeddings  
6. Embeddings are stored in ChromaDB  

---

### 3️⃣ Search Flow

1. User enters a natural language query  
2. Query is converted into an embedding  
3. ChromaDB performs similarity search  
4. Top results are returned  
5. User clicks a result to open the file  

---

## 🔒 Privacy & Security

ODF follows strict privacy-first principles:

- ✅ 100% Offline  
- ✅ No cloud APIs  
- ✅ No data collection  
- ✅ No tracking  
- ✅ No external servers  
- ✅ No API keys required  

Your files never leave your machine.

---

## ⚡ Features

- 🔎 Semantic document search  
- 🧠 AI-powered understanding  
- 💾 Local vector storage (ChromaDB)  
- ⚡ Global hotkey access  
- 📂 Folder indexing  
- 🖱️ Click-to-open results  
- 🪶 Lightweight & fast  
- 🔒 Fully offline  

---

## 📦 Installation Guide

### Requirements

- Python 3.10+  
- Windows (recommended for global hotkey support)  

---

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/ombhaltilak/Offline-Document-Finder-ODF-AI-Semantic-Search-Engine.git
cd Offline-Document-Finder-ODF-AI-Semantic-Search-Engine
```

---

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

If hotkey registration fails, run your terminal as **Administrator**.

---

### 3️⃣ Run the Application

```bash
python main.py
```

---

## 📂 How To Use

1. Start the application  
2. Press **Ctrl + K**  
3. Click **Index** and select your document folder  
4. Wait for indexing to complete  
5. Search using natural language  
6. Click a result to open the file  

---

## 📁 Project Structure

```
Offline-Document-Finder/
│
├── main.py
├── data/
│   └── chroma_db/
├── models/
├── ui/
│   └── search_window.py
├── requirements.txt
└── README.md
```

---

## 🧾 Git Ignore Rules

The following are intentionally ignored:

- `data/`
- `*.sqlite3`
- `models/`
- `__pycache__/`
- `venv/`

These files are generated locally and should not be pushed to GitHub.

---

## 🛣️ Future Improvements

- macOS & Linux hotkey support  
- System tray integration  
- Standalone executable build (.exe)  
- Faster indexing pipeline  
- Advanced ranking algorithm  
- Background auto-sync  
- File preview panel  

---

## 👨‍💻 Author

**Om bhaltilak**  
AI + Systems Engineering Project  

---

## 💡 Vision

ODF aims to bring private, local AI search to everyday users — without relying on cloud infrastructure.

> **Search Like You Think.**
