<<<<<<< HEAD
=======
"""
Offline Document Finder - Main UI

This module:
- Builds the CustomTkinter GUI
- Handles user search interactions
- Connects indexing system with vector search
- Displays ranked results with preview and similarity score
- Manages indexing progress and database reset
"""

>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
import hashlib
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import sys
from PIL import Image

# Backend imports
from search_engine.vector_search import VectorSearch
from search_engine.file_indexer import FileIndexer
from utils.open_file import open_file


# ---------------------------------------------------------
# THEME CONFIGURATION (Dark Modern UI)
# ---------------------------------------------------------
THEME = {
<<<<<<< HEAD
    "bg": "#0d0d0d",           # Ultra Dark
    "card": "#1a1a1a",         # Slightly lighter for contrast
    "card_hover": "#252525",   # Hover Grey
    "border": "#444444",       # Light Border for visibility
    "accent": "#3B8ED0",       # Electric Blue
=======
    "bg": "#0d0d0d",           # Ultra Dark Background
    "card": "#1a1a1a",         # Card Background
    "card_hover": "#252525",   # Hover Effect
    "border": "#444444",       # Card Border
    "accent": "#3B8ED0",       # Primary Accent Color
>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
    "text_primary": "#FFFFFF",
    "text_secondary": "#808080",
    "danger": "#C42B1C"        # Danger / Reset Button Color
}

# Force Dark Mode
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


<<<<<<< HEAD
# -------------------- CUSTOM WIDGETS --------------------
class CircularProgress(tk.Canvas):
=======
# ---------------------------------------------------------
# CUSTOM CIRCULAR PROGRESS WIDGET
# ---------------------------------------------------------
class CircularProgress(tk.Canvas):
    """
    Custom circular progress indicator.
    Used during folder indexing.
    """

>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
    def __init__(self, master, size=45, bg_color=THEME["bg"],
                 fg_color=THEME["accent"], track_color="#333333"):
        super().__init__(
            master,
            width=size,
            height=size,
            bg=bg_color,
            highlightthickness=0
        )
<<<<<<< HEAD
=======

        # Visual configuration
>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
        self.size = size
        self.fg_color = fg_color
        self.track_color = track_color
        self.percentage = 0
<<<<<<< HEAD
        self.center = size / 2
        self.radius = (size - 8) / 2
        self.stroke_width = 5
        self.draw()

    def set(self, value):
=======

        # Geometry helpers
        self.center = size / 2
        self.radius = (size - 8) / 2
        self.stroke_width = 5

        self.draw()

    def set(self, value):
        """Update progress value (0.0 to 1.0)."""
>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
        self.percentage = max(0.0, min(value, 1.0))
        self.draw()

    def draw(self):
<<<<<<< HEAD
        self.delete("all")

        # Background Track
=======
        """Redraw circular progress."""
        self.delete("all")

        # Background track
>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
        self.create_oval(
            self.center - self.radius, self.center - self.radius,
            self.center + self.radius, self.center + self.radius,
            outline="#2b2b2b", width=self.stroke_width
        )

<<<<<<< HEAD
        # Progress Arc
=======
        # Foreground progress arc
>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
        if self.percentage >= 1.0:
            self.create_oval(
                self.center - self.radius, self.center - self.radius,
                self.center + self.radius, self.center + self.radius,
                outline="#3B8ED0", width=self.stroke_width
            )
        elif self.percentage > 0:
            angle = -360 * self.percentage
            self.create_arc(
                self.center - self.radius, self.center - self.radius,
                self.center + self.radius, self.center + self.radius,
                start=90, extent=angle, style="arc",
                outline="#3B8ED0", width=self.stroke_width
            )

<<<<<<< HEAD
        # Percentage Text
=======
        # Percentage text
>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
        text_content = f"{int(self.percentage * 100)}%"
        self.create_text(
            self.center, self.center,
            text=text_content, fill="white",
            font=("Segoe UI", 10, "bold")
        )


