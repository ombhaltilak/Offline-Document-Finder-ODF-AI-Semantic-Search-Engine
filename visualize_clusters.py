import os
import re
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
import chromadb


# ==========================================================
# EXTRACT DOMAIN FROM FILENAME
# ==========================================================
def extract_domain(filename):
    """
    Extract domain from filename like:
    [CS - AI] paper.pdf → Computer Science
    [Bio - Genomics] → Biology
    """

    if not filename:
        return "Unknown"

    match = re.search(r"\[(.*?)\]", filename)
    if not match:
        return "Unknown"

    content = match.group(1)

    if content.startswith("CS"):
        return "Computer Science"
    elif content.startswith("Bio"):
        return "Biology"
    elif content.startswith("Fin"):
        return "Finance"
    elif content.startswith("Math"):
        return "Mathematics"
    elif content.startswith("Phys"):
        return "Physics"
    else:
        return "Unknown"


# ==========================================================
# LOAD EMBEDDINGS FROM CHROMA
# ==========================================================
def load_embeddings():

    print("🔍 Connecting to Chroma DB...")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "data", "chroma_db")

    client = chromadb.PersistentClient(path=db_path)

    collections = client.list_collections()
    if not collections:
        raise ValueError("No collections found in Chroma DB.")

    collection_name = collections[0].name
    print(f"📦 Using collection: {collection_name}")

    collection = client.get_collection(name=collection_name)

    data = collection.get(include=["embeddings", "metadatas"])

    embeddings = data.get("embeddings", [])
    metadatas = data.get("metadatas", [])

    # Proper check (fixes NumPy ambiguity error)
    if embeddings is None or len(embeddings) == 0:
        raise ValueError("No embeddings found in collection.")

    embeddings = np.array(embeddings)

    print(f"✅ Loaded {embeddings.shape[0]} embeddings.")

    # Extract domains
    domains = []
    for meta in metadatas:
        filename = meta.get("filename", "")
        domains.append(extract_domain(filename))

    return embeddings, domains


# ==========================================================
# VISUALIZATION
# ==========================================================
def visualize_embeddings_2d():

    print("\n🎨 Generating TRUE Domain-Based Visualization...\n")

    embeddings, domains = load_embeddings()

    # Normalize embeddings
    scaler = StandardScaler()
    embeddings = scaler.fit_transform(embeddings)

    # Run t-SNE
    print("   ↳ Running t-SNE...")
    tsne = TSNE(
        n_components=2,
        perplexity=30,
        max_iter=1000,
        random_state=42
    )

    reduced = tsne.fit_transform(embeddings)

    # Domain Colors
    domain_colors = {
        "Computer Science": "#1f77b4",
        "Finance": "#2ca02c",
        "Mathematics": "#ff7f0e",
        "Biology": "#d62728",
        "Physics": "#9467bd",
        "Unknown": "#7f7f7f"
    }

    plt.figure(figsize=(9, 8))

    unique_domains = sorted(set(domains))

    for domain in unique_domains:
        idx = [i for i, d in enumerate(domains) if d == domain]

        plt.scatter(
            reduced[idx, 0],
            reduced[idx, 1],
            s=60,
            alpha=0.85,
            color=domain_colors.get(domain, "#7f7f7f"),
            edgecolors="black",
            linewidths=0.4,
            label=domain
        )

    plt.title("2D Visualization of Document Embeddings by Domain", fontsize=14)
    plt.xlabel("t-SNE Component 1")
    plt.ylabel("t-SNE Component 2")

    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend(title="Domain", frameon=True)

    plt.tight_layout()

    # Save output
    os.makedirs("outputs", exist_ok=True)
    output_path = os.path.join("outputs", "visualization.png")
    plt.savefig(output_path, dpi=300)

    print(f"\n✅ Saved to {output_path}")
    plt.show()


# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":
    visualize_embeddings_2d()