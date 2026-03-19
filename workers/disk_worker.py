import subprocess
import re
import os
from workers.base_worker import BaseWorker

class DiskWorker(BaseWorker):
    def process(self, evidence_path: str) -> dict:
        self.log(f"Starting Sleuth Kit analysis on: {evidence_path}")
        
        if not os.path.exists(evidence_path):
            return self.create_result("DiskWorker", "error", errors="Image file not found.")

        try:
            # 1. Run mmls to find partitions
            # mmls identifies the partition table (DOS, GPT, etc.)
            mmls_cmd = ["mmls", evidence_path]
            mmls_result = subprocess.run(mmls_cmd, capture_output=True, text=True)
            
            if mmls_result.returncode != 0:
                return self.create_result("DiskWorker", "error", errors="mmls failed to read partition table.")

            # 2. Extract the start sector of the largest Data/Linux/NTFS partition
            # We use Regex to find the partition that isn't 'Unallocated' or 'Table'
            partition_start = self._find_main_partition(mmls_result.stdout)
            
            if not partition_start:
                return self.create_result("DiskWorker", "error", errors="Could not find a valid data partition.")

            # 3. Run fls to list files (Recursive -r, Display Path -p)
            # -o is the offset (where the partition starts)
            fls_cmd = ["fls", "-r", "-p", "-o", partition_start, evidence_path]
            fls_result = subprocess.run(fls_cmd, capture_output=True, text=True)

            # 4. Parse the fls text output into a structured list
            file_system_map = self._parse_fls(fls_result.stdout)

            return self.create_result(
                worker_name="DiskWorker-TSK",
                status="success",
                findings={
                    "partition_offset": partition_start,
                    "total_files_found": len(file_system_map),
                    "file_system_hierarchy": file_system_map[:50]  # Return top 50 for summary
                }
            )

        except Exception as e:
            return self.create_result("DiskWorker", "error", errors=str(e))

    def _find_main_partition(self, mmls_output):
        """Simple logic to find the starting sector of the primary data partition."""
        lines = mmls_output.splitlines()
        for line in lines:
            # Look for common data partition types (Linux, NTFS, Win95)
            if any(x in line for x in ["Linux", "Win95", "NTFS", "0x83", "0x07"]):
                parts = line.split()
                # Usually the start sector is the 3rd column in mmls output
                return parts[2]
        return None

    def _parse_fls(self, fls_output):
        """Parses fls output lines like: 'r/r 12345: /folder/file.txt'"""
        files = []
        for line in fls_output.splitlines():
            if ":" in line:
                meta, path = line.split(":", 1)
                file_type = "Deleted" if "*" in meta else "Allocated"
                files.append({
                    "path": path.strip(),
                    "status": file_type,
                    "inode": meta.split()[-1]
                })
        return files

    def create_result(self, worker_name, status, findings=None, errors=None):
        return {
            "worker": worker_name,
            "status": status,
            "findings": findings or {},
            "error": errors
        }