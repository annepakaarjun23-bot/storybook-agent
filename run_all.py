import subprocess
import sys
import time


def main():
    api = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"])
    time.sleep(2)
    ui = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "ui/streamlit_app.py", "--server.port", "8501"])
    try:
        ui.wait()
    except KeyboardInterrupt:
        pass
    finally:
        for process in (ui, api):
            if process.poll() is None:
                process.terminate()
        for process in (ui, api):
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()


if __name__ == "__main__":
    main()
