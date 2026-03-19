import os
import json
import datetime
from core.evidence_manager import EvidenceManager
from core.dispatcher import Dispatcher

def main():
    # 1. Initialize our Forensic Framework
    # The Case Manager handles the "Legal Foundation"
    manager = EvidenceManager("Sample_Investigation_001")
    
    # The Dispatcher acts as the "Brain"
    dispatcher = Dispatcher()

    # 2. Point to the evidence
    target_file = "evidence/valid_test.exe"  # Change this to your test file in the /evidence folder
    
    if not os.path.exists(target_file):
        print(f"[!] Error: {target_file} not found. Please place it in the /evidence folder.")
        return

    # 3. Phase 1: Evidence Registration (Legal Layer)
    print(f"\n[+] Phase 1: Registering {target_file}...")
    manifest = manager.ingest(target_file)
    print(f"[+] SHA256: {manifest['hashes']['sha256']}")

    # 4. Phase 2: Triage (The Brain/Dispatcher)
    print(f"\n[+] Phase 2: Dispatching workers...")
    report = dispatcher.dispatch(target_file)
    
    # 5. Output the results cleanly
    if report:
        print("\n--- TRIAGE ANALYSIS REPORT ---")
        for worker_name, data in report.get("triage_results", {}).items():
            print(f"\n[Worker: {worker_name.upper()}]")
            
            findings = data.get("findings")
            
            if findings:
                # Display YARA-specific detailed findings
                if worker_name == "yara":
                    fm = findings.get("forensic_markers", {})
                    yara_hits = fm.get("yara_hits", [])
                    match_count = fm.get("match_count", 0)
                    detailed = fm.get("detailed_matches", {})
                    
                    if match_count > 0:
                        print(f"  Matches Found: {match_count}")
                        print(f"  Triggered Rules:")
                        for hit in yara_hits:
                            print(f"    ✓ {hit}")
                        
                        if detailed:
                            print(f"\n  Detailed Findings:")
                            for rule_name, match_data in detailed.items():
                                print(f"    Rule: {rule_name}")
                                if match_data.get("metadata"):
                                    meta = match_data["metadata"]
                                    print(f"      Description: {meta.get('description', 'N/A')}")
                                    print(f"      Severity: {meta.get('severity', 'N/A')}")
                                if match_data.get("matched_strings"):
                                    print(f"      Matched Strings ({len(match_data['matched_strings'])}):")
                                    for s in match_data["matched_strings"][:3]:
                                        print(f"        - Offset {s['offset']}: {repr(s['value'][:40])}")
                                    if len(match_data["matched_strings"]) > 3:
                                        print(f"        ... and {len(match_data['matched_strings']) - 3} more")
                    else:
                        print(f"  No matches found")
                
                # Display other findings as key-value pairs
                elif isinstance(findings, dict):
                    for key, value in findings.items():
                        if isinstance(value, dict):
                            print(f"  {key}:")
                            for k, v in value.items():
                                if isinstance(v, (list, dict)):
                                    print(f"    {k}: {len(v)} items" if isinstance(v, (list, dict)) else f": {v}")
                                else:
                                    print(f"    {k}: {v}")
                        else:
                            print(f"  {key}: {value}")
                else:
                    print(f"  {findings}")
            
            # Display errors if they occurred
            if "error" in data:
                print(f"  [!] ERROR: {data['error']}")
    
    # 6. Save report to JSON in evidence_output
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join("evidence_output", f"forensic_report_{timestamp}.json")

    json_report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "evidence_file": target_file,
        "evidence_hashes": manifest.get("hashes", {}),
        "triage_results": report.get("triage_results", {}),
        "summary": {
            "yara_rules_triggered": len(report.get("triage_results", {}).get("yara", {}).get("findings", {}).get("forensic_markers", {}).get("yara_hits", [])),
            "primary_worker": report.get("triage_results", {}).get("primary", {}).get("status")
        }
    }

    with open(report_path, "w") as f:
        json.dump(json_report, f, indent=2)

    print(f"\n[+] JSON report written to: {report_path}")
    print("\n[+] Triage Complete. Check 'evidence_output/' for audit logs and detailed reports.")

if __name__ == "__main__":
    main()