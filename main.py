from core.evidence_manager import EvidenceManager

def main():
    # 1. Setup our Case
    manager = EvidenceManager("Sample_Investigation_001")

    # 2. Point to a file you want to analyze
    # (Put a file in a folder named 'evidence' first!)
    file_to_analyze = "evidence/Vendor-Evaluation-Criteria-for-AI-Red-Teaming-Providers-Tooling-v1.0.pdf"
    
    # 3. Register the evidence
    try:
        manifest = manager.ingest(file_to_analyze)
        print("--- Evidence Registered Successfully ---")
        print(f"SHA256: {manifest['hashes']['sha256']}")
        print("Check the 'output/' folder for your logs.")
    except FileNotFoundError:
        print(f"Error: Could not find {file_to_analyze}. Please create it first.")

if __name__ == "__main__":
    main()