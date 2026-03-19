import os
import sys
import json
import datetime
from workers.doc_worker import DocWorker
# from workers.yara_worker import YaraWorker  # Placeholder for your next task

class Orchestrator:
    def __init__(self):
        self.output_dir = "evidence_output"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Phase 2: Register workers by extension
        # In a full system, this would be moved to dispatcher.py
        self.workers = {
            ".pdf": DocWorker(),
            ".docx": DocWorker(),
            ".doc": DocWorker(),
            ".xlsx": DocWorker(),
            ".pptx": DocWorker(),
            # ".exe": YaraWorker(), # Future worker
        }

    def run(self, target_path):
        print(f"[*] Starting Analysis: {target_path}")
        
        # 1. Validation
        if not os.path.exists(target_path):
            print(f"[!] Error: File {target_path} not found.")
            return

        # 2. Triage (Extension Check)
        ext = os.path.splitext(target_path)[1].lower()
        worker = self.workers.get(ext)

        if not worker:
            print(f"[!] No specialized worker found for extension: {ext}. Skipping.")
            return

        # 3. Execution
        print(f"[*] Routing to {worker.worker_name}...")
        results = worker.process(target_path)

        # 4. Evidence Management (Phase 1 Task)
        self.save_evidence(target_path, results)

    def save_evidence(self, original_file, data):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(original_file)
        report_name = f"report_{filename}_{timestamp}.json"
        
        report_path = os.path.join(self.output_dir, report_name)
        
        # Standardize the final container
        final_output = {
            "case_metadata": {
                "scan_time": timestamp,
                "target_file": original_file,
                "status": "Success" if "error" not in data else "Failed"
            },
            "analysis": data
        }

        with open(report_path, "w") as f:
            json.dump(final_output, f, indent=4)
        
        print(f"[SUCCESS] Forensic report generated: {report_path}")

if __name__ == "__main__":
    # Check if user provided a file argument
    if len(sys.argv) < 2:
        print("Usage: python main1.py <path_to_evidence_file>")
        sys.exit(1)

    target = sys.argv[1]
    app = Orchestrator()
    app.run(target)