#!/usr/bin/env python3
"""
⚙️ Data Processor — Parsing & Deduplication

Mengambil output mentah dari Santika API (layer1),
membersihkan, mendeduplikasi, dan menambahkan scoring risiko.

Output: Struktur data terstandarisasi untuk NingguangReporter.
"""

import json
import re
from datetime import datetime
from typing import Any


class DataProcessor:
    """
    Memproses data OSINT mentah dari Santika menjadi format terstruktur.
    """

    @staticmethod
    def _normalize_domain(domain: str) -> str:
        """Normalisasi domain: lowercase, strip whitespace."""
        return domain.strip().lower()

    @staticmethod
    def _extract_domains_from_whois(whois_raw: str) -> list[str]:
        """Extract nameserver domains from WHOIS raw text."""
        domains = []
        if not whois_raw:
            return domains
        for match in re.finditer(r"Name Server:\s*(\S+)", whois_raw, re.IGNORECASE):
            domains.append(match.group(1).lower())
        return list(set(domains))

    def process(self, santika_response: dict, target: str) -> dict:
        """
        Proses response Santika API menjadi format terstruktur.

        Args:
            santika_response: Raw response dari Santika API
            target: Domain target

        Returns:
            Dict terstruktur dengan:
              - target_info
              - subdomains
              - open_ports
              - live_hosts
              - whois
              - tech_stack (dari informasi yang tersedia)
              - risk_indicators
              - severity_counts
              - analysis (jika layer2 tersedia)
        """
        layer1 = santika_response.get("layer1", {})
        layer2 = santika_response.get("layer2")

        result = {
            "target": target,
            "processed_at": datetime.utcnow().isoformat() + "Z",
            "target_info": {},
            "subdomains": [],
            "open_ports": [],
            "live_hosts": [],
            "whois": {},
            "tech_stack": [],
            "risk_indicators": [],
            "severity_counts": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0},
            "analysis": None,
        }

        # ── Target Info ──
        result["target_info"] = {
            "host": layer1.get("target", target),
            "timestamp": layer1.get("timestamp", ""),
        }

        # ── Subdomains ──
        subdomains_data = layer1.get("subdomains", {})
        items = subdomains_data.get("items", [])
        # Normalize
        result["subdomains"] = sorted(set(
            self._normalize_domain(s) for s in items if s
        ))

        # ── Open Ports ──
        ports_data = layer1.get("ports", {})
        port_list = ports_data.get("ports", [])
        result["open_ports"] = []
        for p in port_list:
            port_entry = {
                "port": p.get("port"),
                "state": p.get("state", "unknown"),
                "service": p.get("service", "unknown"),
                "banner": str(p.get("banner", "") or ""),
            }
            result["open_ports"].append(port_entry)

        # ── Live Hosts ──
        live_data = layer1.get("live_hosts", {})
        result["live_hosts"] = live_data.get("items", [])

        # ── WHOIS ──
        whois_data = layer1.get("whois", {})
        whois_raw = whois_data.get("raw", "")
        result["whois"] = {
            "domain": whois_data.get("domain", target),
            "raw": whois_raw,
            "nameservers": self._extract_domains_from_whois(whois_raw),
        }

        # ── Risk Indicators dari Open Ports ──
        for p in result["open_ports"]:
            port = p["port"]
            service = p["service"].lower()

            # Scoring berbasis port
            if port == 21 or service in ("ftp",):
                result["risk_indicators"].append({
                    "port": port,
                    "service": service or "ftp",
                    "severity": "HIGH",
                    "issue": "FTP — unencrypted file transfer, credential exposure risk",
                    "source": "port_analysis",
                })
            elif port == 23 or service in ("telnet",):
                result["risk_indicators"].append({
                    "port": port, "service": service or "telnet",
                    "severity": "CRITICAL",
                    "issue": "Telnet — unencrypted protocol, credential & command exposure",
                    "source": "port_analysis",
                })
            elif port == 25 or service in ("smtp",):
                result["risk_indicators"].append({
                    "port": port, "service": service or "smtp",
                    "severity": "MEDIUM",
                    "issue": "SMTP — open relay risk, potential spam vector",
                    "source": "port_analysis",
                })
            elif port in (80, 8080, 8880) and "https" not in service:
                result["risk_indicators"].append({
                    "port": port, "service": service or "http",
                    "severity": "MEDIUM",
                    "issue": f"HTTP port {port} — unencrypted traffic, MITM risk",
                    "source": "port_analysis",
                })
            elif port in (8443, 9443, 4443) or (port not in (80, 443, 22, 21, 25) and "http" in service):
                result["risk_indicators"].append({
                    "port": port, "service": service or "http",
                    "severity": "HIGH",
                    "issue": f"Alternative HTTP port {port} — often unprotected or misconfigured",
                    "source": "port_analysis",
                })
            elif port == 3306 or service in ("mysql",):
                result["risk_indicators"].append({
                    "port": port, "service": service or "mysql",
                    "severity": "HIGH",
                    "issue": "MySQL — database port exposed to internet",
                    "source": "port_analysis",
                })
            elif port == 6379 or service in ("redis",):
                result["risk_indicators"].append({
                    "port": port, "service": service or "redis",
                    "severity": "CRITICAL",
                    "issue": "Redis — unauthenticated access risk, data exposure",
                    "source": "port_analysis",
                })
            elif port in (27017, 27018) or service in ("mongodb",):
                result["risk_indicators"].append({
                    "port": port, "service": service or "mongodb",
                    "severity": "CRITICAL",
                    "issue": "MongoDB — database exposed to internet, data breach risk",
                    "source": "port_analysis",
                })
            elif port == 22:
                # SSH is common but note it
                result["risk_indicators"].append({
                    "port": port, "service": service or "ssh",
                    "severity": "LOW",
                    "issue": "SSH — ensure key-based auth, disable password login",
                    "source": "port_analysis",
                })

        # ── Severity Counts ──
        for indicator in result["risk_indicators"]:
            sev = indicator["severity"].upper()
            if sev in result["severity_counts"]:
                result["severity_counts"][sev] += 1

        # ── Analysis dari Santika (Layer 2) ──
        if layer2:
            result["analysis"] = {
                "risk_findings": layer2.get("risk_findings", []),
                "narrative": layer2.get("narrative", ""),
                "recommendations": layer2.get("recommendations", []),
            }

        return result


