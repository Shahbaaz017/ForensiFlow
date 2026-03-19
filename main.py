import os
from core.evidence_manager import EvidenceManager
from core.dispatcher import Dispatcher

def main():
    # 1. Initialize our Forensic Framework
    # The Case Manager handles the "Legal Foundation"
    manager = EvidenceManager("Sample_Investigation_001")
    
    # The Dispatcher acts as the "Brain"
    dispatcher = Dispatcher()

    # 2. Point to the evidence
    target_file = "evidence/Vendor-Evaluation-Criteria-for-AI-Red-Teaming-Providers-Tooling-v1.0.pdf"
    
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
            
            # Display findings if they exist
            findings = data.get("findings")
            if findings:
                # If findings is a dictionary, print key-value pairs
                if isinstance(findings, dict):
                    for key, value in findings.items():
                        print(f"  > {key}: {value}")
                else:
                    print(f"  > {findings}")
            
            # Display errors if they occurred
            if "error" in data:
                print(f"  [!] ERROR: {data['error']}")
    
    print("\n[+] Triage Complete. Check 'output/' for audit logs.")

if __name__ == "__main__":
    main()