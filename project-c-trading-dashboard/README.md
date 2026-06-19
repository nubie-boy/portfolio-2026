# Project C: Autonomous Trading Dashboard

> **Status:** 📋 Rencana  
> **Agent Utama:** Ningguang (Analysis & Reporting)

## 📋 Ringkasan

Market scanner harian otonom yang menganalisis SMC structure, candlestick patterns, dan technical indicators — menghasilkan interactive chart report otomatis setiap pukul 20:00 WITA. Dibangun untuk berjalan 3+ bulan berturut-turut sebagai bukti consistency dan reliability.

## 🏗️ Struktur

```
core/
├── scanner.py               # Market scanner (wrapper Bitunix API)
├── analyzer.py              # SMC + pattern analysis engine
├── reporter.py              # HTML report generator
└── risk_manager.py          # Position sizing & SL/TP

reports/
├── daily/                   # Report harian
├── weekly/                  # Rekap mingguan
└── monthly/                 # Rekap bulanan

cron/
├── run_daily.sh             # Eksekusi harian
└── run_weekly.sh            # Rekap mingguan
```

## ⚙️ Alur Analisis

```
Fetch OHLCV → Technical Indicators → SMC Structure → Pattern Recognition → Scoring → Report
    1               2                   3                 4               5         6
```

## 📊 Format Report

Setiap report mencakup:
- **Market Overview:** Harga real-time, perubahan 24h, sentimen
- **Top Picks:** Ranking pair berdasarkan skor teknis (0-100)
- **Interactive Chart:** SMC structure, Order Blocks, FVG
- **Verdict:** LONG/SHORT/WATCH dengan Entry, SL, TP
- **Risk Level:** Portfolio allocation recommendation

## ⏰ Jadwal

- **Daily:** 12:00 UTC (20:00 WITA) via GitHub Actions
- **Weekly:** Setiap hari Minggu
- **Monthly:** Akhir bulan
