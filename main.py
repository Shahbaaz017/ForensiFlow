import os
import sys
import json
import datetime
from core.evidence_manager import EvidenceManager
from core.dispatcher import Dispatcher


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

    dispatcher = Dispatcher()
    report = dispatcher.dispatch(evidence_file)

    status = report.get("status", "error")
    print(f"Report Status: {status}")

    # Save JSON report to evidence_output
    os.makedirs("evidence_output", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_name = os.path.basename(evidence_file)
    report_file = f"evidence_output/report_{report_name}_{timestamp}.json"

    saved_report = {
        "case_name": case_name,
        "target_file": evidence_file,
        "status": status,
        "result": report,
    }

    with open(report_file, "w") as f:
        json.dump(saved_report, f, indent=2)

    print(f"Saved JSON report: {report_file}")

    if status == "success":
        findings = report.get("findings") or report.get("result")
        print("Findings:")
        print(json.dumps(findings, indent=2))
    else:
        print(f"Error: {report.get('error')}")
        if report.get("result"):
            print(json.dumps(report.get("result"), indent=2))


if __name__ == "__main__":
    main()