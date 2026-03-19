import subprocess
import os
from workers.base_worker import BaseWorker

class TimelineWorker(BaseWorker):
    def check_dependency(self):
        # Check if log2timeline is in the system PATH
        return subprocess.call(['which', 'log2timeline'], stdout=subprocess.DEVNULL) == 0

    def process(self, evidence_path: str) -> dict:
        self.log(f"Starting Plaso Timeline Generation on: {evidence_path}")
        
        # Define output paths
        plaso_db = "output/timeline.plaso"
        timeline_csv = "output/timeline.csv"
        
        try:
            # 1. Run log2timeline to create the binary database
            # We use --no-dependencies-check to avoid errors in Codespaces
            subprocess.run(["log2timeline", "--no-dependencies-check", plaso_db, evidence_path], check=True)
            
            # 2. Run psort to export the database to a readable CSV
            subprocess.run(["psort", "-o", "l2tcsv", plaso_db, "-w", timeline_csv], check=True)
            
            return self.create_result(
                "TimelineWorker", 
                "success", 
                findings={"csv_path": timeline_csv, "db_path": plaso_db}
            )
            
        except subprocess.CalledProcessError as e:
            return self.create_result("TimelineWorker", "error", errors=f"Plaso failed: {str(e)}")