#!/usr/bin/env python3
"""
🏛️ OSINT Pipeline Orchestrator
Project A — Automated Security Recon Pipeline

Alur:
  1. Baca targets.txt
  2. Untuk setiap target → panggil SantikaIntegration (OSINT)
  3. Proses & dedup data via DataProcessor
  4. Generate report HTML/MD via NingguangReporter
  5. Simpan ke output/ & reports/

Usage:
  python orchestrator.py                     # Semua target
  python orchestrator.py --target example.com # Satu target spesifik
  python orchestrator.py --demo              # Mode demo dengan data sample
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ── Path Constants ──
BASE_DIR = Path(__file__).resolve().parent.parent
PIPELINE_DIR = BASE_DIR / "pipeline"
TARGETS_FILE = PIPELINE_DIR / "targets.txt"
OUTPUT_DIR = BASE_DIR / "output"
REPORTS_DIR = BASE_DIR / "reports"
SAMPLE_DIR = REPORTS_DIR / "sample"

sys.path.insert(0, str(PIPELINE_DIR))

from santika_integration import SantikaIntegration
from data_processor import DataProcessor
from ningguang_reporter import NingguangReporter


def load_targets(target_file: Path) -> list[str]:
    """Load targets from file, skipping comments and blank lines."""
    if not target_file.exists():
        print(f"[!] Targets file not found: {target_file}")
        return []
    targets = []
    with open(target_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                targets.append(line)
    return targets


def ensure_dirs():
    """Create output directories if they don't exist."""
    for d in [OUTPUT_DIR, REPORTS_DIR, SAMPLE_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def run_pipeline(targets: list[str], demo_mode: bool = False) -> dict:
    """
    Execute full OSINT pipeline for all targets.
    Returns summary dict.
    """
    ensure_dirs()
    santika = SantikaIntegration()
    processor = DataProcessor()
    reporter = NingguangReporter()

    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    timestamp = datetime.utcnow().isoformat() + "Z"

    # Cek koneksi Santika dulu
    health = santika.health_check()
    if health.get("status") != "ok":
        print(f"[!] Santika API tidak merespon: {health}")
        print("[!] Pipeline dihentikan — pastikan Santika API berjalan di 10.10.10.100:8266")
        return {"timestamp": timestamp, "date": date_str, "targets_scanned": 0, "findings_per_target": {}, "errors": [{"target": "system", "error": f"Santika unavailable: {health}"}]}

    print(f"  ✓ Santika API terdeteksi di {santika.base_url}")

    summary = {
        "timestamp": timestamp,
        "date": date_str,
        "targets_scanned": 0,
        "findings_per_target": {},
        "errors": [],
    }

    print(f"{'='*60}")
    print(f"  💎 TIANQUAN OSINT PIPELINE")
    print(f"  {timestamp}")
    print(f"{'='*60}")
    print(f"  Targets: {len(targets)}")
    print(f"{'='*60}\n")

    for target in targets:
        print(f"\n──▶ Scanning: {target}")
        try:
            # Step 1: Santika OSINT collection
            print(f"  [1/3] OSINT Reconnaissance...")
            analyze_mode = os.environ.get("SANTIKA_ANALYZE", "false").lower() == "true"
            raw_data = santika.collect(target, analyze=analyze_mode)
            # Save raw data
            target_output = OUTPUT_DIR / target.replace("/", "_").replace(":", "_")
            target_output.mkdir(parents=True, exist_ok=True)
            raw_path = target_output / "raw_osint.json"
            with open(raw_path, "w") as f:
                json.dump(raw_data, f, indent=2)
            print(f"       ✓ Raw data saved: {raw_path}")

            # Step 2: Data processing & dedup
            print(f"  [2/3] Processing & Deduplication...")
            processed = processor.process(raw_data, target)
            processed_path = target_output / "processed_osint.json"
            with open(processed_path, "w") as f:
                json.dump(processed, f, indent=2)
            print(f"       ✓ Processed data saved: {processed_path}")

            # Step 3: Report generation
            print(f"  [3/3] Generating Reports...")
            report_files = reporter.generate(
                target=target,
                data=processed,
                output_dir=REPORTS_DIR,
                date_str=date_str,
                timestamp=timestamp,
            )
            print(f"       ✓ Reports generated:")
            for rf in report_files:
                print(f"         • {rf}")

            summary["targets_scanned"] += 1
            summary["findings_per_target"][target] = {
                "subdomains": len(processed.get("subdomains", [])),
                "open_ports": processed.get("open_ports", []),
                "tech_stack": processed.get("tech_stack", []),
                "risk_indicators": len(processed.get("risk_indicators", [])),
                "severity_breakdown": processed.get("severity_counts", {}),
            }

        except Exception as e:
            error_msg = f"[!] Error scanning {target}: {str(e)}"
            print(f"  {error_msg}")
            summary["errors"].append({"target": target, "error": str(e)})

    # Save pipeline summary
    summary_path = OUTPUT_DIR / f"pipeline-summary-{date_str}.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n{'='*60}")
    print(f"  ✅ PIPELINE COMPLETE")
    print(f"  Targets scanned: {summary['targets_scanned']}/{len(targets)}")
    print(f"  Errors: {len(summary['errors'])}")
    print(f"  Summary saved: {summary_path}")
    print(f"{'='*60}")

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="💎 Tianquan OSINT Pipeline — Project A"
    )
    parser.add_argument("--target", "-t", help="Single target domain/IP")
    args = parser.parse_args()

    if args.target:
        targets = [args.target]
    else:
        targets = load_targets(TARGETS_FILE)

    if not targets:
        print("[!] No targets provided. Add domains to targets.txt or use --target")
        sys.exit(1)

    summary = run_pipeline(targets)

    # Exit code: 0 if all succeeded, 1 if any errors
    sys.exit(1 if summary["errors"] else 0)


if __name__ == "__main__":
    main()
