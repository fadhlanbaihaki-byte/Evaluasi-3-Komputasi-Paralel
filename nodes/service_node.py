import time
import random
from queue import Empty
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Pengelompokan Dokter Spesialis / Dokter Unit Tindakan Utama
DOCTORS_POOL = {
    "URGENT": ["Dr. Andi, Sp.An (IGD)", "Dr. Budi, Sp.JP (Spesialis Jantung)"],
    "NORMAL": ["Dr. Citra (Poli Umum)", "Dr. Dewi, Sp.A (Poli Anak)"],
    "LOW":    ["Dr. Eko (Klinik 24 Jam)", "Dr. Fitri (Poli Umum)"],
}

SPECIALTIES = {
    "URGENT": ["IGD Utama", "ICU Transit"],
    "NORMAL": ["Poli Rawat Jalan", "Klinik Umum"],
    "LOW":    ["Klinik Umum", "Apotek Internal"],
}

def handle_patient(patient):
    """
    Simulasi penanganan tindakan medis/pengobatan oleh DOKTER SPESIALIS.
    """
    priority = patient.get("priority", "NORMAL")

    # Durasi pengobatan (Pasien Urgent butuh tindakan lebih lama & intensif)
    if priority == "URGENT":
        duration = random.uniform(0.6, 1.0)
        treatment_time = random.randint(45, 90)
    elif priority == "NORMAL":
        duration = random.uniform(0.3, 0.5)
        treatment_time = random.randint(15, 30)
    else:
        duration = random.uniform(0.1, 0.2)
        treatment_time = random.randint(5, 15)

    time.sleep(duration)  # Simulasi proses pengobatan/tindakan

    return {
        **patient,
        "assigned_doctor": random.choice(DOCTORS_POOL[priority]), # Dokter spesifik sesuai keparahan
        "unit": random.choice(SPECIALTIES[priority]),
        "treatment_minutes": treatment_time,
        "served_at": datetime.now().strftime("%H:%M:%S"),
        "status": "SELESAI TREATMENT",
    }

def service_node(queue_in, queue_out, shared_state, stop_event):
    print("[NODE C] Layanan dokter spesialis paralel dimulai (Menggunakan ThreadPool)")
    
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
                results = list(executor.map(handle_patient, batch))
            except Exception as e:
                print(f"[NODE C ERROR] Gagal melayani batch: {e}")
                continue

            for result in results:
                queue_out.put(result)

            history = list(shared_state.get("recent_patients", []))
            history.extend(results)
            
            shared_state["recent_patients"] = history[-20:]
            shared_state["total_served"] = shared_state.get("total_served", 0) + len(results)

            print(f"[NODE C] {len(results)} pasien selesai ditangani Dokter Spesialis.")
            
    print("[NODE C] Selesai")