<<<<<<< HEAD
# -------------------- MAIN WINDOW --------------------
=======
# ---------------------------------------------------------
# MAIN APPLICATION WINDOW
# ---------------------------------------------------------
>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
class SearchWindow:
    """
    Main application window for Offline Document Finder.

    Responsibilities:
    - Manage UI lifecycle
    - Trigger search queries
    - Display ranked results
    - Handle indexing operations
    - Manage database reset
    """

    WIDTH = 800
    INITIAL_HEIGHT = 160
    MAX_HEIGHT = 700

    def __init__(self):
        self.root = None

        # Backend systems
        self.vector_search = VectorSearch()
        self.file_indexer = FileIndexer()
<<<<<<< HEAD
        self.results = []
        self.selected_index = -1

    # -------------------- WINDOW LOGIC --------------------
=======

        # Search state
        self.results = []
        self.selected_index = -1

    # ---------------------------------------------------------
    # WINDOW VISIBILITY LOGIC
    # ---------------------------------------------------------
>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
    def toggle_window(self):
        if not self.root:
            self.show_window()
        elif self.root.state() in ('withdrawn', 'iconic'):
            self.show_window()
        else:
            self.root.withdraw()

    def show_window(self):
        """Show or restore main window."""
        if not self.root:
            self._create_window()
        else:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            self.search_entry.focus_set()
<<<<<<< HEAD
=======

        # Check if DB is empty after showing window
>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
        self.root.after(400, self._check_empty_db)

    def _create_window(self):
        """Initialize and build UI layout."""
        self.root = ctk.CTk()
        self.root.overrideredirect(False)
        self.root.title("Offline Document Finder")
        self.root.attributes("-topmost", False)
        self.root.configure(fg_color=THEME["bg"])
        self.root.resizable(True, True)
        self._center()

        # Main container
        self.main = ctk.CTkFrame(
            self.root,
            corner_radius=0,
            fg_color=THEME["bg"],
            border_width=0
        )
        self.main.pack(fill="both", expand=True)

        self._build_search_bar()
        self._build_results()
        self._build_footer()
        self._bind_keys()
<<<<<<< HEAD
        self.root.protocol("WM_DELETE_WINDOW", self.root.withdraw)
