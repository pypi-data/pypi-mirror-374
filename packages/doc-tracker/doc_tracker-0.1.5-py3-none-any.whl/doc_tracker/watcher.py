import time
import sys
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .merger import DocumentMerger

class DocumentWatcher(FileSystemEventHandler):
    def __init__(self, config_path=None, base_path=None):
        # Keep signature for backward-compat, but use current directory
        self.merger = DocumentMerger()
        self.base_path = self.merger.base_path
        self.last_run = 0
        self.debounce_seconds = 2
        
        self.tracked_paths = set()
        for doc in self.merger.tracked_docs:
            doc_path_str = doc['path']
            if not Path(doc_path_str).is_absolute():
                doc_path = self.base_path / doc_path_str
            else:
                doc_path = Path(doc_path_str)
            self.tracked_paths.add(str(doc_path))
            self.tracked_paths.add(str(doc_path.parent))
        
    def should_process_file(self, file_path):
        file_str = str(file_path)
        for tracked in self.tracked_paths:
            if file_str == tracked or file_str.endswith(tracked):
                return True
        return False
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        if file_path.name == 'config.yaml' and str(file_path) == str(self.merger.config_path):
            print(f"\n🔄 Config file changed, reloading...")
            self.merger.load_config()
            self.merger.aggregate_documents()
            return
        
        if self.should_process_file(file_path):
            current_time = time.time()
            if current_time - self.last_run > self.debounce_seconds:
                print(f"\n📄 Change detected: {file_path.name}")
                time.sleep(0.5)
                self.merger.aggregate_documents()
                self.last_run = current_time

def watch(config_path=None, base_path=None):
    print("🔍 Starting documentation watcher...")
    print("=" * 50)
    
    event_handler = DocumentWatcher()
    
    print(f"📁 Base directory: {event_handler.base_path}")
    print(f"📄 Config file: {event_handler.merger.config_path}")
    print(f"📝 Output file: {event_handler.merger.output_file}")
    print(f"\n📚 Tracking {len(event_handler.merger.tracked_docs)} documents:")
    
    for doc in event_handler.merger.tracked_docs:
        doc_path_str = doc['path']
        if not Path(doc_path_str).is_absolute():
            doc_path = event_handler.base_path / doc_path_str
        else:
            doc_path = Path(doc_path_str)
        status = "✅" if doc_path.exists() else "❌"
        print(f"   {status} {doc['path']}")
    
    print("\n" + "=" * 50)
    print("✨ Initial aggregation...")
    event_handler.merger.aggregate_documents()
    
    print("\n👀 Watching for changes... (Press Ctrl+C to stop)\n")
    
    observer = Observer()
    observer.schedule(event_handler, str(event_handler.base_path), recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n\n👋 Stopped watching")
    
    observer.join()
