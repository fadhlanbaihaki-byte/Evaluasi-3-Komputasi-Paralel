import csv
import os
from queue import Empty
from datetime import datetime

LOG_FILE = "logs/queue_log.csv"
HEADERS = [
    "timestamp", "patient_id", "name", "age", "complaint",
    "severity_score", "priority", "assigned_doctor",
    "unit", "treatment_minutes", "arrival_time", "served_at"
]

def logger_node(queue_in, stop_event):
    print("[NODE D] Logger CSV dimulai")

    # Buat file CSV jika belum ada
    os.makedirs("logs", exist_ok=True)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=HEADERS)
            writer.writeheader()

    while not stop_event.is_set():
        try:
            patient = queue_in.get(timeout=1)
        except Empty:
            continue

        row = {
            "timestamp": datetime.now().isoformat(),
            "patient_id": patient.get("id", ""),
            "name": patient.get("name", ""),
            "age": patient.get("age", ""),
            "complaint": patient.get("complaint", ""),
            "severity_score": patient.get("severity_score", ""),
            "priority": patient.get("priority", ""),
            "assigned_doctor": patient.get("assigned_doctor", ""),
            "unit": patient.get("unit", ""),
            "treatment_minutes": patient.get("treatment_minutes", ""),
            "arrival_time": patient.get("arrival_time", ""),
            "served_at": patient.get("served_at", ""),
        }

        with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=HEADERS)
            writer.writerow(row)

        print(f"[NODE D] Log disimpan: {row['patient_id']} - {row['priority']}")

    print("[NODE D] Selesai")
