import os
import yaml
import glob
from datetime import datetime
from pathlib import Path

class DocumentMerger:
    def __init__(self, config_path=None, base_path=None):
        if base_path:
            self.base_path = Path(base_path).resolve()
        else:
            self.base_path = Path.cwd()
        
        if config_path:
            self.config_path = Path(config_path).resolve()
        else:
            self.config_path = self.base_path / "config.yaml"
        
        if not self.config_path.exists():
            self.create_default_config()
        
        self.load_config()
    
    def create_default_config(self):
        """Create a default config.yaml file"""
        default_config = {
            'output_file': 'MASTER_DOCUMENTATION.md',
            'tracked_documents': [
                'README.md',
                'docs/*.md'
            ]
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        print(f"✅ Created default config: {self.config_path}")
        print("📝 Edit config.yaml to specify your documents")
        
    def load_config(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        output_file = self.config.get('output_file', 'MASTER_DOCUMENTATION.md')
        if not os.path.isabs(output_file):
            self.output_file = self.base_path / output_file
        else:
            self.output_file = Path(output_file)
        
        self.tracked_docs = []
        for doc in self.config.get('tracked_documents', []):
            if isinstance(doc, str):
                # Handle glob patterns
                if '*' in doc or '?' in doc:
                    # Use glob to expand patterns
                    expanded_files = glob.glob(os.path.join(self.base_path, doc))
                    for expanded_file in expanded_files:
                        rel_path = os.path.relpath(expanded_file, self.base_path)
                        self.tracked_docs.append({'path': rel_path})
                else:
                    self.tracked_docs.append({'path': doc})
            else:
                self.tracked_docs.append(doc)
        
    
    def aggregate_documents(self):
        documents_data = []
        missing_files = []
        
        for doc_config in self.tracked_docs:
            doc_path_str = doc_config['path']
            if not os.path.isabs(doc_path_str):
                doc_path = self.base_path / doc_path_str
            else:
                doc_path = Path(doc_path_str)
            
            doc_config['exists'] = doc_path.exists()
            
            if doc_path.exists():
                with open(doc_path, 'r', encoding='utf-8') as f:
                    doc_config['content'] = f.read()
            else:
                missing_files.append(doc_path_str)
            
            documents_data.append(doc_config)
        
        output_lines = []
        output_lines.append("# MASTER DOCUMENTATION")
        output_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output_lines.append("="*80)
        
        for doc in documents_data:
            output_lines.append(f"## FILE: {doc['path']}")
            output_lines.append("="*80)
            
            if doc['exists']:
                for line in doc['content'].splitlines():
                    if line.strip():
                        output_lines.append(line)
            else:
                output_lines.append("⚠️ File not found")
            
            output_lines.append("="*80)
        
        output_content = '\n'.join(output_lines)
        
        import re
        while '\n\n' in output_content:
            output_content = output_content.replace('\n\n', '\n')
        
        if not output_content.endswith('\n'):
            output_content += '\n'
        
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(output_content)
        
        print(f"✅ Documentation aggregated to: {self.output_file}")
        
        if missing_files:
            print(f"⚠️  Missing {len(missing_files)} file(s):")
            for file in missing_files:
                print(f"   - {file}")