from core.evidence_manager import EvidenceManager
from core.dispatcher import Dispatcher
import os

def main():
    # 1. Setup Case
    manager = EvidenceManager("Sample_Investigation_001")
    dispatcher = Dispatcher()

    # 2. Define File
    target_file = "evidence/test_virus.exe"
    
    if not os.path.exists(target_file):
        print(f"Error: {target_file} not found.")
        return

    # 3. Register
    manager.ingest(target_file)
    
    # 4. Dispatch (The "Brain" handles the rest)
    report = dispatcher.dispatch(target_file)
    
    # 5. Output
    print(f"Report Status: {report['status']}")
    if report['status'] == 'success':
        print(f"Findings: {report['findings']}")
    else:
        print(f"Error: {report['errors']}")

if __name__ == "__main__":
    main()