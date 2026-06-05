import random
import time
import uuid
from datetime import datetime

COMPLAINTS = [
    "demam tinggi", "sakit kepala berat", "nyeri dada",
    "sesak napas", "patah tulang", "luka terbuka",
    "mual dan muntah", "pusing", "sakit perut", "batuk"
]

def generate_patient():
    return {
        "id": str(uuid.uuid4())[:8].upper(),
        "name": f"Pasien-{random.randint(1000, 9999)}",
        "complaint": random.choice(COMPLAINTS),
        "age": random.randint(5, 80),
        "arrival_time": datetime.now().strftime("%H:%M:%S"),
        # 'severity_score' dihapus dari sini karena akan ditentukan oleh Dokter Triase
    }

def registration_node(queue_out, shared_state, stop_event):
    print("[NODE A] Pendaftaran pasien dimulai")
    while not stop_event.is_set():
        count = random.randint(1, 3)
        batch = [generate_patient() for _ in range(count)]
        for patient in batch:
            queue_out.put(patient)

        current = shared_state.get("waiting_registration", 0)
        shared_state["waiting_registration"] = current + count
        shared_state["total_arrived"] = shared_state.get("total_arrived", 0) + count

        print(f"[NODE A] {count} pasien baru didaftarkan")
        time.sleep(2)
    print("[NODE A] Selesai")