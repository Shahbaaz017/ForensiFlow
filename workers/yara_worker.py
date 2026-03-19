import yara
import os
import shutil
from workers.base_worker import BaseWorker

class YaraWorker(BaseWorker):
    def __init__(self):
        super().__init__(worker_name="YaraWorker")
        # Point this to where you store your YARA rules
        self.rules_dir = "tools/rules/" 
        
    def check_dependency(self):
        # YARA is a python library, so we check if the module works
        return True 

    def compile_rules(self):
        # Compile all .yar files in the rules directory
        rules_dict = {}
        
        if not os.path.exists(self.rules_dir):
            self.log(f"Rules directory not found: {self.rules_dir}")
            return None
        
        for filename in os.listdir(self.rules_dir):
            if filename.endswith(".yar"):
                rules_dict[filename] = os.path.join(self.rules_dir, filename)
        
        if not rules_dict:
            self.log(f"No YARA rules found in {self.rules_dir}")
            return None
        
        self.log(f"Compiling {len(rules_dict)} YARA rules...")
        return yara.compile(filepaths=rules_dict)

    def run(self, evidence_path: str) -> dict:
        """Implements the required abstract run method."""
        self.log(f"Starting YARA analysis on: {evidence_path}")
        try:
            result = self.process(evidence_path)
            if "error" in result:
                return self.create_result("YaraWorker", "error", errors=result["error"])
            return self.create_result("YaraWorker", "success", findings=result)
        except Exception as e:
            self.log(f"Critical error: {str(e)}")
            return self.create_result("YaraWorker", "error", errors=str(e))

    def process(self, evidence_path: str) -> dict:
        try:
            # 1. Compile YARA rules
            rules = self.compile_rules()
            
            if rules is None:
                return {
                    "forensic_markers": {"yara_hits": [], "match_count": 0},
                    "raw_metadata": {"match_count": 0, "scan_file": evidence_path, "note": "No rules found"}
                }
            
            # 2. Scan the file
            matches = rules.match(evidence_path)
            
            # 3. Extract detailed findings from matches
            findings = self._extract_detailed_matches(matches)
            
            return {
                "forensic_markers": {
                    "yara_hits": list(findings.keys()),
                    "match_count": len(findings),
                    "detailed_matches": findings
                },
                "raw_metadata": {
                    "match_count": len(findings),
                    "scan_file": evidence_path
                }
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _extract_detailed_matches(self, matches) -> dict:
        """Extract detailed information from YARA matches"""
        detailed_findings = {}
        
        for match in matches:
            rule_name = match.rule
            
            # Extract rule metadata
            rule_meta = {
                "rule_name": rule_name,
                "tags": match.tags if hasattr(match, 'tags') else [],
                "metadata": match.meta if hasattr(match, 'meta') else {},
                "matched_strings": []
            }
            
            # Extract matched strings with offsets
            if hasattr(match, 'strings') and match.strings:
                for string_match in match.strings:
                    try:
                        # Each item in match.strings is a StringMatch object with attributes:
                        # instances: list of (offset, data) tuples
                        if hasattr(string_match, 'instances'):
                            for instance in string_match.instances:
                                offset = instance.offset
                                matched_data = instance.matched_data
                                
                                rule_meta["matched_strings"].append({
                                    "offset": offset,
                                    "identifier": string_match.identifier,
                                    "value": matched_data.decode('utf-8', errors='ignore') if isinstance(matched_data, bytes) else str(matched_data),
                                    "size": len(matched_data) if isinstance(matched_data, bytes) else len(str(matched_data))
                                })
                    except (AttributeError, IndexError) as e:
                        self.log(f"Error processing string match: {e}")
                        continue
            
            detailed_findings[rule_name] = rule_meta
        
        return detailed_findings