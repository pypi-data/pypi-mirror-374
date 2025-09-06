import argparse
import sys
import os
import subprocess
from pathlib import Path
from .merger import DocumentMerger
from .watcher import watch

def _resolve_base_dir(config_path=None, base_path=None):
    if base_path:
        return Path(base_path).resolve()
    if config_path:
        return Path(config_path).resolve().parent
    return Path.cwd()

def start_background(config_path=None, base_path=None):
    base_dir = _resolve_base_dir(config_path, base_path)
    pid_file = base_dir / "doc-tracker.pid"
    log_file = base_dir / "doc-tracker.log"

    if pid_file.exists():
        print(f"⚠️  doc-tracker may already be running (found {pid_file})")
        return

    cmd = [sys.executable, "-m", "doc_tracker.cli", "watch"]
    if config_path:
        cmd.extend(["-c", str(config_path)])
    if base_path:
        cmd.extend(["-b", str(base_path)])

    base_dir.mkdir(parents=True, exist_ok=True)

    with open(log_file, 'w') as f:
        process = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT)

    with open(pid_file, 'w') as f:
        f.write(str(process.pid))

    print(f"✅ doc-tracker started in background (PID: {process.pid})")
    print(f"📝 Logs: tail -f {log_file}")
    print(f"🛑 Stop: doc-tracker stop -c {config_path or (base_dir / 'config.yaml')} or -b {base_dir}")

def stop_background(config_path=None, base_path=None):
    base_dir = _resolve_base_dir(config_path, base_path)
    pid_file = base_dir / "doc-tracker.pid"

    if not pid_file.exists():
        print(f"⚠️  No doc-tracker process found (looked for {pid_file})")
        return

    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())

        os.kill(pid, 9)
        pid_file.unlink()
        print("✅ doc-tracker stopped")
    except (ValueError, ProcessLookupError, FileNotFoundError):
        pid_file.unlink(missing_ok=True)
        print("⚠️  Process not found, cleaned up pid file")

def init_project(project_name=None):
    if project_name is None:
        project_name = "doc-tracker"
    
    project_path = Path(project_name)
    
    if project_path.exists():
        print(f"❌ Directory '{project_name}' already exists")
        return
    
    project_path.mkdir(parents=True)
    
    config_content = """output_file: master-doc.md
tracked_documents:
- README.md
- docs/*.md
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
    print(f"   # Edit config.yaml to add your documents")
    print(f"   doc-tracker start")

def main():
    parser = argparse.ArgumentParser(prog='doc-tracker', description='Track and merge documentation files into a single file')
    
    parser.add_argument(
        'command',
        nargs='?',
        default='watch',
        choices=['init', 'aggregate', 'watch', 'start', 'stop'],
        help='Command to run: watch (default), init (create project), aggregate (once), start (background), stop'
    )
    
    parser.add_argument(
        'project_name',
        nargs='?',
        help='Project name for init command (default: doc-tracker)'
    )
    
    parser.add_argument(
        '-c', '--config',
        help='Path to config.yaml file (default: ./config.yaml)',
        default=None
    )
    
    parser.add_argument(
        '-b', '--base',
        help='Base directory for relative paths (default: current directory)',
        default=None
    )
    
    args = parser.parse_args()
    
    try:
        if args.command == 'init':
            init_project(args.project_name)
        elif args.command == 'aggregate':
            merger = DocumentMerger(config_path=args.config, base_path=args.base)
            merger.aggregate_documents()
        elif args.command == 'watch':
            watch(config_path=args.config, base_path=args.base)
        elif args.command == 'start':
            start_background(args.config, args.base)
        elif args.command == 'stop':
            stop_background(args.config, args.base)
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
