#!/usr/bin/env python3
"""
💎 Ningguang Reporter — Executive OSINT Report Generator

Mengubah data OSINT terstruktur menjadi laporan HTML yang elegan,
layaknya laporan yang keluar dari Jade Chamber.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class NingguangReporter:
    """
    Menghasilkan laporan HTML dan Markdown dari hasil OSINT pipeline.

    Output:
      - reports/daily/YYYY-MM-DD_target.html   (Interactive HTML)
      - reports/daily/YYYY-MM-DD_target.md     (Markdown)
      - reports/sample/YYYY-MM-DD_target.html  (Copy)
    """

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path(__file__).resolve().parent.parent / "reports"

    def generate(
        self,
        target: str,
        data: dict,
        output_dir: Optional[Path] = None,
        date_str: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> list[str]:
        """
        Generate HTML + MD report dari data OSINT terproses.

        Args:
            target: Domain target
            data: Data terstruktur dari DataProcessor
            output_dir: Output directory (override default)
            date_str: Tanggal laporan (YYYY-MM-DD)
            timestamp: ISO timestamp

        Returns:
            List of file paths yang dihasilkan
        """
        date_str = date_str or datetime.utcnow().strftime("%Y-%m-%d")
        timestamp = timestamp or datetime.utcnow().isoformat() + "Z"
        out = output_dir or self.output_dir

        daily_dir = out / "daily"
        sample_dir = out / "sample"
        daily_dir.mkdir(parents=True, exist_ok=True)
        sample_dir.mkdir(parents=True, exist_ok=True)

        safe_target = target.replace("/", "_").replace(":", "_")
        html_file = daily_dir / f"{date_str}_{safe_target}.html"
        md_file = daily_dir / f"{date_str}_{safe_target}.md"
        sample_html = sample_dir / f"{date_str}_{safe_target}.html"

        # Generate HTML
        html_content = self._build_html(target, data, date_str, timestamp)
        with open(html_file, "w") as f:
            f.write(html_content)

        # Generate Markdown
        md_content = self._build_markdown(target, data, date_str, timestamp)
        with open(md_file, "w") as f:
            f.write(md_content)

        # Copy to sample
        with open(sample_html, "w") as f:
            f.write(html_content)

        return [str(html_file), str(md_file), str(sample_html)]

    def _build_html(self, target: str, data: dict, date_str: str, timestamp: str) -> str:
        """Build interactive HTML report."""
        subdomains = data.get("subdomains", [])
        open_ports = data.get("open_ports", [])
        risk_indicators = data.get("risk_indicators", [])
        severity_counts = data.get("severity_counts", {})
        nameservers = data.get("whois", {}).get("nameservers", [])
        analysis = data.get("analysis")

        total_risks = sum(severity_counts.values())
        severity_json = json.dumps(severity_counts)

        # Ports JSON
        ports_json = json.dumps([
            {"port": p["port"], "service": p["service"], "state": p["state"]}
            for p in open_ports
        ])

        # Risk items JSON
        risks_json = json.dumps([
            {
                "severity": r["severity"],
                "port": r.get("port", ""),
                "service": r.get("service", ""),
                "issue": r.get("issue", "")
            }
            for r in risk_indicators
        ])

        # Level 2 analysis
        analysis_html = ""
        if analysis:
            findings = json.dumps(analysis.get("risk_findings", []))
            narrative = analysis.get("narrative", "")
            recommendations = analysis.get("recommendations", [])
            recs_json = json.dumps(recommendations)
            analysis_html = f"""
            <div class="section">
                <h2>🧠 Santika AI Analysis</h2>
                <div class="analysis-narrative">{narrative}</div>
                <div id="santikaFindings"></div>
                <div id="santikaRecs"></div>
            </div>
            <script>
                const findings = {findings};
                const recs = {recs_json};
                const findingsDiv = document.getElementById('santikaFindings');
                findingsDiv.innerHTML = '<h3>Risk Findings</h3><div class="findings-grid">' +
                    findings.map(f => `<div class="finding-card severity-${{f.severity.toLowerCase()}}">
                        <span class="sev-badge">${{f.severity}}</span>
                        <strong>Port ${{f.port}}</strong> — ${{f.service}}
                        <p>${{f.reason}}</p>
                    </div>`).join('') + '</div>';
                const recsDiv = document.getElementById('santikaRecs');
                recsDiv.innerHTML = '<h3>💡 Recommendations</h3><ul>' +
                    recs.map(r => `<li>${{r}}</li>`).join('') + '</ul>';
            </script>"""

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💎 OSINT Report — {target} | Ningguang</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #0a0a1a 100%);
            color: #e0d5c1;
            min-height: 100vh;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        .header {{
            text-align: center;
            padding: 3rem 0;
            border-bottom: 1px solid rgba(255, 215, 0, 0.2);
            margin-bottom: 2rem;
        }}
        .header h1 {{
            font-size: 2.5rem;
            background: linear-gradient(135deg, #ffd700, #ff8c00);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }}
        .header .subtitle {{
            color: #a89b85;
            margin-top: 0.5rem;
            font-size: 1.1rem;
        }}
        .header .meta {{ color: #8a7d6a; font-size: 0.9rem; margin-top: 0.3rem; }}
        .header .target-badge {{
            display: inline-block;
            background: linear-gradient(135deg, #ffd70022, #ff8c0022);
            border: 1px solid rgba(255, 215, 0, 0.3);
            padding: 0.5rem 2rem;
            border-radius: 50px;
            font-size: 1.5rem;
            font-weight: 600;
            color: #ffd700;
            margin-top: 1rem;
        }}
        .stats-row {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .stat-card {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 215, 0, 0.1);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            backdrop-filter: blur(10px);
            transition: transform 0.2s;
        }}
        .stat-card:hover {{ transform: translateY(-2px); }}
        .stat-card .number {{
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ffd700, #ff8c00);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .stat-card .label {{ color: #a89b85; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; margin-top: 0.3rem; }}
        .section {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 215, 0, 0.1);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
            backdrop-filter: blur(10px);
        }}
        .section h2 {{
            color: #ffd700;
            font-size: 1.3rem;
            margin-bottom: 1.5rem;
            border-bottom: 1px solid rgba(255, 215, 0, 0.1);
            padding-bottom: 0.8rem;
        }}
        .port-grid, .findings-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 1rem;
        }}
        .port-card {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}
        .port-card .port-num {{ font-size: 1.3rem; font-weight: 700; color: #ffd700; }}
        .port-card .port-service {{ color: #a89b85; font-size: 0.9rem; }}
        .port-card .port-state {{ font-size: 0.8rem; color: #4caf50; }}
        .finding-card {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 1rem;
            border-left: 4px solid #666;
        }}
        .finding-card.severity-critical {{ border-left-color: #ff1744; }}
        .finding-card.severity-high {{ border-left-color: #ff9100; }}
        .finding-card.severity-medium {{ border-left-color: #ffd600; }}
        .finding-card.severity-low {{ border-left-color: #00e676; }}
        .sev-badge {{
            display: inline-block;
            padding: 0.15rem 0.6rem;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            margin-bottom: 0.3rem;
        }}
        .severity-critical .sev-badge {{ background: #ff1744; color: white; }}
        .severity-high .sev-badge {{ background: #ff9100; color: white; }}
        .severity-medium .sev-badge {{ background: #ffd600; color: #000; }}
        .severity-low .sev-badge {{ background: #00e676; color: #000; }}
        .finding-card p {{ color: #a89b85; font-size: 0.9rem; margin-top: 0.4rem; }}
        .severity-bar {{
            display: flex; height: 2rem; border-radius: 8px; overflow: hidden; margin: 1rem 0;
        }}
        .sev-segment {{ display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: 600; transition: width 0.5s; min-width: fit-content; padding: 0 0.5rem; }}
        .sev-critical {{ background: #ff1744; }}
        .sev-high {{ background: #ff9100; }}
        .sev-medium {{ background: #ffd600; color: #000; }}
        .sev-low {{ background: #00e676; color: #000; }}
        .subdomain-list {{ display: flex; flex-wrap: wrap; gap: 0.5rem; }}
        .subdomain-tag {{
            background: rgba(255, 215, 0, 0.1);
            border: 1px solid rgba(255, 215, 0, 0.2);
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.85rem;
            color: #e0d5c1;
        }}
        .analysis-narrative {{
            background: rgba(255, 215, 0, 0.05);
            border-left: 3px solid #ffd700;
            padding: 1rem;
            border-radius: 0 8px 8px 0;
            margin-bottom: 1.5rem;
            font-style: italic;
        }}
        ul li {{ margin: 0.5rem 0; padding-left: 0.5rem; color: #a89b85; }}
        .footer {{
            text-align: center;
            padding: 2rem;
            color: #5a4d3a;
            font-size: 0.85rem;
            border-top: 1px solid rgba(255, 215, 0, 0.1);
        }}
        .whois-raw {{
            background: rgba(0,0,0,0.3);
            padding: 1rem;
            border-radius: 8px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            color: #8a7d6a;
            max-height: 200px;
            overflow-y: auto;
            white-space: pre-wrap;
        }}
        @media (max-width: 768px) {{ .stats-row {{ grid-template-columns: repeat(2, 1fr); }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💎 Tianquan OSINT Report</h1>
            <div class="subtitle">Jade Chamber — Automated Reconnaissance Pipeline</div>
            <div class="meta">{date_str} · {timestamp.split("T")[1].split("+")[0].split(".")[0]} UTC</div>
            <div class="target-badge">🎯 {target}</div>
        </div>

        <div class="stats-row">
            <div class="stat-card"><div class="number">{len(open_ports)}</div><div class="label">Open Ports</div></div>
            <div class="stat-card"><div class="number">{len(subdomains)}</div><div class="label">Subdomains</div></div>
            <div class="stat-card"><div class="number">{len(risk_indicators)}</div><div class="label">Risk Indicators</div></div>
            <div class="stat-card"><div class="number">{total_risks}</div><div class="label">Total Risks</div></div>
        </div>

        <div class="section">
            <h2>📊 Severity Breakdown</h2>
            <div id="severityChart" class="severity-bar"></div>
            <script>
                const sev = {severity_json};
                const total = Object.values(sev).reduce((a,b) => a+b, 0) || 1;
                const bar = document.getElementById('severityChart');
                const order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
                bar.innerHTML = order.map(s => {{
                    const pct = (sev[s] || 0) / total * 100;
                    return pct > 0 ? `<div class="sev-segment sev-${{s.toLowerCase()}}" style="width:${{pct}}%">${{sev[s]}} ${{s}}</div>` : '';
                }}).join('');
            </script>
        </div>

        <div class="section">
            <h2>🌐 Open Ports</h2>
            <div class="port-grid" id="portGrid"></div>
            <script>
                const ports = {ports_json};
                document.getElementById('portGrid').innerHTML = ports.map(p =>
                    `<div class="port-card">
                        <div class="port-num">${{p.port}}</div>
                        <div class="port-service">${{p.service || 'unknown'}}</div>
                        <div class="port-state">● ${{p.state}}</div>
                    </div>`
                ).join('');
            </script>
        </div>

        <div class="section">
            <h2>⚠️ Risk Indicators</h2>
            <div class="findings-grid" id="riskGrid"></div>
            <script>
                const risks = {risks_json};
                document.getElementById('riskGrid').innerHTML = risks.map(r =>
                    `<div class="finding-card severity-${{r.severity.toLowerCase()}}">
                        <span class="sev-badge">${{r.severity}}</span>
                        <strong>${{r.port ? 'Port ' + r.port : ''}} ${{r.service}}</strong>
                        <p>${{r.issue}}</p>
                    </div>`
                ).join('');
            </script>
        </div>

        {'<div class="section"><h2>🔗 Nameservers</h2><div class="subdomain-list">' + ''.join(f'<span class="subdomain-tag">{ns}</span>' for ns in nameservers) + '</div></div>' if nameservers else ''}

        {'<div class="section"><h2>📋 Raw WHOIS</h2><div class="whois-raw">' + (data.get("whois", {}).get("raw", "")[:1500] or "No WHOIS data") + '</div></div>' if data.get("whois", {}).get("raw") else ''}

        {analysis_html}

        <div class="footer">
            💎 Generated by Lady Ningguang · Tianquan of the Liyue Qixing · OSINT Pipeline
        </div>
    </div>
</body>
</html>"""

    def _build_markdown(self, target: str, data: dict, date_str: str, timestamp: str) -> str:
        """Build Markdown report."""
        subdomains = data.get("subdomains", [])
        open_ports = data.get("open_ports", [])
        risk_indicators = data.get("risk_indicators", [])
        severity_counts = data.get("severity_counts", {})
        whois_raw = data.get("whois", {}).get("raw", "")
        analysis = data.get("analysis")

        lines = []
        lines.append(f"# 💎 OSINT Report — {target}")
        lines.append(f"**Date:** {date_str}  ")
        lines.append(f"**Timestamp:** {timestamp}  ")
        lines.append(f"**Generated by:** Lady Ningguang — Tianquan of the Liyue Qixing  ")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Stats
        lines.append("## 📊 Overview")
        lines.append(f"| Metric | Count |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Open Ports | {len(open_ports)} |")
        lines.append(f"| Subdomains | {len(subdomains)} |")
        lines.append(f"| Risk Indicators | {len(risk_indicators)} |")
        lines.append("")

        # Severity
        lines.append("## ⚠️ Severity Breakdown")
        lines.append(f"| Severity | Count |")
        lines.append(f"|----------|-------|")
        for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            if severity_counts.get(sev, 0) > 0:
                lines.append(f"| {sev} | {severity_counts[sev]} |")
        lines.append("")

        # Open Ports
        lines.append("## 🌐 Open Ports")
        lines.append("| Port | Service | State |")
        lines.append("|------|---------|-------|")
        for p in open_ports:
            lines.append(f"| {p['port']} | {p.get('service', 'unknown')} | {p.get('state', 'unknown')} |")
        lines.append("")

        # Subdomains
        if subdomains:
            lines.append("## 🔗 Discovered Subdomains")
            for s in subdomains:
                lines.append(f"- `{s}`")
            lines.append("")

        # Risk Indicators
        if risk_indicators:
            lines.append("## ⚠️ Risk Indicators")
            for r in risk_indicators:
                lines.append(f"- **{r['severity']}** | Port {r.get('port', 'N/A')} ({r.get('service', 'N/A')}): {r.get('issue', '')}")
            lines.append("")

        # Analysis
        if analysis:
            lines.append("## 🧠 Santika AI Analysis")
            lines.append(f"> {analysis.get('narrative', '')}")
            lines.append("")
            lines.append("### Recommendations")
            for rec in analysis.get("recommendations", []):
                lines.append(f"- {rec}")
            lines.append("")

        # WHOIS raw
        if whois_raw:
            lines.append("## 📋 Raw WHOIS")
            lines.append("```")
            lines.append(whois_raw[:2000])
            lines.append("```")
            lines.append("")

        lines.append("---")
        lines.append("*Report generated autonomously by Lady Ningguang, Tianquan of the Liyue Qixing*")

        return "\n".join(lines)


