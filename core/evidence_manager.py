import hashlib
import json
import datetime
import os

class EvidenceManager:
    def __init__(self, case_name):
        self.case_name = case_name
        self.manifest_path = f"evidence_output/{case_name}_manifest.json"
        self.audit_log = f"evidence_output/{case_name}_audit.log"
        
        # Ensure output directory exists
        if not os.path.exists("evidence_output"):
            os.makedirs("evidence_output")

    def calculate_hashes(self, file_path):
        """Generates SHA256 and MD5 hashes for integrity."""
        sha256 = hashlib.sha256()
        md5 = hashlib.md5()
        
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
                md5.update(chunk)
        
        return {"sha256": sha256.hexdigest(), "md5": md5.hexdigest()}

    def log_action(self, action, details):
        """Records every tool/action in an audit log for court evidence."""
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"[{timestamp}] {action}: {details}\n"
        with open(self.audit_log, "a") as f:
            f.write(log_entry)
        print(log_entry.strip())

    def ingest(self, file_path):
        """Registers new evidence and creates the legal manifest."""
        print(f"Registering evidence: {file_path}")
        hashes = self.calculate_hashes(file_path)
        
        manifest = {
            "case_name": self.case_name,
            "evidence_file": file_path,
            "hashes": hashes,
            "ingestion_time": str(datetime.datetime.now())
        }
        
        with open(self.manifest_path, "w") as f:
            json.dump(manifest, f, indent=4)
            
        self.log_action("INGESTION", f"Evidence registered with SHA256: {hashes['sha256']}")
        return manifest

# Quick test if you run this script directly
if __name__ == "__main__":
    manager = EvidenceManager("Test_Case_001")
    # manager.ingest("evidence/my_disk_image.e01") # Uncomment and point to a real file