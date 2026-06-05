import time
import random
from queue import Empty
from concurrent.futures import ThreadPoolExecutor

# Daftar Dokter Spesifik Tugas Triase/Pemeriksaan Awal
TRIAGE_DOCTORS = ["Dr. Alice (Triase)", "Dr. Bob (Triase)", "Dr. Charlie (Triase)"]

def assess_patient(patient):
    """
    Simulasi penilaian triase oleh DOKTER TRIASE.
    Menentukan severity_score berdasarkan keluhan (complaint) pasien.
    """
    time.sleep(0.3)  # Simulasi waktu pemeriksaan fisik awal oleh dokter
    complaint = patient.get("complaint", "pusing")

    # Logika Medis: Menentukan keparahan berdasarkan jenis keluhan
    if complaint in ["nyeri dada", "sesak napas"]:
        score = random.randint(8, 10)
        priority = "URGENT"
        wait_time = 0
        color = "red"
    elif complaint in ["demam tinggi", "sakit kepala berat", "patah tulang", "luka terbuka"]:
        score = random.randint(5, 7)
        priority = "NORMAL"
        wait_time = random.randint(10, 30)
        color = "yellow"
    else:  # mual, muntah, pusing, sakit perut, batuk
        score = random.randint(1, 4)
        priority = "LOW"
        wait_time = random.randint(30, 60)
        color = "green"

    return {
        **patient,
        "severity_score": score,
        "priority": priority,
        "estimated_wait": wait_time,
        "priority_color": color,
        "triage_by": random.choice(TRIAGE_DOCTORS), # Dokter yang memeriksa di triase
        "triage_time": __import__('datetime').datetime.now().strftime("%H:%M:%S"),
    }


def triage_node(queue_in, queue_out, shared_state, stop_event):
    print("[NODE B] Triase paralel dimulai (Menggunakan ThreadPool)")
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        while not stop_event.is_set():
            batch = []
            
            try:
                patient = queue_in.get(timeout=0.5)
                batch.append(patient)
            except Empty:
                continue

            while len(batch) < 4:
                try:
                    patient = queue_in.get_nowait()
                    batch.append(patient)
                except Empty:
                    break

            if not batch:
                continue

            try:
                results = list(executor.map(assess_patient, batch))
            except Exception as e:
                print(f"[NODE B ERROR] Gagal memproses batch: {e}")
                continue

            for result in results:
                queue_out.put(result)

            by_priority = {"URGENT": 0, "NORMAL": 0, "LOW": 0}
            for r in results:
                by_priority[r["priority"]] += 1

            for key, val in by_priority.items():
                k = f"triage_{key.lower()}"
                shared_state[k] = shared_state.get(k, 0) + val

            shared_state["total_triaged"] = shared_state.get("total_triaged", 0) + len(results)

            print(f"[NODE B] {len(results)} pasien selesai diperiksa Dokter Triase.")
            
    print("[NODE B] Selesai")