# test_worker.py
import json
from doc_worker import DocWorker

def run_test():
    # 1. Initialize the worker
    worker = DocWorker()
    
    # 2. Check if the tool (ExifTool) is actually installed
    if not worker.check_dependency():
        print("[!] Error: ExifTool is not installed. Run ./setup.sh first.")
        return

    # 3. Define the test file
    target_file = "/workspaces/ForensiFlow/evidence/Vendor-Evaluation-Criteria-for-AI-Red-Teaming-Providers-Tooling-v1.0.pdf"
    
    print(f"[+] Starting analysis on: {target_file}")
    
    # 4. Run the process
    result = worker.process(target_file)
    
    # 5. Pretty print the results
    if "error" in result:
        print(f"[!] Worker Error: {result['error']}")
    else:
        print("\n--- FORENSIC MARKERS ---")
        print(json.dumps(result['forensic_markers'], indent=4))
        
        print("\n--- RAW METADATA (Partial) ---")
        # Just show the first 10 keys so the screen isn't flooded
        raw_keys = list(result['raw_metadata'].keys())[:10]
        for key in raw_keys:
            print(f"{key}: {result['raw_metadata'][key]}")

if __name__ == "__main__":
    run_test()