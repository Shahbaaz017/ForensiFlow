import subprocess
import json
from workers.base_worker import BaseWorker

class CapaWorker(BaseWorker):
    def run(self, evidence_path: str) -> dict:
        self.log(f"Starting capability analysis on: {evidence_path}")
        
        try:
            # 1. Run Capa as a subprocess
            # We use --json to get a clean machine-readable format
            cmd = ["capa", "--json", evidence_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # 2. Check for tool failure
            if result.returncode != 0 and result.returncode != 1:
                return self.create_result("CapaWorker", "error", errors="Capa failed to execute.")

            # 3. Parse the output
            # Capa returns a JSON object with a 'capabilities' key
            capa_json = json.loads(result.stdout)
            
            # 4. Return the standardized result
            return self.create_result(
                worker_name="CapaWorker",
                status="success",
                findings=capa_json.get("capabilities", {})
            )
            
        except Exception as e:
            self.log(f"Critical error: {str(e)}")
            return self.create_result("CapaWorker", "error", errors=str(e))