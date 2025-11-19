"""Generated code output directory for AI-created software components"""

import os
import json
from datetime import datetime
from pathlib import Path

class GeneratedCodeManager:
    """Manager for generated code output files"""
    
    def __init__(self, base_path: str = "outputs/generated_code"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save_generated_code(self, code: str, filename: str, metadata: dict = None):
        """Save generated code to file with metadata"""
        file_path = self.base_path / filename
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save code
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # Save metadata
        if metadata:
            meta_path = file_path.with_suffix('.meta.json')
            metadata['generated_at'] = datetime.now().isoformat()
            metadata['file_size'] = len(code)
            
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
        
        return str(file_path)
    
    def list_generated_files(self, pattern: str = "*"):
        """List all generated code files"""
        return list(self.base_path.rglob(pattern))
    
    def get_code_statistics(self):
        """Get statistics about generated code"""
        files = list(self.base_path.rglob("*.py")) + list(self.base_path.rglob("*.js")) + \
                list(self.base_path.rglob("*.java")) + list(self.base_path.rglob("*.cpp"))
        
        total_files = len(files)
        total_lines = 0
        total_size = 0
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    total_lines += content.count('\n')
                    total_size += len(content)
            except:
                continue
        
        return {
            'total_files': total_files,
            'total_lines': total_lines,
            'total_size_kb': total_size / 1024,
            'languages': {
                'python': len(list(self.base_path.rglob("*.py"))),
                'javascript': len(list(self.base_path.rglob("*.js"))),
                'java': len(list(self.base_path.rglob("*.java"))),
                'cpp': len(list(self.base_path.rglob("*.cpp")))
            }
        }
