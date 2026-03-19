import subprocess
import os
from workers.base_worker import BaseWorker

class DiskWorker(BaseWorker):
    def process(self, evidence_path: str) -> dict:
        self.log(f"Deep Disk Analysis started: {evidence_path}")
        
        try:
            # 1. Map Partitions (mmls)
            mmls_output = subprocess.check_output(["mmls", evidence_path], text=True)
            partition_offset = self._find_main_partition(mmls_output)
            
            if not partition_offset:
                return self.create_result("DiskWorker", "error", errors="No data partition found.")

            # 2. Get File System Stats (fsstat)
            # This tells us if it's NTFS, FAT32, etc. and the Block Size
            fs_info = subprocess.check_output(["fsstat", "-o", partition_offset, evidence_path], text=True)
            fs_type = "Unknown"
            for line in fs_info.splitlines():
                if "File System Type:" in line:
                    fs_type = line.split(":")[1].strip()

            # 3. List Files (fls)
            # We'll grab the first 20 files found to show in the report
            fls_output = subprocess.check_output(["fls", "-r", "-p", "-o", partition_offset, evidence_path], text=True)
            file_list = self._parse_fls(fls_output)

            # 4. DATA CARVING EXAMPLE: Extract a specific interesting file (icat)
            # Let's say we find an EXE on the disk. We can extract it for Capa!
            extracted_path = None
            for file in file_list:
                if file['path'].endswith(".exe"):
                    extracted_path = self.extract_file(evidence_path, partition_offset, file['inode'], "extracted_suspect.exe")
                    break

            return self.create_result(
                worker_name="DiskWorker-TSK",
                status="success",
                findings={
                    "fs_type": fs_type,
                    "partition_offset": partition_offset,
                    "total_files": len(file_list),
                    "sample_files": file_list[:10],  # Show a sample in the report
                    "extracted_evidence": extracted_path if extracted_path else "None found"
                }
            )

        except Exception as e:
            return self.create_result("DiskWorker", "error", errors=str(e))

    def extract_file(self, img_path, offset, inode, output_name):
        """
        The 'icat' magic: Extracting raw bytes from a disk image based on Inode.
        This allows you to analyze a file even if the OS is locked.
        """
        output_dir = "evidence_output/extracted"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        target_path = os.path.join(output_dir, output_name)
        
        # icat -o [offset] [image] [inode] > [output_file]
        with open(target_path, "wb") as f:
            cmd = ["icat", "-o", offset, img_path, inode]
            subprocess.run(cmd, stdout=f)
        
        return target_path

    def _find_main_partition(self, mmls_output):
        for line in mmls_output.splitlines():
            if any(x in line for x in ["Linux", "Win95", "NTFS", "0x83", "0x07"]):
                return line.split()[2] # The 'Start' sector column
        return None

    def _parse_fls(self, output):
        files = []
        for line in output.splitlines():
            if ":" in line:
                meta, path = line.split(":", 1)
                files.append({
                    "path": path.strip(),
                    "inode": meta.split()[-1].replace("*", ""), # Remove the 'deleted' asterisk
                    "is_deleted": "*" in meta
                })
        return files