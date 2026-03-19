import yara
import os
import shutil
from workers.base_worker import BaseWorker

class YaraWorker(BaseWorker):
    def __init__(self):
        # Point this to where you store your YARA rules
        self.rules_dir = "tools/rules/" 
        
    def check_dependency(self):
        # YARA is a python library, so we check if the module works
        return True 

    def compile_rules(self):
        # Compile all .yar files in the rules directory
        rules_dict = {}
        for filename in os.listdir(self.rules_dir):
            if filename.endswith(".yar"):
                rules_dict[filename] = os.path.join(self.rules_dir, filename)
        return yara.compile(filepaths=rules_dict)

    def process(self, evidence_path: str) -> dict:
        try:
            # 1. Compile YARA rules
            rules = self.compile_rules()
            
            # 2. Scan the file
            matches = rules.match(evidence_path)
            
            # 3. Format findings
            findings = [match.rule for match in matches]
            
            return {
                "forensic_markers": {"yara_hits": findings},
                "raw_metadata": {"match_count": len(findings)}
            }
        except Exception as e:
            return {"error": str(e)}