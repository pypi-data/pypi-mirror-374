import argparse
import sys
from pathlib import Path
from .watcher import watch

def init_project(project_name=None):
    if project_name is None:
        project_name = "doc-tracker"
    
    project_path = Path(project_name)
    
    if project_path.exists():
        print(f"❌ Directory '{project_name}' already exists")
        return
    
    project_path.mkdir(parents=True)
    
    # Minimal config, encourage absolute paths with examples
    config_content = """# Output file must be a relative path inside this folder
output_file: master-doc.md

# Use absolute paths for tracked documents.
# Examples:
# tracked_documents:
#   - /absolute/path/to/README.md
#   - /absolute/path/to/docs/*.md
tracked_documents: []
"""
    
    config_file = project_path / "config.yaml"
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    master_doc = project_path / "master-doc.md"
    with open(master_doc, 'w', encoding='utf-8') as f:
        f.write("")
    
    print(f"✅ Initialized doc-tracker project in '{project_name}/'")
    print(f"📁 Created: {project_name}/config.yaml")
    print(f"📁 Created: {project_name}/master-doc.md")
    print(f"\n🚀 Next steps:")
    print(f"   cd {project_name}")
    print(f"   # Edit config.yaml: add absolute file paths or globs")
    print(f"   doc-tracker watch")

def main():
    parser = argparse.ArgumentParser(
        prog='doc-tracker',
        description='Track and merge documentation files into a single file. Commands: init <folder>, watch',
        formatter_class=argparse.RawTextHelpFormatter,
    )
    
    parser.add_argument(
        'command',
        choices=['init', 'watch'],
        help=('init: create project folder with config.yaml and master-doc.md\n'
              'watch: aggregate and watch; runs in current folder,\n'
              '       or auto-detects the only subfolder containing config.yaml')
    )
    
    parser.add_argument(
        'project_name',
        nargs='?',
        help='Project name for init command (default: doc-tracker)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.command == 'init':
            init_project(args.project_name)
        elif args.command == 'watch':
            watch()
    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
