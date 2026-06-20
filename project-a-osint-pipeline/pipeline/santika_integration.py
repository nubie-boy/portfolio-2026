#!/usr/bin/env python3
"""
🔗 Santika Integration — HTTP API Bridge ke Santika Scanner Node
Server B: 10.10.10.100:8266

Mengubah OSINT collection dari eksekusi lokal menjadi remote call
ke Santika Agent via HTTP API Bridge.
"""

import json
import os
import time
import requests
from typing import Optional

SANTIKA_BASE = os.environ.get("SANTIKA_BASE", "http://10.10.10.100:8266")
SANTIKA_API_KEY = os.environ.get("SANTIKA_API_KEY", "")
REQUEST_TIMEOUT = 180  # 3 menit untuk scan

# Validasi: pastikan API key tersedia
if not SANTIKA_API_KEY:
    print("[!] PERINGATAN: SANTIKA_API_KEY tidak diset. Set via environment variable.")


class SantikaIntegration:
    """
    HTTP Client untuk Santika Scanner API.

    Pola:
      - /health → cek ketersediaan Santika
      - POST /scan → kirim target, terima OSINT data (layer1 + opsional layer2)
    """

    def __init__(self, base_url: str = SANTIKA_BASE, api_key: str = SANTIKA_API_KEY):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        })
        self.session.timeout = REQUEST_TIMEOUT

    def health_check(self) -> dict:
        """Cek apakah Santika API hidup."""
        try:
            resp = self.session.get(f"{self.base_url}/health", timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            return {"status": "error", "message": str(e)}

    def collect(
        self,
        target: str,
        analyze: bool = False,
        timeout: Optional[int] = None,
    ) -> dict:
        """
        Kirim target ke Santika untuk OSINT scanning.

        Args:
            target: Domain/IP target
            analyze: True = Santika LLM analysis (layer2), False = raw OSINT only
            timeout: Request timeout in seconds (default: 180)

        Returns:
            Dict dengan layer1 (raw OSINT) dan opsional layer2 (analisis)
        """
        t = timeout or REQUEST_TIMEOUT
        payload = {"target": target, "analyze": analyze}

        print(f"    ╭─ Santika Scanner API")
        print(f"    ├─ Target : {target}")
        print(f"    ├─ Analyze: {analyze}")
        print(f"    ├─ Timeout: {t}s")
        print(f"    ╰─ Endpoint: POST {self.base_url}/scan")

        start = time.time()
        try:
            resp = self.session.post(
                f"{self.base_url}/scan",
                json=payload,
                timeout=t,
            )
            elapsed = time.time() - start

            if resp.status_code == 401:
                error_detail = resp.json().get("detail", "Unauthorized")
                print(f"    ✗ HTTP 401: {error_detail}")
                return {"error": "unauthorized", "detail": error_detail, "target": target}

            resp.raise_for_status()
            data = resp.json()
            elapsed = time.time() - start
            print(f"    ✓ Response: {elapsed:.1f}s")

            # Tambahkan metadata
            data["_meta"] = {
                "source": "santika-scanner",
                "target": target,
                "analyze": analyze,
                "response_time": round(elapsed, 2),
            }
            return data

        except requests.Timeout:
            elapsed = time.time() - start
            print(f"    ✗ Timeout after {elapsed:.0f}s (limit: {t}s)")
            print(f"    ╰─ Saran: Target besar? Coba naikkan timeout atau target spesifik")
            return {
                "error": "timeout",
                "target": target,
                "response_time": round(elapsed, 2),
            }

        except requests.RequestException as e:
            elapsed = time.time() - start
            print(f"    ✗ Connection error: {str(e)}")
            return {
                "error": "connection_error",
                "target": target,
                "detail": str(e),
                "response_time": round(elapsed, 2),
            }

    def get_status(self) -> dict:
        """Cek status tools yang tersedia di Santika."""
        try:
            health = self.health_check()
            return health
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ── Quick Test ──
if __name__ == "__main__":
    import sys

    santika = SantikaIntegration()

    # Test health
    print("\n[HEALTH CHECK]")
    health = santika.health_check()
    print(json.dumps(health, indent=2))

    if len(sys.argv) > 1:
        target = sys.argv[1]
        analyze = "--analyze" in sys.argv

        print(f"\n[SCAN: {target}] (analyze={analyze})")
        data = santika.collect(target, analyze=analyze)

        # Print layer summary
        if "error" in data:
            print(f"ERROR: {data['error']}")
        else:
            l1 = data.get("layer1", {})
            l2 = data.get("layer2")
            print(json.dumps({
                "subdomains": l1.get("subdomains", {}).get("count", 0),
                "ports_open": len(l1.get("ports", {}).get("ports", [])),
                "live_hosts": l1.get("live_hosts", {}).get("count", 0),
                "whois": bool(l1.get("whois", {}).get("raw")),
                "risk_findings": len(l2.get("risk_findings", [])) if l2 else 0,
                "response_time": data.get("_meta", {}).get("response_time"),
            }, indent=2))
