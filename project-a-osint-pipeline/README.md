# Project A: Automated Security Recon Pipeline

> **Status:** 🚧 Dalam Pengembangan  
> **Agent Utama:** Santika (OSINT) + Ningguang (Reporting)

## 📋 Ringkasan

Pipeline otomatis yang menerima target domain atau IP, menjalankan reconnaissance multi-layer via Santika Agent, dan menghasilkan executive report dalam HTML/Markdown.

## 🏗️ Struktur

```
pipeline/
├── orchestrator.py          # Main entry — koordinasi semua agent
├── targets.txt              # Daftar target (1 per line)
├── santika_integration.py   # Bridge ke Santika API/CLI
├── data_processor.py        # Parse & dedup hasil OSINT
└── ningguang_reporter.py    # Generate report (HTML/MD)
```

## ⚙️ Cara Kerja

```
Target Input → Santika Recon → Data Processing → Report Generation → Deploy Pages
    1              2               3                 4                  5
```

1. Baca target dari `targets.txt`
2. Santika menjalankan: subdomain enumeration, port scan, certificate transparency, WHOIS
3. DataProcessor: parsing, deduplikasi, scoring
4. NingguangReporter: executive summary, risk indicators, severity breakdown
5. Auto-deploy ke GitHub Pages via GitHub Actions

## 📄 Sample Output

Lihat [`reports/sample/`](reports/sample/) untuk contoh report yang sudah dihasilkan.

## ⏰ Jadwal

- **Daily Scan:** 06:00 UTC via GitHub Actions
- **Manual Trigger:** via `workflow_dispatch`
