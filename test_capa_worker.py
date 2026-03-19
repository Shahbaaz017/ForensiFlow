#!/usr/bin/env python3
"""
Test script to verify CapaWorker functionality with test executables
"""
import os
import json
from workers.capa_worker import CapaWorker

def test_file(test_file):
    """Test a single file with CapaWorker"""
    print(f"\n{'='*60}")
    print(f"[+] Testing CapaWorker with: {test_file}")
    
    if not os.path.exists(test_file):
        print(f"[!] Error: {test_file} not found")
        return
    
    print(f"[+] File size: {os.path.getsize(test_file)} bytes")
    print("-" * 60)
    
    # Initialize the CapaWorker
    worker = CapaWorker()
    
    # Run the worker
    result = worker.run(test_file)
    
    # Display results
    print("\n[+] CapaWorker Result:")
    print(json.dumps(result, indent=2))
    
    # Summary
    print("\n" + "-" * 60)
    if result.get("status") == "success":
        findings = result.get("findings", {})
        print(f"[+] SUCCESS: Found {len(findings)} capabilities")
        if findings:
            print(f"[+] Capabilities detected:")
            for cap_name, cap_details in findings.items():
                print(f"    - {cap_name}")
    else:
        print(f"[!] FAILED: {result.get('errors', 'Unknown error')}")

def main():
    # Test both files
    test_files_list = [
        "evidence/capa_test.exe",      # Original test file (invalid PE)
        "evidence/valid_test.exe"       # Valid PE file we just created
    ]
    
    for file_path in test_files_list:
        test_file(file_path)
    
    print(f"\n{'='*60}")
    print("[+] All tests completed!")

if __name__ == "__main__":
    main()

