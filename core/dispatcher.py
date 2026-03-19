from workers.doc_worker import DocWorker
from workers.capa_worker import CapaWorker

class Dispatcher:
    def __init__(self):
        # Initialize all workers
        self.workers = {
            'pdf': DocWorker(),
            'docx': DocWorker(),
            'exe': CapaWorker(),
            'dll': CapaWorker()
        }

    def dispatch(self, evidence_path):
        # 1. Get file extension
        ext = evidence_path.split('.')[-1].lower()
        worker = self.workers.get(ext)
        
        if not worker:
            return {"status": "error", "error": f"No worker available for extension: {ext}"}

        # 2. Check Dependency (The "Friend's" logic added here)
        # We assume every worker has a check_dependency() method now
        if hasattr(worker, 'check_dependency') and not worker.check_dependency():
            return {"status": "error", "error": f"Tool for {worker.__class__.__name__} is not installed."}

        # 3. Process the file
        print(f"[Dispatcher] Routing {evidence_path} to {worker.__class__.__name__}")
        try:
            result = worker.process(evidence_path)
            if isinstance(result, dict) and "error" in result:
                return {"status": "failed", "error": result.get("error"), "result": result}
            return {"status": "success", "findings": result, "result": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}