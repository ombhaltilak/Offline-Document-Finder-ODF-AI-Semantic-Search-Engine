import time  # Used for measuring total execution time and average query latency
import numpy as np  # Used for numerical computations (Mean Reciprocal Rank calculation)
from search_engine.vector_search import VectorSearch  # Semantic vector search engine implementation

# ==========================================
# 🎯 GROUND TRUTH: 100 SEMANTIC QUERIES
# ==========================================
"""
GROUND_TRUTH Dictionary

Maps:
    Natural Language Query → Expected Keyword in Target Paper Filename

Purpose:
- Provides deterministic evaluation targets
- Enables automated ranking verification
- Used to compute MRR, Precision@1, Recall@5, and Recall@10

Each query expects the system to retrieve a document
whose filename contains the associated keyword fragment.
"""
GROUND_TRUTH = {
    # --- BIOLOGY (15 Queries) ---
    "emergence of metabolically active protocells": "De novo emergence",
    "radiofrequency effects on leuconostoc mesenteroides": "Effects of 245 GHz",
    "network pharmacology for polypharmacology": "Network Pharmacology Framework",
    "client enrichment in biomolecular condensates": "Principles of Client Enrichment",
    "detecting batch heterogeneity in genomics": "Detecting Batch Heterogeneity",
    "dual head transformer for biological sequences": "GP-DHT",
    "computational evolution of spatial oncology": "Histopathology-centered",
    "estimating mitochondrial genome frequency": "MitoFREQ",
    "graph neural networks for cortical morphology": "Graph Neural Network Reveals",
    "kuramoto guided graph network for brain structure": "KOCOBrain",
    "visual decoding from primate brains": "Simple Models Rich Representations",
    "symptoms of sporadic creutzfeldt jakob disease": "Sporadic Creutzfeldt Jakob",
    "agent based modelling for population impact": "An agent-based modelling",
    "gene genealogies in diploid populations": "Gene genealogies in diploid",
    "developmental enigma of rhizomes": "The genetic and developmental enigma",

    # --- COMPUTER SCIENCE: AI & LEARNING (20 Queries) ---
    "building production ready probes for gemini": "Building Production-Ready Probes",
    "do explanations generalize in reasoning models": "Do explanations generalize",
    "consolidated dataset for metabolomics ai": "MetaboNet",
    "strategic manipulation of mediated content": "The Poisoned Apple Effect",
    "constant depth unitary preparation of dicke states": "Constant-Depth Unitary",
    "computational and dynamical complexity correspondences": "Correspondences in computational",
    "minimizing cost of efx allocations": "Minimizing the Cost of EFx",
    "optimal proximity gap for reed solomon codes": "Optimal Proximity Gap",
    "chebyshev accelerated subspace eigensolver": "Chebyshev Accelerated Subspsace",
    "generative data assimilation on urban areas": "GenDA Generative Data",
    "scad thresholding rule for statistics": "Smooth SCAD",
    "conversational exam for assessment": "The Conversational Exam",
    "capacity constraints in admissions processes": "Capacity Constraints Make",
    "evaluating llm behavior in hiring": "Evaluating LLM Behavior",
    "bridging computational narrative analytics": "Interactive Narrative Analytics",
    "language of thought in large language models": "Language of Thought Shapes",
    "intelligent hardware monitoring for security": "IMS Intelligent Hardware",
    "distributed authentication via physical unclonable functions": "InterPUF",
    "help seeking for digital privacy": "Understanding Help Seeking",
    "membership inference attacks against video models": "VidLeaks",

    # --- COMPUTER SCIENCE: SYSTEMS & HARDWARE (15 Queries) ---
    "stabilizer code generic fault tolerant computing": "Stabilizer Code-Generic",
    "streaming stochastic submodular maximization": "Streaming Stochastic Submodular",
    "spanning tree congestion complexity": "Two Complexity Results",
    "parallel batch dynamic trees algorithm": "UFO Trees",
    "improving database performance with transactions": "Improving Database Performance",
    "redundancy driven functional dependency discovery": "Redundancy-Driven Top-k",
    "resistance distance in databases": "Theoretically and Practically",
    "translating database schemes into relational": "Translating database mathematical",
    "load stabilization for mmo game servers": "AFLL Real-time Load Stabilization",
    "breaking storage bandwidth tradeoff": "Breaking the Storage-Bandwidth",
    "optimized function fusion for serverless": "Konflux",
    "topology agnostic throughput computation": "Space-Optimal Computation",
    "enhancing mobile ad hoc networks": "Enhancing Mobile Ad Hoc",
    "extractive summarization on cmos ising machine": "Extractive summarization on a CMOS",
    "reproducible platform for ai research": "MHubai",

    # --- COMPUTER SCIENCE: VISION & ROBOTICS (10 Queries) ---
    "verifying noir zero knowledge programs": "Formally Verifying Noir",
    "reversible weighted automata over rings": "Reversible Weighted Automata",
    "rewriting systems on arbitrary monoids": "Rewriting Systems on Arbitrary",
    "symbolic functional decomposition": "Symbolic Functional Decomposition",
    "editing intrinsic attributes of objects": "Alterbute Editing Intrinsic",
    "3d understanding for precise camera control": "Beyond Inpainting",
    "extrinsic vector field processing": "Extrinsic Vector Field",
    "vision as inverse graphics agent": "Vision-as-Inverse-Graphics",
    "approximate cim compiler for sram": "OpenACM",
    "pipelined graph random walks on fpgas": "RidgeWalker",

    # --- FINANCE (15 Queries) ---
    "crypto pricing with hidden factors": "Crypto Pricing with Hidden Factors",
    "market co-movement in critical minerals": "Event-Driven Market Co-Movement",
    "martingale optimal transport theory": "Multi-Period Martingale",
    "reinforcement learning for option hedging": "Reinforcement Learning for Option Hedging",
    "federated survival learning with bayesian privacy": "FSL-BDP",
    "timescale separation in financial time series": "Fast Times Slow Times",
    "optimal abatement schedules for carbon": "Optimal Abatement Schedules",
    "adaptive dataflow system for finance": "History Is Not Enough",
    "probabilistic time series foundation model": "ProbFM",
    "resisting manipulative bots in copy trading": "Resisting Manipulative Bots",
    "linear strands of binomial edge ideals": "Linear strands of powers",
    "n-total graph of an integral domain": "The n-total graph",
    "rank nullity ring of a matroid": "The rank-nullity ring",
    "universality results for random matrices": "Universality results for random matrices",
    "frame eversion and geometric rigidity": "Frame eversion and contextual",

    # --- PHYSICS (15 Queries) ---
    "globally rigid vertex transitive graphs": "Highly regular vertex-transitive",
    "newman polynomials and their divisors": "Algorithmic aspects of Newman",
    "effective roth and ridout constants": "From ABC to Effective Roth",
    "sumset size races for measurable sets": "Sumset size races",
    "divisor function along sums of biquadrates": "The divisor function along sums",
    "viscosity solutions for branching diffusion": "Controlled Interacting Branching",
    "dvoretzky covering problem": "Dvoretzky covering problem",
    "stein's method for matrix normal distribution": "Steins method for the matrix",
    "stochastic perturbation of sweeping process": "Stochastic Perturbation",
    "optimal transport for latent structured models": "Optimal transport based theory",
    "classification of regular maps with euler characteristic": "A classification of regular maps",
    "entanglement complexity of spanning pairs": "Entanglement complexity",
    "forbidden configurations in lens space": "Forbidden configurations",
    "knot surgery 4-manifolds": "Knot surgery 4-manifolds",
    "bremsstrahlung emission in compact stars": "Bremsstrahlung emission",

    # --- ASTROPHYSICS & QUANTUM (10 Queries) ---
    "variability analysis of blazar 3c 4543": "Correlated variability in the blazar",
    "warped inflationary brane scanning": "Towards a warped inflationary",
    "ultraviolet spectra of local galaxies": "Ultraviolet Spectra of Local Galaxies",
    "ferromagnetism in fe doped sno2": "Ferromagnetism in Fe-doped SnO2",
    "rotating bose einstein condensate phases": "Phases of a rotating Bose-Einstein",
    "quantum magneto oscillations in mn11": "Quantum-magneto oscillations",
    "ultrafast conductivity dynamics in pentacene": "Ultrafast Conductivity Dynamics",
    "algebraic description of page transition": "An algebraic description",
    "conformal symmetry and thermal acceleration": "Conformal Symmetry and the Thermal",
    "nanofabricated torsion pendulums for gravity": "Nanofabricated torsion pendulums"
}

