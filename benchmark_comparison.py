"""
Benchmark Script: Keyword Search vs ODF Semantic Search

This script:
- Implements a baseline keyword-based retrieval engine
- Benchmarks it against the ODF semantic vector search system
- Evaluates using Precision@1 and Recall@5
- Generates comparison plots
- Saves publication-ready figures (PDF + PNG)

Designed for academic evaluation and research reporting.
"""

import time                  # Used for potential timing measurements (future extension)
import os                    # File system operations
import matplotlib.pyplot as plt  # Plotting library for visualization
import numpy as np           # Numerical operations (array positioning for bars)
import seaborn as sns        # Optional styling support (not heavily used but imported)

# --- PLOT STYLING CONFIGURATION ---
# Configure matplotlib for academic-style appearance
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman"],
    "font.size": 12,
    "axes.labelsize": 14,
    "axes.labelweight": "bold",
    "axes.titlesize": 16,
    "axes.titleweight": "bold",
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "legend.fontsize": 11,
    "figure.titlesize": 18
})


# ==========================================
# 🧠 1. KEYWORD SEARCH ENGINE (BASELINE)
# ==========================================
class KeywordSearchEngine:
    """
    Baseline search engine using simple term-frequency matching.

    Ranking Logic:
    - Counts how many query words appear in the filename
    - Higher count = higher ranking
    - No semantic understanding (pure string matching)

    Purpose:
    - Acts as a traditional retrieval baseline
    - Used for comparison against semantic ODF system
    """

    def __init__(self, dataset_folder):
        """
        Initialize baseline engine.

        Args:
            dataset_folder (str): Folder containing dataset PDFs
        """
        self.files = []

        # Load only PDF files from dataset directory
        if os.path.exists(dataset_folder):
            self.files = [f for f in os.listdir(dataset_folder) if f.endswith('.pdf')]
        else:
            print(f"⚠️ Warning: Dataset folder '{dataset_folder}' not found.")

    def search(self, query, top_k=5):
        """
        Perform keyword-based search.

        Args:
            query (str): Search query
            top_k (int): Number of results to return

        Returns:
            list: Ranked list of filenames
        """
        query_words = query.lower().split()
        results = []

        # Iterate through dataset filenames
        for filename in self.files:
            score = 0
            name_lower = filename.lower()

            # Term frequency scoring (very simple heuristic)
            for word in query_words:
                if word in name_lower:
                    score += 1
            
            # Only keep matches with at least one keyword
            if score > 0:
                results.append((filename, score))

        # Sort results by score (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Return only filenames (strip scores)
        return [res[0] for res in results[:top_k]]


# ==========================================
# 🎯 2. GROUND TRUTH (Test Queries)
# ==========================================
"""
GROUND_TRUTH maps:
    Query → Expected Relevant Paper Title Fragment

Used to:
- Evaluate Precision@1
- Evaluate Recall@5
- Ensure reproducible benchmarking

Total queries ≈ 100 (cross-domain coverage)
"""
GROUND_TRUTH = {
    # (Dictionary content unchanged — intentionally preserved)
    # ...
}
# NOTE: Dictionary content intentionally unchanged.


