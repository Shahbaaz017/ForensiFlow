#!/usr/bin/env python3
"""
CapaWorker Test Runner with JSON Report Output
Executes tests and generates structured JSON reports
"""
import os
import json
import subprocess
import sys
from datetime import datetime
from workers.capa_worker import CapaWorker


class CapaTestRunner:
    """Run CapaWorker tests and generate JSON reports"""
    
    def __init__(self, output_dir="evidence_output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def test_file(self, filepath, description):
        """Test a single file and return structured result"""
        result = {
            "filepath": filepath,
            "description": description,
            "exists": os.path.exists(filepath),
            "status": "unknown",
            "file_size": 0,
            "file_type": "unknown",
            "capabilities_count": 0,
            "capabilities": {},
            "error": None
        }
        
        if not result["exists"]:
            result["status"] = "skipped"
            result["error"] = f"File not found: {filepath}"
            return result
        
        # Get file info
        result["file_size"] = os.path.getsize(filepath)
        
        # Get file type
        try:
            proc = subprocess.run(["file", filepath], capture_output=True, text=True)
            if ": " in proc.stdout:
                result["file_type"] = proc.stdout.strip().split(": ", 1)[1]
            else:
                result["file_type"] = proc.stdout.strip()
        except Exception as e:
            result["file_type"] = f"Error detecting: {str(e)}"
        
        # Run CapaWorker
        try:
            worker = CapaWorker()
            worker_result = worker.run(filepath)
            
            result["status"] = worker_result.get("status", "unknown")
            
            if result["status"] == "success":
                findings = worker_result.get("findings", {})
                result["capabilities"] = findings if isinstance(findings, dict) else {}
                result["capabilities_count"] = len(result["capabilities"])
            else:
                result["error"] = worker_result.get("errors", "Unknown error")
                
        except Exception as e:
            result["status"] = "error"
            result["error"] = f"Exception: {str(e)}"
        
        return result
    
    def run_tests(self, test_cases):
        """Run all tests and return results"""
        report = {
            "timestamp": self.timestamp,
            "datetime": datetime.now().isoformat(),
            "test_runner": "CapaWorker Test Suite",
            "total_tests": len(test_cases),
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "tests": []
        }
        
        for filepath, description in test_cases:
            result = self.test_file(filepath, description)
            report["tests"].append(result)
            
            if result["status"] == "success":
                report["passed"] += 1
            elif result["status"] == "skipped":
                report["skipped"] += 1
            else:
                report["failed"] += 1
        
        return report
    
    def save_report(self, report, filename=None):
        """Save report to JSON file"""
        if filename is None:
            filename = f"capa_test_results_{self.timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        return filepath
    
    def print_summary(self, report):
        """Print test summary to console"""
        print("\n" + "="*70)
        print("CAPA WORKER TEST REPORT")
        print("="*70)
        print(f"Timestamp: {report['datetime']}")
        print(f"Total Tests: {report['total_tests']}")
        print(f"  ✓ Passed:  {report['passed']}")
        print(f"  ✗ Failed:  {report['failed']}")
        print(f"  ⊘ Skipped: {report['skipped']}")
        print("\nTest Details:")
        print("-"*70)
        
        for test in report["tests"]:
            status_icon = "✓" if test["status"] == "success" else "✗" if test["status"] == "error" else "⊘"
            print(f"{status_icon} {test['description']}")
            print(f"  File: {test['filepath']}")
            print(f"  Status: {test['status'].upper()}")
            print(f"  Size: {test['file_size']} bytes")
            print(f"  Type: {test['file_type']}")
            
            if test["status"] == "success":
                print(f"  Capabilities: {test['capabilities_count']}")
                if test["capabilities_count"] > 0:
                    for cap_name in list(test["capabilities"].keys())[:3]:
                        print(f"    - {cap_name}")
                    if test["capabilities_count"] > 3:
                        print(f"    ... and {test['capabilities_count'] - 3} more")
            elif test["error"]:
                # Truncate long error messages
                error = test["error"][:120]
                if len(test["error"]) > 120:
                    error += "..."
                print(f"  Error: {error}")
            
            print()
        
        print("="*70)


def main():
    # Define test cases
    test_cases = [
        ("/bin/ls", "System Binary (ELF 64-bit)"),
        ("evidence/capa_test.exe", "Invalid PE File"),
    ]
    
    # Create test runner
    runner = CapaTestRunner()
    
    # Run tests
    print("[*] Running CapaWorker tests...")
    report = runner.run_tests(test_cases)
    
    # Save report
    report_file = runner.save_report(report)
    print(f"\n[+] Report saved to: {report_file}")
    
    # Print summary
    runner.print_summary(report)
    
    # Return exit code based on results
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
