import time
import random
from multiprocessing import Pool

# Simulasi beban kerja triase satu pasien
def mock_assess(patient):
    time.sleep(0.3)
    score = patient["severity_score"]
    if score >= 8:
        return {**patient, "priority": "URGENT"}
    elif score >= 5:
        return {**patient, "priority": "NORMAL"}
    else:
        return {**patient, "priority": "LOW"}

def generate_mock_patients(n=8):
    return [
        {"id": f"P{i:03d}", "severity_score": random.randint(1, 10)}
        for i in range(n)
    ]

def run_sequential(patients):
    results = []
    for p in patients:
        results.append(mock_assess(p))
    return results

def run_parallel(patients, num_workers=4):
    with Pool(processes=num_workers) as pool:
        results = pool.map(mock_assess, patients)
    return results

def run_benchmark(num_patients=8, num_workers=4):
    patients = generate_mock_patients(num_patients)

    # Sequential
    start = time.perf_counter()
    run_sequential(patients)
    seq_time = round(time.perf_counter() - start, 4)

    # Parallel
    start = time.perf_counter()
    run_parallel(patients, num_workers)
    par_time = round(time.perf_counter() - start, 4)

    speedup   = round(seq_time / par_time, 2) if par_time > 0 else 0
    efficiency = round((speedup / num_workers) * 100, 1)

    return {
        "num_patients":   num_patients,
        "num_workers":    num_workers,
        "sequential_time": seq_time,
        "parallel_time":   par_time,
        "speedup":         speedup,
        "efficiency":      efficiency,
    }

if __name__ == "__main__":
    result = run_benchmark()
    print("\n=== BENCHMARK HASIL ===")
    for k, v in result.items():
        print(f"  {k}: {v}")