# ==========================================
# 🚀 EVALUATION LOGIC
# ==========================================
def calculate_metrics():
    """
    Main evaluation pipeline.

    Steps:
    1. Initialize VectorSearch engine
    2. Execute 100 semantic queries (Top-10 retrieval)
    3. Compute ranking metrics:
        - Mean Reciprocal Rank (MRR)
        - Precision@1
        - Recall@5
        - Recall@10
        - Average query latency
    4. Print formatted report
    5. Generate LaTeX-ready results table
    """

    print("\n🚀 INITIALIZING MASSIVE EVALUATION (100 QUERIES)...")

    # Initialize semantic vector search engine
    try:
        vs = VectorSearch()
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    print(f"\n🧪 STARTING TEST...")
    print("="*80)
    print(f"{'QUERY (Truncated)':<50} | {'RANK':<5} | {'STATUS'}")
    print("-" * 80)

    # Metric tracking containers
    reciprocal_ranks = []  # For MRR calculation
    hits_at_1 = 0          # Precision@1 counter
    hits_at_5 = 0          # Recall@5 counter
    hits_at_10 = 0         # Recall@10 counter

    total_queries = len(GROUND_TRUTH)
    start_time = time.time()  # Start latency measurement

    # Iterate over benchmark queries
    for query, expected_keyword in GROUND_TRUTH.items():

        # Retrieve Top-10 results from semantic search engine
        results = vs.search(query, top_k=10)

        rank = -1  # Default: not found

        # Determine ranking position of expected document
        for i, res in enumerate(results):
            if expected_keyword.lower() in res['metadata']['filename'].lower():
                rank = i + 1  # Convert zero-based index to rank
                break

        # Update evaluation statistics
        if rank != -1:
            reciprocal_ranks.append(1.0 / rank)

            if rank == 1:
                hits_at_1 += 1
            if rank <= 5:
                hits_at_5 += 1
            if rank <= 10:
                hits_at_10 += 1

            print(f"{query[:47]:<50} | #{rank:<4} | ✅ Found")
        else:
            reciprocal_ranks.append(0.0)
            print(f"{query[:47]:<50} | -    | ❌ Not Found")

    # Compute latency
    total_time = time.time() - start_time
    avg_latency = total_time / total_queries

    # Final metric calculations
    mrr_score = np.mean(reciprocal_ranks) if reciprocal_ranks else 0
    recall_1 = (hits_at_1 / total_queries) * 100
    recall_5 = (hits_at_5 / total_queries) * 100
    recall_10 = (hits_at_10 / total_queries) * 100

    # Print summary report
    print("\n" + "="*60)
    print("📊 FINAL IEEE RESULTS (100 SAMPLE SIZE)")
    print("="*60)
    print(f"📂 Dataset Size:        ~200 Documents")
    print(f"❓ Queries Tested:      {total_queries}")
    print(f"⏱️ Avg Latency:         {avg_latency:.4f} sec/query")
    print("-" * 60)
    print(f"🏆 MRR Score:           {mrr_score:.4f}")
    print(f"🎯 Precision@1:         {recall_1:.1f}%")
    print(f"🔎 Recall@5:            {recall_5:.1f}%")
    print(f"🔎 Recall@10:           {recall_10:.1f}%")
    print("="*60)

    # Generate LaTeX table for academic publication
    print("\n📝 LaTeX Code for IEEE Paper:")
    print("-" * 30)
    print(r"\begin{table}[h]")
    print(r"\centering")
    print(r"\caption{Retrieval Performance on 100-Query Benchmark}")
    print(r"\begin{tabular}{|l|c|}")
    print(r"\hline")
    print(r"\textbf{Metric} & \textbf{Value} \\ \hline")
    print(f"Mean Reciprocal Rank (MRR) & {mrr_score:.3f} \\\\")
    print(f"Precision@1 & {recall_1:.1f}\\% \\\\")
    print(f"Recall@5 & {recall_5:.1f}\\% \\\\")
    print(f"Avg. Query Latency & {avg_latency:.3f} s \\\\ \hline")
    print(r"\end{tabular}")
    print(r"\label{tab:results_100}")
    print(r"\end{table}")


# Script entry point
if __name__ == "__main__":
    calculate_metrics()