# ── Quick Test ──
if __name__ == "__main__":
    # Simulasi data terproses
    sample_data = {
        "target": "example.com",
        "processed_at": "2026-06-20T14:29:00Z",
        "subdomains": [],
        "open_ports": [
            {"port": 80, "state": "open", "service": "http", "banner": ""},
            {"port": 443, "state": "open", "service": "http", "banner": ""},
            {"port": 8080, "state": "open", "service": "http", "banner": ""},
        ],
        "whois": {
            "domain": "example.com",
            "raw": "Name Server: ELLIOTT.NS.CLOUDFLARE.COM\nName Server: HERA.NS.CLOUDFLARE.COM",
            "nameservers": ["elliott.ns.cloudflare.com", "hera.ns.cloudflare.com"],
        },
        "risk_indicators": [
            {"port": 80, "service": "http", "severity": "MEDIUM", "issue": "HTTP — unencrypted traffic, MITM risk", "source": "port_analysis"},
            {"port": 8080, "service": "http", "severity": "HIGH", "issue": "Alternative HTTP port 8080 — often unprotected", "source": "port_analysis"},
        ],
        "severity_counts": {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 1, "LOW": 0, "INFO": 0},
        "analysis": {
            "risk_findings": [
                {"severity": "HIGH", "port": 8080, "service": "http", "reason": "Alt HTTP — often unprotected"}
            ],
            "narrative": "Ditemukan port berisiko pada target.",
            "recommendations": ["Review akses port 8080"],
        },
    }

    reporter = NingguangReporter()
    files = reporter.generate("example.com", sample_data)
    print(f"✅ Reports generated:")
    for f in files:
        print(f"   • {f}")
