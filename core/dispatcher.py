from workers.doc_worker import DocWorker
from workers.capa_worker import CapaWorker
from workers.yara_worker import YaraWorker
from workers.disk_worker import DiskWorker

class Dispatcher:
    def __init__(self):
        # The primary worker is based on extension
        self.primary_workers = {
            'pdf': DocWorker(),
            'docx': DocWorker(),
            'exe': CapaWorker(),
            'dll': CapaWorker(),
            ".img": DiskWorker(),  # <--- Register disk images
            ".dd": DiskWorker(),   # <--- Register raw dumps
            ".raw": DiskWorker()
        }
        # YARA runs on EVERYTHING as a baseline triage
        self.baseline_worker = YaraWorker()

    def dispatch(self, evidence_path):
        ext = evidence_path.split('.')[-1].lower()
        primary_worker = self.primary_workers.get(ext)
        
        results = {
            "file": evidence_path,
            "triage_results": {}
        }

        # 1. Run Baseline Triage (YARA)
        print(f"[Dispatcher] Running Baseline (YARA) on {evidence_path}")
        results["triage_results"]["yara"] = self._run_worker(self.baseline_worker, evidence_path)

        # 2. Run Primary Worker (Doc or Capa)
        if primary_worker:
            print(f"[Dispatcher] Running Primary ({primary_worker.__class__.__name__}) on {evidence_path}")
            results["triage_results"]["primary"] = self._run_worker(primary_worker, evidence_path)
        else:
            results["triage_results"]["primary"] = {"status": "skipped", "error": "No primary worker for this type."}

        return results

    def _run_worker(self, worker, path):
        """Helper to ensure every worker follows the same error-handling flow."""
        try:
            # Check dependency first
            if hasattr(worker, 'check_dependency') and not worker.check_dependency():
                return {"status": "error", "error": "Dependency check failed."}
            
            # Call the run() method which uses standardized create_result() formatting
            return worker.run(path)
        except Exception as e:
            return {"status": "error", "error": str(e)}