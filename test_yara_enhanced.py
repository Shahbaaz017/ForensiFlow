#!/usr/bin/env python3
"""
Test enhanced YaraWorker with detailed match extraction
"""
import json
from workers.yara_worker import YaraWorker

def test_yara_worker():
    print("\n" + "="*70)
    print("ENHANCED YARA WORKER TEST")
    print("="*70)
    
    worker = YaraWorker()
    
    # Test with the PDF first
    test_file = "evidence/Vendor-Evaluation-Criteria-for-AI-Red-Teaming-Providers-Tooling-v1.0.pdf"
    
    print(f"\n[*] Scanning: {test_file}")
    print(f"[*] Rules directory: {worker.rules_dir}")
    
    result = worker.run(test_file)
    
    print("\n[+] YARA Worker Result:")
    print(json.dumps(result, indent=2))
    
    # Summary
    if result.get("status") == "success":
        findings = result.get("findings", {})
        yara_hits = findings.get("forensic_markers", {}).get("yara_hits", [])
        match_count = findings.get("forensic_markers", {}).get("match_count", 0)
        
        print("\n" + "-"*70)
        print(f"[+] Scan Complete!")
        print(f"[+] Matches Found: {match_count}")
        print(f"[+] Rules Triggered:")
        for hit in yara_hits:
            print(f"    ✓ {hit}")
        
        # Show detailed matches
        detailed = findings.get("forensic_markers", {}).get("detailed_matches", {})
        if detailed:
            print(f"\n[+] Detailed Matches:")
            for rule_name, match_data in detailed.items():
                print(f"\n    Rule: {rule_name}")
                if match_data.get("metadata"):
                    print(f"    Metadata: {match_data['metadata']}")
                if match_data.get("matched_strings"):
                    print(f"    Matched Strings ({len(match_data['matched_strings'])}):")
                    for s in match_data["matched_strings"][:3]:  # Show first 3
                        print(f"      - Offset {s['offset']}: {s['identifier']} = {repr(s['value'][:50])}")
                    if len(match_data["matched_strings"]) > 3:
                        print(f"      ... and {len(match_data['matched_strings']) - 3} more matches")
    else:
        print(f"\n[!] Error: {result.get('findings', {}).get('error', 'Unknown error')}")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    test_yara_worker()
