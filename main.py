import json
import time
import threading
import multiprocessing
from flask import Flask, Response, jsonify, send_from_directory
from nodes.registration_node import registration_node
from nodes.triage_node import triage_node
from nodes.service_node import service_node
from nodes.logger_node import logger_node
from benchmark.perf_test import run_benchmark

app = Flask(__name__, static_folder="static")

# ── Shared state & queues (dibuat di top-level agar picklable) ──
manager    = None
shared     = None
q1 = q2 = q3 = q4 = None
stop_event = None
processes  = []

def init_system():
    global manager, shared, q1, q2, q3, q4, stop_event, processes
    manager    = multiprocessing.Manager()
    shared     = manager.dict({
        "waiting_registration": 0,
        "total_arrived":  0,
        "total_triaged":  0,
        "total_served":   0,
        "triage_urgent":  0,
        "triage_normal":  0,
        "triage_low":     0,
        "recent_patients": [],
        "system_running": True,
    })
    q1 = multiprocessing.Queue()   # Node A → Node B
    q2 = multiprocessing.Queue()   # Node B → Node C
    q3 = multiprocessing.Queue()   # Node C → Node D
    stop_event = multiprocessing.Event()

    procs = [
        multiprocessing.Process(target=registration_node, args=(q1, shared, stop_event), name="NodeA"),
        multiprocessing.Process(target=triage_node,       args=(q1, q2, shared, stop_event), name="NodeB"),
        multiprocessing.Process(target=service_node,      args=(q2, q3, shared, stop_event), name="NodeC"),
        multiprocessing.Process(target=logger_node,       args=(q3, stop_event), name="NodeD"),
    ]
    for p in procs:
        p.daemon = True
        p.start()
    processes.extend(procs)
    print("[SYSTEM] Semua node berjalan.")

# ── Routes ──────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/api/status")
def status():
    """Snapshot state saat ini (digunakan polling biasa)."""
    data = dict(shared)
    # List tidak bisa di-JSON langsung dari Manager, konversi dulu
    data["recent_patients"] = list(data.get("recent_patients", []))
    return jsonify(data)

@app.route("/api/stream")
def stream():
    """Server-Sent Events — browser subscribe ke endpoint ini."""
    def event_generator():
        while True:
            data = dict(shared)
            data["recent_patients"] = list(data.get("recent_patients", []))
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(1.5)
    return Response(event_generator(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@app.route("/api/benchmark")
def benchmark():
    """Jalankan benchmark di thread terpisah agar tidak block UI."""
    def do_bench():
        result = run_benchmark(num_patients=8, num_workers=4)
        shared["benchmark"] = result
    threading.Thread(target=do_bench, daemon=True).start()
    return jsonify({"message": "Benchmark dimulai, tunggu hasilnya di /api/status"})

@app.route("/api/reset")
def reset():
    """Reset counter statistik."""
    for key in ["waiting_registration","total_arrived","total_triaged",
                "total_served","triage_urgent","triage_normal","triage_low"]:
        shared[key] = 0
    shared["recent_patients"] = []
    return jsonify({"message": "Reset berhasil"})

# ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    multiprocessing.freeze_support()
    init_system()
    print("[SERVER] Flask berjalan di http://localhost:5000")
    app.run(debug=False, threaded=True, port=5000)