# ── Quick Test ──
if __name__ == "__main__":
    # Simulasi data dari Santika
    SAMPLE = {
        "layer1": {
            "target": "example.com",
            "timestamp": "2026-06-20T14:28:59Z",
            "subdomains": {"source": "subfinder", "count": 0, "items": []},
            "ports": {
                "host": "example.com",
                "ports": [
                    {"port": 80, "state": "open", "service": "http", "banner": ""},
                    {"port": 443, "state": "open", "service": "http", "banner": ""},
                    {"port": 8080, "state": "open", "service": "http", "banner": ""},
                    {"port": 22, "state": "open", "service": "ssh", "banner": "SSH-2.0-OpenSSH_8.9"},
                ]
            },
            "live_hosts": {"count": 0, "items": []},
            "whois": {
                "domain": "example.com",
                "raw": "Name Server: ELLIOTT.NS.CLOUDFLARE.COM\nName Server: HERA.NS.CLOUDFLARE.COM"
            }
        },
        "layer2": None
    }

    proc = DataProcessor()
    result = proc.process(SAMPLE, "example.com")
    print(json.dumps({
        "target": result["target"],
        "subdomains_count": len(result["subdomains"]),
        "open_ports_count": len(result["open_ports"]),
        "risk_indicators_count": len(result["risk_indicators"]),
        "severity_counts": result["severity_counts"],
        "nameservers": result["whois"]["nameservers"],
    }, indent=2))
