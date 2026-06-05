# Parallel Queue Simulator — Sistem Antrian Klinik
**Mata Kuliah: Komputasi Paralel**

---

## Deskripsi
Simulasi sistem antrian klinik menggunakan konsep **komputasi paralel** dan **sistem terdistribusi**.
Setiap tahap pemrosesan pasien berjalan sebagai proses OS terpisah (terdistribusi),
dan tahap triase + layanan dokter menggunakan `multiprocessing.Pool` untuk memproses
banyak pasien secara **serentak dan paralel**.

---

## Arsitektur Pipeline

```
Node A → [Queue 1] → Node B (Pool.map) → [Queue 2] → Node C (Pool.map) → [Queue 3] → Node D
                                                              ↕
                                                    Manager Shared Dict
                                                              ↕
                                                    Flask SSE → Browser Dashboard
```

| Node | Fungsi | Paralel? |
|------|--------|----------|
| Node A | Pendaftaran pasien | ✗ |
| Node B | Triase & klasifikasi prioritas | ✓ Pool.map |
| Node C | Penanganan dokter (multi-loket) | ✓ Pool.map |
| Node D | Logging CSV | ✗ |

---

## Konsep Komputasi Paralel yang Diimplementasikan

1. **multiprocessing.Pool.map()** — Node B dan C memproses N pasien secara serentak di CPU core berbeda
2. **multiprocessing.Queue** — IPC antar-node (unidirectional message broker)
3. **multiprocessing.Manager** — shared dict yang aman untuk dibaca Flask dari proses berbeda
4. **Server-Sent Events (SSE)** — push data real-time dari Flask ke browser tanpa polling
5. **Benchmark** — perbandingan waktu sequential vs parallel (speedup & efficiency)

---

## Instalasi

```bash
pip install flask
```

---

## Cara Menjalankan

```bash
python main.py
```

Buka browser: **http://localhost:5000**

---

## Struktur File

```
parallel-queue-sim/
├── main.py                  # Flask server + SSE + launcher semua node
├── requirements.txt
├── nodes/
│   ├── registration_node.py # Node A: generate pasien
│   ├── triage_node.py       # Node B: triase paralel (Pool.map)
│   ├── service_node.py      # Node C: layanan dokter paralel (Pool.map)
│   └── logger_node.py       # Node D: tulis CSV
├── benchmark/
│   └── perf_test.py         # Sequential vs Parallel benchmark
├── static/
│   └── index.html           # Dashboard browser
└── logs/
    └── queue_log.csv        # Log otomatis
```

---

## Hasil Benchmark (Contoh)

| Metrik | Nilai |
|--------|-------|
| Sequential (8 pasien) | ~2.4 detik |
| Parallel (4 core) | ~0.7 detik |
| Speedup | ~3.4× |
| Efisiensi | ~85% |
