# Contoh Report OSINT Pipeline
## Target: example.com
## Tanggal: 2026-06-19
## Status: 🟡 Intermediate

---

## 📋 Executive Summary

- **3 subdomain** ditemukan (mail, blog, dev)
- **2 service** teridentifikasi (nginx 1.18, Apache 2.4.41)
- **1 potensi kerentanan** — Apache versi lama
- **SSL/TLS** valid, certificate dari Let's Encrypt

---

## 🗺️ Attack Surface Map

```
example.com
├── mail.example.com (192.168.1.10)
│   └── nginx 1.18
├── blog.example.com (192.168.1.11)
│   └── Apache 2.4.41 ⚠️
└── dev.example.com (192.168.1.12)
    └── Apache 2.4.41 ⚠️
```

## ⚠️ Risk Indicators

| Indicator | Severity | Detail |
|-----------|----------|--------|
| Apache 2.4.41 | 🟠 High | CVE-2021-41773 (Path Traversal) |
| Open port 22 | 🔵 Low | SSH accessible from public |
| Missing Security Headers | 🟡 Medium | X-Content-Type-Options, CSP tidak ada |

## 📊 Severity Breakdown

```
Critical:  0  ██░░░░░░░░  0%
High:      1  ██████████ 33%
Medium:    1  ██████████ 33%
Low:       1  ██████████ 33%
```

---

## 🔗 Referensi

- CVE-2021-41773: https://nvd.nist.gov/vuln/detail/CVE-2021-41773
- Target: example.com
- Scanner: Santika Agent v1.0
