from core.evidence_manager import EvidenceManager
from workers.capa_worker import CapaWorker
import os

def main():
    # 1. Setup our Case
    case_name = "Sample_Investigation_001"
    manager = EvidenceManager(case_name)

    # 2. Define the evidence file
    target_file = "evidence/test_virus.exe"  # Change this to your actual test file path
    
    # 3. Check if file exists before proceeding
    if not os.path.exists(target_file):
        print(f"Error: {target_file} not found.")
        return

    # 4. Register the evidence (Phase 1)
    manifest = manager.ingest(target_file)
    print(f"--- Evidence Registered: {manifest['hashes']['sha256']} ---")

    # 5. Route to Worker (Phase 2 - Triage)
    # We check if the file is an executable before running Capa
    if target_file.lower().endswith(('.exe', '.dll', '.bin')):
        print("Detected Executable: Running CapaWorker...")
        worker = CapaWorker()
        report = worker.run(target_file)
        print(f"Analysis Results: {report['status']}")
    else:
        print(f"Skipping Capa: {target_file} is not an executable.")

if __name__ == "__main__":
    main()