=======

        # Fully close app on window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        """
        Forcefully terminate application.
        Ensures background threads are stopped.
        """
        try:
            if self.root:
                self.root.quit()
                self.root.destroy()
        except Exception as e:
            print(f"Error closing: {e}")

        os._exit(0)
>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)

    def _center(self):
        """Center window on screen."""
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        x = (sw - self.WIDTH) // 2
        y = sh // 4
        self.root.geometry(f"{self.WIDTH}x{self.INITIAL_HEIGHT}+{x}+{y}")

    # ---------------------------------------------------------
    # SEARCH BAR UI
    # ---------------------------------------------------------
    def _build_search_bar(self):
        """Create search input bar and button."""
        bar = ctk.CTkFrame(self.main, fg_color="transparent")
        bar.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(bar, text="🔍", font=("Segoe UI", 22)).pack(side="left", padx=(4, 12))

        self.query = tk.StringVar()

        self.search_entry = ctk.CTkEntry(
            bar,
            textvariable=self.query,
            font=("Segoe UI", 18),
            height=48,
            fg_color=THEME["card"],
            border_width=1,
            border_color=THEME["border"],
            corner_radius=8,
            placeholder_text="Search documents..."
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.focus()

<<<<<<< HEAD
        # --- NEW: Submit Button ---
=======
        # Manual search trigger button
>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
        self.btn_search = ctk.CTkButton(
            bar,
            text="Search",
            fg_color=THEME["accent"],
            text_color="#000",
            corner_radius=8,
            width=100,
            command=self._on_search_click
        )
        self.btn_search.pack(side="left")

<<<<<<< HEAD
    # -------------------- SEARCH TRIGGER --------------------
    def _on_search_click(self):
=======
    # ---------------------------------------------------------
    # SEARCH LOGIC
    # ---------------------------------------------------------
    def _on_search_click(self):
        """Validate and trigger search."""
>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
        q = self.query.get().strip()
        if not q:
            self.status.configure(text="Please enter a search term.")
            return
        self._search(q)

<<<<<<< HEAD
    # -------------------- SEARCH EXECUTION --------------------
    def _search(self, query):
        def task():
            # Limit results to top 10
            res = self.vector_search.search(query, top_k=10)
            self.root.after(0, lambda: self._render_results(res))
        threading.Thread(target=task, daemon=True).start()

    # -------------------- RENDER RESULTS --------------------
=======
    def _search(self, query):
        """
        Execute semantic search in background thread.
        - Fetches top 50 chunks
        - Deduplicates by filename
        - Displays top 10 unique files
        """
        self.status.configure(text="Searching...")

        def task():
            raw_results = self.vector_search.search(query, top_k=50)

            # Deduplicate by filename
            unique_results = []
            seen_files = set()

            for res in raw_results:
                fname = res.get("filename", "unknown")
                if fname not in seen_files:
                    unique_results.append(res)
                    seen_files.add(fname)

            final_results = unique_results[:10]

            self.root.after(0, lambda: self._render_results(final_results))

        threading.Thread(target=task, daemon=True).start()

    # ---------------------------------------------------------
    # RESULTS DISPLAY
    # ---------------------------------------------------------
>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
    def _build_results(self):
        """Initialize result container."""
        self.separator = ctk.CTkFrame(self.main, height=1, fg_color=THEME["border"])
        self.results_view = ctk.CTkScrollableFrame(
            self.main,
            fg_color="transparent",
            corner_radius=0
        )

<<<<<<< HEAD
    def _show_results(self):
        self.separator.pack(fill="x", padx=20, pady=10)
        self.results_view.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def _hide_results(self):
        self.separator.pack_forget()
        self.results_view.pack_forget()
        if self.root.state() != 'zoomed':
            self._animate_height(self.INITIAL_HEIGHT)

=======
>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
    def _render_results(self, results):
        """Render result cards."""
        for w in self.results_view.winfo_children():
            w.destroy()
        self.results = results
        self.selected_index = -1

        if not results:
            self.status.configure(text="No results found.")
            self._hide_results()
            return

        self._show_results()
<<<<<<< HEAD
        for i, r in enumerate(results[:10]):  # show only first 10
=======

        for i, r in enumerate(results[:10]):
>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
            self._create_card(i, r)

        if self.root.state() != 'zoomed':
            height = min(self.MAX_HEIGHT, self.INITIAL_HEIGHT + len(results[:10]) * 85)
            self._animate_height(height)
<<<<<<< HEAD

        self.status.configure(text=f"Showing {len(results[:10])} results")

    # -------------------- RESULT CARD --------------------
    def _create_card(self, index, res):
        frame = ctk.CTkFrame(
            self.results_view,
            fg_color=THEME["card"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"]
        )
        frame.pack(fill="x", pady=6)

        icon = "📄"
        ext = os.path.splitext(res.get("filename", "file"))[1].lower()
        if ext == ".pdf":
            icon = "📕"
        elif ext == ".docx":
            icon = "📘"
        elif ext == ".txt":
            icon = "📝"

        ctk.CTkLabel(frame, text=icon, font=("Segoe UI", 22)).pack(side="left", padx=12)

        body = ctk.CTkFrame(frame, fg_color="transparent")
        body.pack(side="left", fill="x", expand=True, pady=8)

        ctk.CTkLabel(
            body,
            text=res.get("filename", "Unknown"),
            font=("Segoe UI", 14, "bold"),
            text_color=THEME["accent"],
            anchor="w"
        ).pack(fill="x")

        content = res.get("content", "")
        preview_text = content[:200].replace("\n", " ") + "..."
        if not content.strip():
            preview_text = "No text content found."

        ctk.CTkLabel(
            body,
            text=preview_text,
            font=("Segoe UI", 11),
            text_color=THEME["text_secondary"],
            anchor="w",
            wraplength=600
        ).pack(fill="x")

        score = int(res.get("similarity", 0) * 100)
        ctk.CTkLabel(
            frame,
            text=f"{score}%",
            fg_color=THEME["accent"],
            text_color="#000",
            corner_radius=12,
            width=48
        ).pack(side="right", padx=12)

        # Bindings
        frame.bind("<Enter>", lambda e: frame.configure(fg_color=THEME["card_hover"], border_color=THEME["accent"]))
        frame.bind("<Leave>", lambda e: frame.configure(fg_color=THEME["card"], border_color=THEME["border"]))
        click_handler = lambda e: open_file(res.get("file_path", ""))
        frame.bind("<Button-1>", click_handler)
        for child in frame.winfo_children():
            if not isinstance(child, ctk.CTkButton):
                child.bind("<Button-1>", click_handler)
        for child in body.winfo_children():
            child.bind("<Button-1>", click_handler)

    # -------------------- FOOTER --------------------
    def _build_footer(self):
        self.footer = ctk.CTkFrame(self.main, fg_color="transparent")
        self.footer.pack(fill="x", padx=20, pady=(0, 20), side="bottom")

        self.status = ctk.CTkLabel(
            self.footer,
            text="Ready",
            font=("Segoe UI", 12),
            text_color=THEME["text_secondary"]
        )
        self.status.pack(side="left", pady=5)

        self.progress_donut = CircularProgress(
            self.footer,
            size=40,
            bg_color=THEME["bg"]
        )

        self.btn_index = ctk.CTkButton(
            self.footer,
            text="📁 Index Folder",
            command=self._browse_folder,
            fg_color="#2a2a2a",
            width=120,
            height=30
        )
        self.btn_index.pack(side="right", padx=0, pady=5)

    # -------------------- KEYBOARD NAV --------------------
    def _bind_keys(self):
        self.root.bind("<Escape>", lambda e: self.root.withdraw())
        self.root.bind("<Return>", lambda e: self._on_search_click())  # NEW: Enter triggers Search
        self.root.bind("<Down>", self._select_next)
        self.root.bind("<Up>", self._select_prev)

    def _select_next(self, _=None):
        self._select(min(self.selected_index + 1, len(self.results) - 1))

    def _select_prev(self, _=None):
        self._select(max(self.selected_index - 1, 0))

    def _select(self, index):
        children = self.results_view.winfo_children()
        if 0 <= self.selected_index < len(children):
            children[self.selected_index].configure(fg_color=THEME["card"], border_color=THEME["border"])
        self.selected_index = index
        if 0 <= index < len(children):
            children[index].configure(fg_color=THEME["card_hover"], border_color=THEME["accent"])
            self.results_view._parent_canvas.yview_moveto(index / len(children))

    def _open_selected(self, _=None):
        if 0 <= self.selected_index < len(self.results):
            open_file(self.results[self.selected_index]["file_path"])

    # -------------------- ANIMATION --------------------
    def _animate_height(self, target):
        if self.root.state() == 'zoomed':
            return
        cur = self.root.winfo_height()
        step = 20 if target > cur else -20

        def run():
            nonlocal cur
            if (step > 0 and cur < target) or (step < 0 and cur > target):
                cur += step
                self.root.geometry(f"{self.WIDTH}x{cur}")
                self.root.after(5, run)
        run()

    # -------------------- INDEXING --------------------
=======

        self.status.configure(text=f"Showing {len(results[:10])} results")

    # ---------------------------------------------------------
    # INDEXING SYSTEM
    # ---------------------------------------------------------
>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
    def _browse_folder(self):
        """Prompt user to select folder for indexing."""
        folder = filedialog.askdirectory()
        if not folder:
            return
<<<<<<< HEAD
        self.status.pack_forget()
        self.progress_donut.pack(side="left", padx=10)
        self.progress_donut.set(0)
        threading.Thread(target=self._index_thread, args=(folder,), daemon=True).start()

    def _index_thread(self, folder):
        try:
            files = self.file_indexer.scan_directory(folder)
            total = len(files)
            if total == 0:
                self.root.after(0, lambda: self.status.configure(text="No supported files found."))
                self.root.after(1500, self._reset_footer)
                return

            existing_ids = self.vector_search.get_all_ids()
            new_files = []
            skipped_count = 0
            self.root.after(0, lambda: self.status.configure(text="Checking file status..."))
            last_update_pct = 0.0

            for i, f in enumerate(files):
                try:
                    stats = os.stat(f)
                    doc_id = hashlib.md5(f"{f}_{stats.st_mtime}".encode()).hexdigest()
                    if doc_id in existing_ids:
                        skipped_count += 1
                    else:
                        new_files.append(f)

                    current_progress = (i + 1) / total
                    if current_progress - last_update_pct >= 0.01:
                        self.root.after(0, lambda p=current_progress: self.progress_donut.set(p))
                        last_update_pct = current_progress
                except Exception:
                    new_files.append(f)

            final_skipped_pct = skipped_count / total
            self.root.after(0, lambda: self.progress_donut.set(final_skipped_pct))

            if not new_files:
                self.root.after(0, lambda: self.progress_donut.set(1.0))
                self.root.after(0, lambda: self.status.configure(text="All files up to date."))
                self.root.after(1500, self._reset_footer)
                return

            self.root.after(0, lambda: self.status.configure(text=f"Indexing {len(new_files)} new files..."))

            def progress_callback(i, name):
                current_total = skipped_count + i
                pct = current_total / total
                self.root.after(0, lambda: self.progress_donut.set(pct))

            gen = self.file_indexer.process_files(new_files, existing_ids=existing_ids)
            self.vector_search.add_documents(gen, progress_callback=progress_callback)

            self.root.after(0, lambda: self.progress_donut.set(1.0))
            self.root.after(0, lambda: self.status.configure(text=f"Indexed {len(new_files)} new files."))

        except Exception as e:
            print(f"Indexing error: {e}")
            self.root.after(0, lambda: self.status.configure(text="Error during indexing."))
        finally:
            self.root.after(2000, self._reset_footer)

    def _reset_footer(self):
        self.progress_donut.pack_forget()
        self.status.pack(side="left", pady=5)

    def _check_empty_db(self):
=======

        self.status.pack_forget()
        self.progress_donut.pack(side="left", padx=10)
        self.progress_donut.set(0)

        threading.Thread(target=self._index_thread, args=(folder,), daemon=True).start()

    def _index_thread(self, folder):
        """
        Background indexing process:
        - Scan files
        - Skip unchanged files
        - Embed and store new documents
        - Update circular progress UI
        """
>>>>>>> 2798949 (Initial commit - ODF AI Semantic Search Engine)
        try:
            files = self.file_indexer.scan_directory(folder)
            total = len(files)

            if total == 0:
                self.root.after(0, lambda: self.status.configure(text="No supported files found."))
                self.root.after(1500, self._reset_footer)
                return

            existing_ids = self.vector_search.get_all_ids()
            new_files = []
            skipped_count = 0

            self.root.after(0, lambda: self.status.configure(text="Checking file status..."))

            for f in files:
                try:
                    stats = os.stat(f)
                    doc_id = hashlib.md5(f"{f}_{stats.st_mtime}".encode()).hexdigest()

                    if doc_id in existing_ids:
                        skipped_count += 1
                    else:
                        new_files.append(f)

                except Exception:
                    new_files.append(f)

            if not new_files:
                self.root.after(0, lambda: self.status.configure(text="All files up to date."))
                self.root.after(1500, self._reset_footer)
                return

            gen = self.file_indexer.process_files(new_files, existing_ids=existing_ids)
            self.vector_search.add_documents(gen)

            self.root.after(0, lambda: self.status.configure(text=f"Indexed {len(new_files)} new files."))

        except Exception as e:
            print(f"Indexing error: {e}")
            self.root.after(0, lambda: self.status.configure(text="Error during indexing."))
        finally:
            self.root.after(2000, self._reset_footer)

    # ---------------------------------------------------------
    # DATABASE RESET
    # ---------------------------------------------------------
    def _on_reset_click(self):
        """
        Delete all indexed documents after confirmation.
        Calls backend clear_database().
        """
        if messagebox.askyesno("Reset Index", "Are you sure you want to delete all indexed documents?\nThis action cannot be undone."):
            try:
                for w in self.results_view.winfo_children():
                    w.destroy()

                self.results = []
                self.status.configure(text="Clearing database...")

                if hasattr(self.vector_search, 'clear_database'):
                    success = self.vector_search.clear_database()

                    if success:
                        self.status.configure(text="Database cleared.")
                        messagebox.showinfo("Success", "All indexed documents have been removed.")
                    else:
                        self.status.configure(text="Error clearing DB.")
                        messagebox.showerror("Error", "Failed to clear database.")
                else:
                    messagebox.showerror("Error", "Backend is outdated. Add clear_database().")

            except Exception as e:
                print(f"Error resetting: {e}")
                messagebox.showerror("Error", f"Unexpected error: {e}")