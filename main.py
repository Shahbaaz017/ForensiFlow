import os
import sys
import json
import datetime
from core.evidence_manager import EvidenceManager
from workers.doc_worker import DocWorker

class Orchestrator:
    def __init__(self, output_dir="evidence_output"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.workers = {
            ".pdf": DocWorker(),
            ".docx": DocWorker(),
            ".doc": DocWorker(),
            ".xlsx": DocWorker(),
            ".pptx": DocWorker(),
        }

    def run(self, target_path: str):
        if not os.path.exists(target_path):
            return {"status": "error", "error": f"File not found: {target_path}"}

        ext = os.path.splitext(target_path)[1].lower()
        worker = self.workers.get(ext)
        if not worker:
            return {"status": "skipped", "error": f"No worker for extension: {ext}"}

        result = worker.run(target_path)
        self.save_evidence(target_path, result)
        return {"status": "success" if "error" not in result else "failed", "result": result}

    def save_evidence(self, original_file, data):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(original_file)
        report_name = f"report_{filename}_{timestamp}.json"
        report_path = os.path.join(self.output_dir, report_name)

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


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <evidence_file> [case_name]")
        sys.exit(1)

    evidence_file = sys.argv[1]
    case_name = sys.argv[2] if len(sys.argv) > 2 else "Sample_Investigation_001"

    if not os.path.exists(evidence_file):
        print(f"Error: {evidence_file} not found.")
        sys.exit(1)

    manager = EvidenceManager(case_name)
    manager.ingest(evidence_file)

    orchestrator = Orchestrator()
    report = orchestrator.run(evidence_file)

    print(f"Report Status: {report['status']}")
    if report["status"] == "success":
        print(json.dumps(report["result"], indent=2))
    else:
        print(f"Error: {report.get('error')}")


if __name__ == "__main__":
    main()