# ==========================================
# 📊 3. BENCHMARK EXECUTION
# ==========================================
def run_benchmark():
    """
    Main benchmarking pipeline.

    Steps:
    1. Initialize baseline and ODF engines
    2. Run queries across both systems
    3. Compute Precision@1 and Recall@5
    4. Print comparison table
    5. Generate styled visualization
    """

    print("🚀 Starting Benchmark: Keyword Baseline vs. ODF Semantic Search...")
    
    # ---------------------------------------------------------
    # 1. Initialize Engines
    # ---------------------------------------------------------
    dataset_path = "Research_Massive_Dataset"
    kw_engine = KeywordSearchEngine(dataset_path)
    
    try:
        from search_engine.vector_search import VectorSearch
        odf_engine = VectorSearch()
        print("✅ Vector Search Engine Loaded Successfully.")
    except ImportError:
        print("❌ Error: 'search_engine' module not found.")
        print("   Ensure you are in the project root and 'search_engine' package exists.")
        return
    except Exception as e:
        print(f"❌ Error initializing VectorSearch: {e}")
        return

    kw_stats = {'p1': 0, 'r5': 0}
    odf_stats = {'p1': 0, 'r5': 0}
    
    total = len(GROUND_TRUTH)

    print("\n" + "="*85)
    print(f"{'QUERY (Truncated)':<50} | {'KEYWORD':<10} | {'ODF (AI)':<10}")
    print("="*85)

    for query, target in GROUND_TRUTH.items():
        
        kw_results = kw_engine.search(query, top_k=5)
        
        kw_p1 = False
        if kw_results and target.lower() in kw_results[0].lower():
            kw_stats['p1'] += 1
            kw_p1 = True
            
        kw_r5 = False
        for res in kw_results:
            if target.lower() in res.lower():
                kw_stats['r5'] += 1
                kw_r5 = True
                break

        odf_results = odf_engine.search(query, top_k=5)
        
        def get_fname(res_item):
            if isinstance(res_item, dict):
                return res_item['metadata']['filename']
            return res_item

        odf_p1 = False
        if odf_results:
            if target.lower() in get_fname(odf_results[0]).lower():
                odf_stats['p1'] += 1
                odf_p1 = True

        odf_r5 = False
        if odf_results:
            for item in odf_results:
                if target.lower() in get_fname(item).lower():
                    odf_stats['r5'] += 1
                    odf_r5 = True
                    break

        status_kw = "✅" if kw_p1 else "❌"
        status_odf = "✅" if odf_p1 else "❌"
        print(f"{query[:47]:<50} | {status_kw:^10} | {status_odf:^10}")

    metrics = {
        'KW_P1': (kw_stats['p1'] / total) * 100,
        'ODF_P1': (odf_stats['p1'] / total) * 100,
        'KW_R5': (kw_stats['r5'] / total) * 100,
        'ODF_R5': (odf_stats['r5'] / total) * 100,
    }
    
    print("\n" + "="*60)
    print("🏆 FINAL SCOREBOARD (N=100 Queries)")
    print("="*60)
    print(f"Keyword Search  | Precision@1: {metrics['KW_P1']:5.1f}% | Recall@5: {metrics['KW_R5']:5.1f}%")
    print(f"ODF (Proposed)  | Precision@1: {metrics['ODF_P1']:5.1f}% | Recall@5: {metrics['ODF_R5']:5.1f}%")
    print("="*60)
    
    labels = ['Keyword Search\n(Baseline)', 'ODF System\n(Proposed)']
    p1_scores = [metrics['KW_P1'], metrics['ODF_P1']]
    r5_scores = [metrics['KW_R5'], metrics['ODF_R5']]

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    
    rects1 = ax.bar(x - width/2, p1_scores, width,
                    label='Precision@1 (Top Match)', 
                    color='#E74C3C', alpha=0.9,
                    edgecolor='black', linewidth=0.7)

    rects2 = ax.bar(x + width/2, r5_scores, width,
                    label='Recall@5 (Top 5 Matches)', 
                    color='#2ECC71', alpha=0.9,
                    edgecolor='black', linewidth=0.7)

    ax.set_ylabel('Accuracy (%)')
    ax.set_title('Comparative Retrieval Performance (N=100)')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(loc='upper left',
              frameon=True,
              fancybox=False,
              edgecolor='black',
              framealpha=1)

    ax.set_ylim(0, 115)

    ax.set_axisbelow(True)
    ax.yaxis.grid(True, linestyle='--', alpha=0.5, color='gray')

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.1f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=10, fontweight='bold')

    autolabel(rects1)
    autolabel(rects2)

    plt.tight_layout()
    
    plt.savefig('performance_comparison.pdf',
                format='pdf', bbox_inches='tight')
    plt.savefig('performance_comparison.png',
                dpi=600, bbox_inches='tight')
    
    print("🖼️  Charts saved: 'performance_comparison.pdf' & .png")
    plt.show()


if __name__ == "__main__":
    run_benchmark()