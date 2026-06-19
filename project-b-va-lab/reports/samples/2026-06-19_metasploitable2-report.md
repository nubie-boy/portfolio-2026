# Contoh Report — AI-Augmented VA Lab
## Target: Metasploitable 2 (192.168.56.101)
## Tanggal: 2026-06-19

---

## 🔍 Executive Summary

Scan terhadap Metasploitable 2 menemukan **5 kerentanan kritis**, **3 high**, **4 medium**, dan **2 low**. Santika Agent memvalidasi 92% temuan. Remediation plan telah disusun berdasarkan prioritas severity.

## 📊 Risk Matrix

| # | Finding | Severity | CVSS | Santika Validasi | Remediasi |
|---|---------|----------|------|------------------|-----------|
| 1 | vsftpd 2.3.4 backdoor | 🔴 Critical | 9.8 | ✅ Confirmed | Upgrade/disable service |
| 2 | UnrealIRCd backdoor | 🔴 Critical | 9.8 | ✅ Confirmed | Patch/disable |
| 3 | Weak SSH creds (root:admin) | 🔴 Critical | 9.0 | ✅ Confirmed | Key-based auth |
| 4 | Samba usermap script | 🟠 High | 8.5 | ✅ Confirmed | Patch Samba |
| 5 | Apache Tomcat default creds | 🟠 High | 8.0 | ⚠️ Needs review | Change credentials |

## 🛡️ Remediation Plan

### Critical (Lakukan Segera)
1. Matikan vsftpd — `service vsftpd stop`
2. Matikan UnrealIRCd — `killall ircd`
3. Ganti semua password default

### High (Lakukan dalam 24 Jam)
1. Upgrade Samba — `apt-get update && apt-get upgrade samba`
2. Nonaktifkan Tomcat manager default

---

## 📈 Severity Distribution

```
Critical: 3 ████████████████ 30%
High:     2 ██████████      20%
Medium:   4 ████████████████████ 40%
Low:      2 ██████████      20%
```
