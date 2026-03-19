import subprocess
import json
import os
from workers.base_worker import BaseWorker

class CapaWorker(BaseWorker):
    def __init__(self):
        super().__init__(worker_name="CapaWorker")
        # Point to the capa rules directory
        self.rules_dir = "tools/rules_db"
    
    def run(self, evidence_path: str) -> dict:
        self.log(f"Starting capability analysis on: {evidence_path}")
        
        try:
            # 1. Run Capa as a subprocess
            # We use --json to get a clean machine-readable format
            # We provide the rules directory via -r option
            cmd = ["capa", "-r", self.rules_dir, "--json", evidence_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # 2. Check for tool failure
            if result.returncode != 0 and result.returncode != 1:
                error_msg = result.stderr if result.stderr else "Capa failed to execute."
                return self.create_result("CapaWorker", "error", errors=error_msg)

            # 3. Parse the output
            # Capa returns a JSON object with a 'capabilities' key
            # Handle both stdout and stderr for output
            output_text = result.stdout if result.stdout else result.stderr
            if not output_text.strip():
                return self.create_result("CapaWorker", "success", findings={})
            
            capa_json = json.loads(output_text)
            
            # 4. Return the standardized result
            return self.create_result(
                worker_name="CapaWorker",
                status="success",
                findings=capa_json.get("capabilities", {})
            )
            
        except Exception as e:
            self.log(f"Critical error: {str(e)}")
            return self.create_result("CapaWorker", "error", errors=str(e))