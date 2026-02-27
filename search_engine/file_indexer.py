"""
File Indexer
Scans folders and extracts content from PDF, DOCX, TXT, and EXE files using parallel processing.

This module:
- Recursively scans directories
- Extracts searchable text from supported file types
- Skips system and unnecessary folders
- Uses parallel processing for high performance
- Generates unique document IDs for incremental indexing
"""

import os
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
# from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document
import re
from tqdm import tqdm
import logging
import fitz
import openpyxl

# Suppress annoying PDFMiner warnings (even though we use PyMuPDF now)
logging.getLogger("pdfminer").setLevel(logging.ERROR)


class FileIndexer:
    def __init__(self):
        """Initialize the file indexer."""
        
        # Supported file extensions for indexing.
        # Added support for:
        # - .exe (binary string extraction)
        # - .xlsx / .xls (Excel files)
        self.supported_extensions = {'.pdf', '.docx', '.txt', '.exe', '.xlsx', '.xls'}
        
        # Windows system folders to skip during scanning.
        # Prevents permission errors and unnecessary indexing.
        self.system_folders = {
            'C:\\WINDOWS',
            'C:\\PROGRAM FILES',
            'C:\\PROGRAM FILES (X86)',
            'C:\\SYSTEM32',
            'C:\\PROGRAMDATA',
            'C:\\USERS\\DEFAULT',
            'C:\\BOOT',
            'C:\\RECOVERY'
        }
    
    def scan_directory(self, folder_path):
        """
        Recursively scans a directory and returns a list of supported files.

        - Skips unwanted folders
        - Filters files based on supported extensions
        """
        if not os.path.exists(folder_path):
            raise ValueError(f"Folder does not exist: {folder_path}")
            
        all_files = []
        
        # Walk through directory tree
        for root, dirs, files in os.walk(folder_path):
            
            # Filter directories in-place to skip unwanted/system folders
            dirs[:] = [d for d in dirs if not self._should_skip_folder(os.path.join(root, d))]
            
            for file in files:
                _, ext = os.path.splitext(file.lower())
                
                # Only collect supported file types
                if ext in self.supported_extensions:
                    all_files.append(os.path.join(root, file))
                    
        print(f"Found {len(all_files)} supported files to scan.")
        return all_files

    def process_files(self, file_paths, existing_ids=None):
        """
        Process files in parallel and yield indexed documents.

        - Skips already indexed files (based on ID)
        - Uses ThreadPoolExecutor for I/O-bound parallelism
        - Yields processed document dictionaries
        """
        if existing_ids is None:
            existing_ids = set()
            
        print(f"Processing {len(file_paths)} files with {len(existing_ids)} existing IDs...")
        
        files_to_process = []
        skipped_count = 0
        
        # Pre-check files to avoid reprocessing unchanged files
        for f in file_paths:
            try:
                # Generate unique ID using file path + last modified time
                file_stats = os.stat(f)
                doc_id = hashlib.md5(f"{f}_{file_stats.st_mtime}".encode()).hexdigest()
                
                # Skip if already indexed
                if doc_id in existing_ids:
                    skipped_count += 1
                    continue
                
                files_to_process.append(f)
            except:
                continue
                
        print(f"Skipping {skipped_count} already indexed files. Processing {len(files_to_process)} new/modified files.")

        # ThreadPoolExecutor is ideal for file I/O operations
        with ThreadPoolExecutor(max_workers=min(32, (os.cpu_count() or 1) * 4)) as executor:
            
            # Submit all file processing tasks
            future_to_file = {
                executor.submit(self._process_single_path_independent, f): f
                for f in files_to_process
            }
            
            # Collect completed tasks
            for future in as_completed(future_to_file):
                try:
                    result = future.result()
                    if result:
                        yield result
                except Exception:
                    # Prevent one failure from stopping the whole indexing process
                    pass

    def _process_single_path_independent(self, file_path):
        """
        Process a single file:
        - Extract text content
        - Generate unique ID
        - Return structured document dictionary
        """
        try:
            _, ext = os.path.splitext(file_path.lower())
            
            # Extract file content based on extension
            content = self._extract_content(file_path, ext)
            
            # If file has no extractable content,
            # use filename so it remains searchable
            if not content or not content.strip():
                content = os.path.basename(file_path)
                
            file_stats = os.stat(file_path)
            
            # Unique document ID based on path + modification time
            doc_id = hashlib.md5(f"{file_path}_{file_stats.st_mtime}".encode()).hexdigest()
            
            return {
                "id": doc_id,
                "content": content,
                "metadata": {
                    "source": file_path,
                    "filename": os.path.basename(file_path),
                    "modified": file_stats.st_mtime,
                    "size": file_stats.st_size,
                    "type": ext
                }
            }
        except Exception:
            return None

    def _extract_content(self, file_path, extension):
        """
        Route content extraction to the correct handler
        based on file extension.
        """
        if extension == '.txt':
            return self._extract_txt_content(file_path)
        elif extension == '.pdf':
            return self._extract_pdf_content(file_path)
        elif extension == '.docx':
            return self._extract_docx_content(file_path)
        elif extension == '.exe':
            return self._extract_exe_content(file_path)
        elif extension in {'.xlsx', '.xls'}:
            return self._extract_excel_content(file_path)
        return ""
    
    # --- EXE EXTRACTOR ---
    def _extract_exe_content(self, file_path):
        """
        Extract readable ASCII strings from binary files (.exe).

        - Does NOT execute the file
        - Reads first 2MB only for performance
        - Extracts printable character sequences
        - Cleans and limits output size
        """
        try:
            min_length = 4  # Minimum string length to consider meaningful
            
            with open(file_path, 'rb') as f:
                # Read first 2MB only (metadata is usually near beginning)
                data = f.read(2 * 1024 * 1024) 
                
                # Find sequences of printable ASCII characters
                strings = re.findall(b'[ -~]{4,}', data)
                
                # Decode bytes to UTF-8 safely
                text = " ".join([s.decode('utf-8', 'ignore') for s in strings])
                
                # Limit size to avoid indexing excessive garbage
                return self._clean_text(text[:5000])
        except:
            return ""
    # --------------------------

    def _extract_txt_content(self, file_path):
        """
        Extract text from TXT files using multiple encoding attempts.
        """
        encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    return self._clean_text(file.read())
            except:
                continue
        return ""
    
    def _extract_pdf_content(self, file_path):
        """
        Extract text from PDF using PyMuPDF (fitz).

        - Much faster than PDFMiner
        - Reads page by page
        """
        try:
            text_content = []
            
            with fitz.open(file_path) as doc:
                for page in doc:
                    text_content.append(page.get_text())
            
            return self._clean_text("\n".join(text_content))
        except:
            return ""
    
    def _extract_docx_content(self, file_path):
        """
        Extract text from DOCX files including:
        - Paragraphs
        - Table cell contents
        """
        try:
            doc = Document(file_path)
            full_text = []
            
            for paragraph in doc.paragraphs:
                full_text.append(paragraph.text)
            
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        full_text.append(cell.text)
                        
            return self._clean_text('\n'.join(full_text))
        except:
            return ""

    def _extract_excel_content(self, file_path):
        """
        Extract text from all sheets and cells in Excel files.

        - Uses read_only mode for performance
        - Extracts computed values (not formulas)
        """
        try:
            wb = openpyxl.load_workbook(file_path, data_only=True, read_only=True)
            content_parts = []
        
            for sheet in wb.worksheets:
                content_parts.append(f"Sheet: {sheet.title}")
                
                for row in sheet.iter_rows(values_only=True):
                    row_data = " ".join([str(cell) for cell in row if cell is not None])
                    if row_data.strip():
                        content_parts.append(row_data)
        
            full_text = "\n".join(content_parts)
            return self._clean_text(full_text)
        except:
            return ""

    def _clean_text(self, text):
        """
        Clean extracted text:
        - Remove excessive whitespace
        - Remove control characters
        - Limit maximum size (100k chars)
        """
        if not text:
            return ""
        
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        return text.strip()[:100000]

    def _should_skip_folder(self, folder_path):
        """
        Determine whether a folder should be skipped.

        Skips:
        - Hidden folders
        - Virtual environments
        - Dependency folders
        - Windows system folders
        """
        if not folder_path:
            return False
        
        name = os.path.basename(folder_path)
        
        # Skip hidden folders (e.g., .git)
        if name.startswith('.'):
            return True
            
        ignore_names = {
            'node_modules', 'site-packages', 'dist-info', '__pycache__', 
            'venv', 'env', 'odf_env', 'libs', 'include', 'scripts', 'bin', 'obj'
        }
        
        if name.lower() in ignore_names:
            return True
            
        # Normalize path for case-insensitive comparison (Windows)
        norm_path = os.path.normpath(folder_path.upper())
        
        # Skip known system folders
        for sys in self.system_folders:
            if norm_path.startswith(sys):
                return True
                
        return False