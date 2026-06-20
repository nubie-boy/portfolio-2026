# Project A: Automated Security Recon Pipeline

> **Status:** ✅ Fase 2 Selesai — Siap Deploy
> **Agent:** Ningguang (Controller) ↔ Santika (Scanner Node via HTTP API Bridge)

## 📋 Ringkasan

Pipeline OSINT otomatis dengan arsitektur **Dual-Agent**:

```
┌─ Server A (10.10.10.114) ────────────────────┐
│  Ningguang — Controller                        │
│  ├── orchestrator.py       Alur utama pipeline │
│  ├── santika_integration.py HTTP Client ke API │
│  ├── data_processor.py     Parsing & dedup     │
│  └── ningguang_reporter.py Generate report     │
└──────────────┬─────────────────────────────────┘
               │ POST /scan (X-API-Key Auth)
               ▼
┌─ Server B (10.10.10.100) ────────────────────┐
│  Santika — Scanner Node                        │
│  ├── FastAPI Server (port 8266)               │
│  ├── subfinder → subdomain enumeration        │
│  ├── nmap → port scanning                     │
│  ├── httpx → live host probing                │
│  ├── whois → domain registration lookup       │
│  └── LLM Analyst → risk analysis (layer2)     │
└───────────────────────────────────────────────┘
```

## 🏗️ Struktur Pipeline

```
project-a-osint-pipeline/
├── pipeline/
│   ├── orchestrator.py          # Entry point — koordinasi semua tahap
│   ├── targets.txt              # Daftar target (1 per line)
│   ├── santika_integration.py   # HTTP Bridge ke Santika API
│   ├── data_processor.py        # Parse & dedup hasil OSINT
│   └── ningguang_reporter.py    # Generate report HTML/MD
├── output/                      # Data mentah & terproses (JSON)
├── reports/
│   ├── daily/                   # Laporan harian (HTML + MD)
│   └── sample/                  # Sample untuk portfolio
├── docs/
│   └── architecture.md          # Dokumentasi arsitektur
└── tests/
```

## ⚙️ Cara Kerja

1. **Orchestrator** membaca target dari `targets.txt`
2. **SantikaIntegration** mengirim `POST /scan` ke Santika API (`10.10.10.100:8266`)
3. **Santika** menjalankan OSINT tools di server-nya → return JSON (Layer 1 + Layer 2)
4. **DataProcessor** membersihkan, dedup, dan memberi scoring risiko
5. **NingguangReporter** menghasilkan laporan HTML & Markdown elegan
6. **GitHub Actions** deploy laporan otomatis ke GitHub Pages

## 📊 Hasil Report

Laporan interaktif tersedia di:
- **HTML:** `reports/daily/YYYY-MM-DD_target.html`
- **Markdown:** `reports/daily/YYYY-MM-DD_target.md`

### Fitur Report HTML
- 💎 **Header** — target, timestamp, Tianquan branding
- 📊 **Overview Stats** — open ports, subdomains, risk indicators
- ⚠️ **Severity Breakdown** — bar chart visual (CRITICAL → LOW)
- 🌐 **Open Ports** — grid cards dengan port & service info
- 🔗 **Risk Indicators** — severity-colored cards dengan deskripsi
- 🧠 **Santika AI Analysis** — narrative & recommendations (jika analyze=true)
- 📋 **Raw WHOIS** — collapsible data

## 🔐 Autentikasi

Komunikasi antar-agent menggunakan **X-API-Key**:
```bash
Header: X-API-Key: <key>
```
Key disimpan sebagai GitHub Secret (`SANTIKA_API_KEY`).

## ▶️ Menjalankan

```bash
# Semua target dari targets.txt
python3 pipeline/orchestrator.py

# Satu target spesifik
python3 pipeline/orchestrator.py --target example.com

# Dengan analisis Santika LLM
SANTIKA_ANALYZE=true python3 pipeline/orchestrator.py --target example.com
```

## ⏰ Jadwal Otomatis

- **Daily Scan:** 06:00 UTC via GitHub Actions
- **Manual Trigger:** via `workflow_dispatch`
