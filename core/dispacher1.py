#from workers.doc_worker import DocWorker
from workers.capa_worker import CapaWorker
# We will import other workers here later (disk_worker, etc.)

class Dispatcher:
    def __init__(self):
        # Map extensions to specific workers
        self.routes = {
 #           'pdf': DocWorker(),
  #          'docx': DocWorker(),
            'exe': CapaWorker(),
            'dll': CapaWorker()
        }

    def dispatch(self, evidence_path):
        ext = evidence_path.split('.')[-1].lower()
        worker = self.routes.get(ext)
        
        if worker:
            print(f"[Dispatcher] Routing {evidence_path} to {worker.__class__.__name__}")
            return worker.run(evidence_path)
        else:
            return {"worker": "Dispatcher", "status": "error", "errors": f"No worker for extension: {ext}"}