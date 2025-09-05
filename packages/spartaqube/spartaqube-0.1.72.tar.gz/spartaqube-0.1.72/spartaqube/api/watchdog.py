import os
import sys
import time
import psutil
import socket
import signal

CHECK_INTERVAL = 5

file_path = "C:\\Users\\benme\\Desktop\\LOG_DEBUG.txt"

def write_or_append_to_file(file_path, text):
    '''
    For debugging purpose only
    '''
    try:
        mode = "a" if os.path.exists(file_path) and os.path.getsize(file_path) > 0 else "w"
        with open(file_path, mode, encoding="utf-8") as file:
            if mode == "a":
                file.write("\n")  # Add a newline before appending
            file.write(text)
        print(f"Successfully wrote/appended to {file_path}")
    except Exception as e:
        print(f"Error writing to file: {e}")


def kill_all():
    """Kills all related processes when Uvicorn dies."""
    # from myapp.kernel_manager import kill_kernels  # Import kernel cleanup function

    # Kill spawned kernel processes
    print("Watchdog: Cleaning up spawned processes...")
    write_or_append_to_file(file_path, f"message > watchdog kill_all")  

    # kill_kernels()
    0/0

def is_port_in_use(port):
    """Check if the given port is in use (indicating Uvicorn is running)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0

def watchdog(port):
    """Daemon that continuously checks if Uvicorn is running."""

    while True:
        write_or_append_to_file(file_path, f"CONNECTED...")  
        if not is_port_in_use(port):
            write_or_append_to_file(file_path, f"CONNECTION LOST, CAN KILL ALL DAEMONS PY PROCESS")  
            kill_all()

        time.sleep(CHECK_INTERVAL)

def main():

    write_or_append_to_file(file_path, f"message > Start watchdog func")  
    write_or_append_to_file(file_path, f"message > {len(sys.argv)}")  

    if len(sys.argv) != 2:
        print("Usage: python watchdog.py <uvicorn_pid>")
        sys.exit(1)

    port = int(sys.argv[1])
    write_or_append_to_file(file_path, f"port > {port}")  

    watchdog(port)

if __name__ == "__main__":

    write_or_append_to_file(file_path, f"message > WELCOME watchdog")  

    main()
