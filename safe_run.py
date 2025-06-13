import os
import subprocess
import signal

def free_port(port):
    try:
        
        result = subprocess.run(["lsof", "-ti", f"tcp:{port}"], capture_output=True, text=True)
        pids = result.stdout.strip().split("\n")
        for pid in pids:
            if pid:
                os.kill(int(pid), signal.SIGKILL)
                print(f"Killed process on port {port} with PID {pid}")
    except Exception as e:
        print(f"No process found using port {port} or error occurred: {e}")


free_port(5000)


os.system("python app.py")
