import os
import yaml
import glob
from pathlib import Path

class DocumentMerger:
    def __init__(self, config_path=None, base_path=None):
        # Only support watch in current directory (no args) to keep usage simple
        self.base_path = Path.cwd() if base_path is None else Path(base_path).resolve()

        self.config_path = (
            Path(config_path).resolve() if config_path else (self.base_path / "config.yaml")
        )

        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Config file not found at {self.config_path}.\n"
                f"Please run 'doc-tracker init <folder>' then: cd <folder> && doc-tracker watch"
            )

        self.load_config()
    
    def create_default_config(self):
        raise RuntimeError("Automatic default config creation is disabled. Use 'doc-tracker init <folder>'.")
        
    def load_config(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        output_file = self.config.get('output_file', 'MASTER_DOCUMENTATION.md')

        if os.path.isabs(output_file):
            raise ValueError("output_file in config.yaml must be a relative path within the project folder")

        self.output_file = self.base_path / output_file
        
        # Normalize to absolute paths for tracking; header display stays relative to base
        self.tracked_docs = []
        for doc in self.config.get('tracked_documents', []):
            if isinstance(doc, str):
                if '*' in doc or '?' in doc:
                    # Expand glob; if doc is absolute, join will respect absolute second arg
                    pattern = doc if os.path.isabs(doc) else os.path.join(str(self.base_path), doc)
                    expanded_files = glob.glob(pattern)
                    for expanded_file in expanded_files:
                        abs_path = str(Path(expanded_file).resolve())
                        self.tracked_docs.append({'path': abs_path})
                else:
                    abs_path = str((self.base_path / doc).resolve()) if not os.path.isabs(doc) else str(Path(doc).resolve())
                    self.tracked_docs.append({'path': abs_path})
            elif isinstance(doc, dict) and 'path' in doc:
                path_val = doc['path']
                abs_path = str((self.base_path / path_val).resolve()) if not os.path.isabs(path_val) else str(Path(path_val).resolve())
                new_doc = dict(doc)
                new_doc['path'] = abs_path
                self.tracked_docs.append(new_doc)
            else:
                self.tracked_docs.append(doc)
        
    
    def aggregate_documents(self):
        documents_data = []
        missing_files = []
        
        for doc_config in self.tracked_docs:
            doc_path_str = doc_config['path']
            doc_path = Path(doc_path_str) if os.path.isabs(doc_path_str) else (self.base_path / doc_path_str)
            
            doc_config['exists'] = doc_path.exists()
            
            if doc_path.exists():
                with open(doc_path, 'r', encoding='utf-8') as f:
                    doc_config['content'] = f.read()
            else:
                missing_files.append(doc_path_str)
            
            documents_data.append(doc_config)
        
        output_lines = []
        
        for doc in documents_data:
            doc_path_str = doc['path']
            if os.path.isabs(doc_path_str):
                try:
                    relative_path = os.path.relpath(doc_path_str, self.base_path)
                except ValueError:
                    relative_path = os.path.basename(doc_path_str)
            else:
                relative_path = doc_path_str

            if not doc['exists']:
                continue

            display_text = f"  @{relative_path}  "

            box_width = len(display_text) + 2
            horizontal_line = "─" * (box_width - 2)

            output_lines.append(f"╭{horizontal_line}╮")
            output_lines.append(f"│{display_text}│")
            output_lines.append(f"╰{horizontal_line}╯")

            output_lines.extend(doc['content'].splitlines())

        
        output_content = '\n'.join(output_lines)
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
