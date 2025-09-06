import multiprocessing
import sys
import time
import traceback
import runpy
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

process = None
SCRIPT_PATH = None  


def run_script(path):
    """Run the target script in a separate process."""
    try:
        runpy.run_path(str(path), run_name="__main__")
    except Exception:
        print(f" Error in {path}:")
        traceback.print_exc()


class Handler(FileSystemEventHandler):
    def on_modified(self, event):
        global process
       
        if Path(event.src_path).resolve() == SCRIPT_PATH:
            if process and process.is_alive():
                process.terminate()
                process.join(timeout=2)
                if process.is_alive():
                    print("Forcing kill of old process...")
                    process.kill()
                    process.join()
            start_process(SCRIPT_PATH)


def start_process(path):
    global process
    process = multiprocessing.Process(target=run_script, args=(path,))
    process.start()


def watch(path=None):
    """
    Watch a given Python file for changes and auto-restart it.
    Usage:
        python watchrunner.py myscript.py
    Or:
        import watchrunner; watchrunner.watch("myscript.py")
    """
    global SCRIPT_PATH
    if path is None:
        if len(sys.argv) > 1:
            path = sys.argv[1]
        else:
            print("No script provided. Example:\n   python watchrunner.py myscript.py")
            return

    SCRIPT_PATH = Path(path).resolve()

    if not SCRIPT_PATH.exists():
        print(f" File {SCRIPT_PATH} not found.")
        return

    observer = Observer()
    
    observer.schedule(Handler(), str(SCRIPT_PATH.parent), recursive=False)
    observer.start()
    print(f" Watching {SCRIPT_PATH} for changes...")

    start_process(SCRIPT_PATH)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping watcher...")
        observer.stop()
        if process and process.is_alive():
            process.terminate()
            process.join(timeout=2)
            if process.is_alive():
                process.kill()
                process.join()
    observer.join()


if __name__ == "__main__":
    watch()
