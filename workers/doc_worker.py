import subprocess
import json
import os
from typing import Dict, Any
# Assuming BaseWorker is in workers/base_worker.py
from workers.base_worker import BaseWorker

class DocWorker(BaseWorker):
    def __init__(self):
        super().__init__(worker_name="DocWorker-ExifTool")
        self.supported_extensions = [
            ".pdf", ".docx", ".doc", ".xlsx", ".xls", 
            ".pptx", ".ppt", ".odt", ".rtf"
        ]

    def check_dependency(self) -> bool:
        """Verify that exiftool is installed on the system."""
        try:
            subprocess.run(["exiftool", "-ver"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def run(self, file_path: str) -> Dict[str, Any]:
        """Implements BaseWorker abstract run by delegating to process."""
        return self.process(file_path)

    def process(self, file_path: str) -> Dict[str, Any]:
        """
        Executes ExifTool on the target file and returns structured JSON.
        """
        if not os.path.exists(file_path):
            return {"error": f"File {file_path} not found."}

        if not self.check_dependency():
            return {"error": "ExifTool is not installed or not in PATH."}

        try:
            # -j: Output in JSON format
            # -g: Group headings (allows us to see 'System', 'File', 'PDF' groups)
            # --fast: Speed up processing by not reading to end of file
            result = subprocess.run(
                ["exiftool", "-j", "-g", file_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            # ExifTool returns a list containing one dictionary per file
            raw_data = json.loads(result.stdout)
            if raw_data:
                return self._standardize_output(raw_data[0])
            return {"error": "No metadata returned."}

        except Exception as e:
            return {"error": f"ExifTool execution failed: {str(e)}"}

    def _standardize_output(self, raw_metadata: Dict) -> Dict[str, Any]:
        """
        Extracts high-value forensic keys into a predictable format 
        for Phase 3's Unified Reporting.
        """
        # Flattening the 'Group' structure slightly for easier correlation
        flat_data = {}
        for group, tags in raw_metadata.items():
            if isinstance(tags, dict):
                for tag, value in tags.items():
                    flat_data[f"{group}:{tag}"] = value
            else:
                flat_data[group] = tags

        # Extracting Key Forensics Markers
        standardized = {
            "worker": self.worker_name,
            "forensic_markers": {
                "author": flat_data.get("PDF:Author") or flat_data.get("File:Creator") or "Unknown",
                "creation_date": flat_data.get("PDF:CreateDate") or flat_data.get("File:FileModifyDate"),
                "modification_date": flat_data.get("PDF:ModifyDate") or flat_data.get("File:FileAccessDate"),
                "software_used": flat_data.get("PDF:Producer") or flat_data.get("File:Software") or "Unknown",
                "page_count": flat_data.get("PDF:PageCount") or "N/A"
            },
            "raw_metadata": raw_metadata
        }
        return standardized

# Quick Test logic
if __name__ == "__main__":
    worker = DocWorker()
    # Replace with a path to a local document for testing
    test_file = "evidence_sample.pdf"
    if os.path.exists(test_file):
        report = worker.process(test_file)
        print(json.dumps(report, indent=4))
    else:
        print(f"Please provide a valid file at {test_file} to test.")