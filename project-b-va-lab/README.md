# Project B: AI-Augmented Vulnerability Assessment Lab

> **Status:** 📋 Rencana  
> **Agent Utama:** Santika (Validation) + Ningguang (Risk Matrix)

## 📋 Ringkasan

Lab lokal Vulnerability Assessment menggunakan Metasploitable 2 dan DVWA di Linux VM. Scanning dilakukan secara manual dengan Nmap/Nikto/Nuclei, kemudian hasilnya divalidasi oleh Santika Agent. Ningguang menghasilkan risk matrix dan remediation plan.

## 🏗️ Struktur

```
scans/
├── raw/                     # Hasil scan mentah (nmap XML, nikto TXT)
├── santika-validation/      # Hasil validasi Santika
└── consolidated/            # Data final setelah diproses

reports/
├── templates/               # Template report
└── samples/                 # Contoh report jadi

scripts/
├── scan_runner.sh           # Wrapper scanning
├── parse_nmap.py            # Parse XML → JSON
├── santika_validator.py     # Cross-validation
└── report_generator.py      # Generate report
```

## ⚙️ Metodologi

```
Phase 1: Reconnaissance (Nmap + Nikto + Nuclei)
Phase 2: Santika Cross-Validation
Phase 3: Data Consolidation
Phase 4: Risk Matrix & Report Generation
```

## 📊 Risk Matrix

| Severity | Score | Contoh |
|----------|-------|--------|
| 🔴 Critical | 9-10 | RCE, SQLi tanpa auth |
| 🟠 High | 7-8 | LFI, SSRF, auth bypass |
| 🟡 Medium | 4-6 | XSS, info disclosure |
| 🔵 Low | 1-3 | Banner grabbing |

## 🎯 Target Lab

- Metasploitable 2 (multiple vulns)
- DVWA (Damn Vulnerable Web Application)
- (Kedepan) HackTheBox retired machines
