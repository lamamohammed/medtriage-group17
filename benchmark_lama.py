import random
import time
from medtriage.models import Patient
from medtriage.bst import PatientBST


def build_balanced_like_bst(n: int) -> tuple[PatientBST, list[Patient], list[int]]:
    """Build a PatientBST and a linear list of n patients, plus sample query IDs."""
    # Shuffle IDs before BST insertion to avoid worst-case skewed tree during average-case benchmark
    ids = list(range(1, n + 1))
    rng = random.Random(42)
    shuffled_ids = ids[:]
    rng.shuffle(shuffled_ids)

    bst = PatientBST()
    linear_list: list[Patient] = []

    for pid in ids:
        linear_list.append(Patient(pid, f"Patient-{pid}", 20 + (pid % 60)))

    for pid in shuffled_ids:
        bst.insert(Patient(pid, f"Patient-{pid}", 20 + (pid % 60)))

    queries = [rng.choice(ids) for _ in range(200)]
    return bst, linear_list, queries


def linear_search_id(records: list[Patient], target_id: int) -> Patient | None:
    for rec in records:
        if rec.patient_id == target_id:
            return rec
    return None


def run_benchmark(sizes: list[int] | None = None) -> list[tuple[int, float, float]]:
    if sizes is None:
        sizes = [1000, 2500, 5000, 7500, 10000]

    results: list[tuple[int, float, float]] = []
    print(f"{'N Records':>10} | {'BST Avg (ms)':>14} | {'Linear Avg (ms)':>16} | {'Speedup':>8}")
    print("-" * 58)

    for n in sizes:
        bst, linear_list, queries = build_balanced_like_bst(n)

        t0 = time.perf_counter()
        for q in queries:
            bst.search(q)
        t1 = time.perf_counter()
        bst_ms = ((t1 - t0) / len(queries)) * 1000.0

        t2 = time.perf_counter()
        for q in queries:
            linear_search_id(linear_list, q)
        t3 = time.perf_counter()
        lin_ms = ((t3 - t2) / len(queries)) * 1000.0

        speedup = (lin_ms / bst_ms) if bst_ms > 0 else 0.0
        results.append((n, bst_ms, lin_ms))
        print(f"{n:>10} | {bst_ms:>14.5f} | {lin_ms:>16.5f} | {speedup:>7.1f}x")

    try:
        import matplotlib.pyplot as plt

        ns = [r[0] for r in results]
        bst_times = [r[1] for r in results]
        lin_times = [r[2] for r in results]

        plt.figure(figsize=(8, 5))
        plt.plot(ns, bst_times, marker="o", label="PatientBST Search (~O(log n))")
        plt.plot(ns, lin_times, marker="s", label="Linear List Search (O(n))")
        plt.title("MedTriage Search Benchmark: BST vs Linear List")
        plt.xlabel("Number of Patient Records (N)")
        plt.ylabel("Average Lookup Time per Query (ms)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("benchmark_bst_vs_linear.png", dpi=150)
        print("\nSaved plot to 'benchmark_bst_vs_linear.png'.")
    except ImportError:
        print("\n(Optional) Install matplotlib to also save a runtime plot image.")

    return results


if __name__ == "__main__":
    run_benchmark()