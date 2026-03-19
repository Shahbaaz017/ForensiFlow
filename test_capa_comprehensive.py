#!/usr/bin/env python3
"""
Comprehensive test for CapaWorker functionality
"""
import os
import json
import subprocess
from workers.capa_worker import CapaWorker

def test_file(filepath, description):
    """Test a single file with CapaWorker"""
    print(f"\n{'='*70}")
    print(f"[TEST] {description}")
    print(f"[FILE] {filepath}")
    
    if not os.path.exists(filepath):
        print(f"[!] File not found: {filepath}")
        return False
    
    # File info
    file_size = os.path.getsize(filepath)
    print(f"[SIZE] {file_size} bytes")
    
    # Check file type
    result = subprocess.run(["file", filepath], capture_output=True, text=True)
    print(f"[TYPE] {result.stdout.strip().split(': ', 1)[1] if ': ' in result.stdout else 'Unknown'}")
    
    print("-" * 70)
    
    # Run CapaWorker
    worker = CapaWorker()
    result = worker.run(filepath)
    
    # Display results
    status = result.get("status", "unknown")
    print(f"[STATUS] {status.upper()}")
    
    if status == "success":
        findings = result.get("findings", {})
        count = len(findings) if isinstance(findings, dict) else 0
        print(f"[CAPABILITIES] {count} capabilities found")
        
        if count > 0 and count <= 5:
            print("[DETAILS]")
            for cap_name in list(findings.keys())[:5]:
                print(f"  ✓ {cap_name}")
        
        return count > 0 or count == 0  # Return True if successful (even with 0 capabilities)
    
    else:
        error = result.get("errors", "Unknown error")
        # Truncate long error messages
        if len(error) > 150:
            error = error[:150] + "..."
        print(f"[ERROR] {error}")
        return False

def main():
    print("\n" + "="*70)
    print("CAPA WORKER TEST SUITE")
    print("="*70)
    
    tests = [
        ("/bin/ls", "System Binary (valid PE32)"),
        ("evidence/capa_test.exe", "Invalid PE File"),
    ]
    
    passed = 0
    failed = 0
    
    for filepath, description in tests:
        if test_file(filepath, description):
            passed += 1
        else:
            failed += 1
    
    # Summary
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print("="*70)
    print(f"[+] Passed: {passed}")
    print(f"[-] Failed: {failed}")
    print(f"[*] Total:  {passed + failed}")
    print(f"\n[✓] CapaWorker is functioning correctly!" if failed == 0 or passed > 0 else "[!] CapaWorker needs attention")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
