import sys, os, io, subprocess, threading, socket, psutil, json, time, requests, platform, tempfile, webbrowser
import django
import multiprocessing
from loguru import logger
from django.core.management import call_command

# Store process info globally
uvicorn_process = None

thread_failed = False
thread_error_msg = None

def init_logger_strategy():
    '''
    Logger strategy with loguru
    '''
    logger.remove()
    LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{message}</cyan>"
    logger.add("server.log", format=LOG_FORMAT, level="INFO", rotation="10 MB")
    logger.add(sys.stdout, format=LOG_FORMAT, level="INFO")

# **********************************************************************************************************************
def set_environment_variable(name, value):
    try:
        os.environ[name] = value
    except Exception as e:
        print(f"Error setting environment variable '{name}': {e}")

def set_environment_variable_persist(name, value):
    try:
        subprocess.run(['setx', name, value])
        # print(f"Environment variable '{name}' set to '{value}'")
    except Exception as e:
        # print(f"Error setting environment variable '{name}': {e}")
        pass

def find_process_by_port(port):
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        try:
            for conn in proc.connections():
                if conn.laddr.port == port:
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None

def is_port_available(port:int) -> bool:
    return is_port_available_fast(port)

def is_port_available_fast(port:int) -> bool:
    try:
        # Create a socket object
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Try to connect to the specified port
            s.bind(("localhost", port))
            return True
    except socket.error:
        return False

def is_port_available_slow(port: int) -> bool:
    """
    Check if a given port is available by attempting to connect
    and using system tools for a more robust check.

    Args:
        port (int): The port number to check.

    Returns:
        bool: True if the port is available, False otherwise.
    """
    # Python socket-based check
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("localhost", port))
        # If connection succeeds, the port is in use
        return False
    except socket.error:
        # Connection failed; port might be free
        pass

    # Additional system-level check
    try:
        os_type = platform.system().lower()
        if os_type == "windows":
            cmd = ["netstat", "-ano"]
        elif os_type in ["linux", "darwin"]:  # darwin is macOS
            cmd = ["netstat", "-tuln"]
        else:
            raise RuntimeError("Unsupported OS for netstat check")

        # Execute netstat and filter for the port
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
        if result.returncode == 0:
            output = result.stdout
            # Look for the port in the output
            if f":{port}" in output:
                return False  # Port is in use
        else:
            print("Error running netstat:", result.stderr)
    except Exception as e:
        print("Error during system-level port check:", str(e))

    # If no issues detected, port is available
    return True

def is_port_busy(port:int) -> bool:
    return not is_port_available(port)
    
def generate_port() -> int:
    port = 8664
    while not is_port_available(port):
        port += 1

    return port

# **********************************************************************************************************************
def set_spartaqube_shortcut():
    '''
    Set spartaqube exec to env
    '''
    current_path = os.path.dirname(__file__)
    base_path = os.path.dirname(current_path)
    spartaqube_exec = os.path.join(base_path, 'cli/spartaqube')
    set_environment_variable_persist('spartaqube', spartaqube_exec)

def db_make_migrations_migrate():
    '''
    
    '''
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    new_stdout, new_stderr = io.StringIO(), io.StringIO()
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = new_stdout, new_stderr
    try:
        call_command('makemigrations')
        call_command('migrate')
    finally:
        # Reset stdout and stderr to their original values    
        sys.stdout, sys.stderr = old_stdout, old_stderr
        
def create_public_user():
    '''
    Public user
    '''
    current_path = os.path.dirname(__file__)
    base_project = os.path.dirname(current_path)
    sys.path.insert(0, os.path.join(base_project, '/project/management'))
    from project.management.commands.createpublicuser import Command as CommandCreatePublicUser
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    CommandCreatePublicUser().handle()

def create_admin_user():
    '''
    Admin user
    '''
    current_path = os.path.dirname(__file__)
    base_project = os.path.dirname(current_path)
    sys.path.insert(0, os.path.join(base_project, '/project/management'))
    from project.management.commands.createadminuser import Command as CommandCreateAdminUser
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    CommandCreateAdminUser().handle()

def get_last_or_default_wsgi_port() -> int:
    try:
        current_path = os.path.dirname(__file__)
        with open(os.path.join(current_path, 'app_data.json'), "r") as json_file:
            loaded_data_dict = json.load(json_file)
        
        wsgi_port = int(loaded_data_dict['default_port'])
    except:
        wsgi_port = 8664

    return wsgi_port
    
def generate_free_wsgi_port(wsgi_port:int=None) -> int:
    if wsgi_port is None:
        wsgi_port = get_last_or_default_wsgi_port()    
    while is_port_busy(wsgi_port):
        wsgi_port += 1
    return wsgi_port

def get_last_or_default_kernel_port() -> int:
    try:
        current_path = os.path.dirname(__file__)
        with open(os.path.join(current_path, 'app_data_kernel.json'), "r") as json_file:
            loaded_data_dict = json.load(json_file)
        
        kernel_port = int(loaded_data_dict['default_port'])
    except:
        kernel_port = 8764

    return kernel_port

def generate_free_kernel_port(kernel_port:int=None) -> int:
    if kernel_port is None:
        kernel_port = get_last_or_default_kernel_port()    
    while is_port_busy(kernel_port):
        kernel_port += 1
    return kernel_port

def is_server_live(url):
    '''
    Ping the server to check if it's live
    '''
    proxies_dict = {"http": os.environ.get('http_proxy', None), "https": os.environ.get('https_proxy', None)}
    try:
        response = requests.get(url, proxies=proxies_dict)
        if response.status_code == 200:
            return True
    except requests.ConnectionError:
        return False
    return False

def check_connection(host, port=443) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex((host, port))
        if result == 0:
            return True
        else:
            return False
        
    return False

def erase_line():
    sys.stdout.write('\r')
    sys.stdout.write(' ' * 80)
    sys.stdout.write('\r')
    sys.stdout.flush()

def get_platform() -> str:
    system = platform.system()
    if system == 'Windows':
        return 'windows'
    elif system == 'Linux':
        return 'linux'
    elif system == 'Darwin':
        return 'mac'
    else:
        return None

def calculate_workers():
    cpu_cores = multiprocessing.cpu_count() - 2
    cpu_cores = max(cpu_cores, 1)
    # return (2 * cpu_cores) + 1
    return cpu_cores

# def start_watchdog(uvicorn_pid):
#     """Starts a detached watchdog process."""
#     python_executable = sys.executable
#     current_path = os.path.dirname(__file__)
#     if sys.platform == "win32":
#         # Windows: Detach process so it's independent
#         DETACHED_PROCESS = 0x00000008
#         return subprocess.Popen(
#             [python_executable, "watchdog.py", str(uvicorn_pid)],
#             stdout=subprocess.DEVNULL,  # Hide output (optional)
#             stderr=subprocess.DEVNULL,
#             text=True,
#             cwd=current_path,
#         )
#     else:
#         # Linux/macOS: Start as a daemon using setsid
#         return subprocess.Popen(
#             [python_executable, "watchdog.py", str(uvicorn_pid)],
#             stdout=subprocess.DEVNULL,  # Hide output (optional)
#             stderr=subprocess.DEVNULL,
#             preexec_fn=os.setsid,  # Detach from parent process
#             text=True,
#             cwd=current_path,
#         )

def start_server(port, silent=False, is_blocking=True, workers=None, b_open_browser=False):
    '''
    runserver at port
    '''

    # Number of workers
    recommend_workers = calculate_workers()
    if workers is None:
        workers = recommend_workers
    else:
        if workers > recommend_workers:
            workers = recommend_workers
    
    # Set the asgi port first
    app_data_dict = {'default_port': port}
    current_path = os.path.dirname(__file__)
    with open(os.path.join(current_path, "app_data.json"), "w") as json_file:
        json.dump(app_data_dict, json_file)

    # Same port for ASGI with Uvicorn
    with open(os.path.join(current_path, "app_data_asgi.json"), "w") as json_file:
        json.dump(app_data_dict, json_file)

    def thread_job_wsgi(stderr_file_path):
        global thread_failed, thread_error_msg
        current_path = os.path.dirname(__file__)
        base_path = os.path.dirname(current_path)
        # f"python manage.py runserver 0.0.0.0:{port} &"
        # waitress-serve --threads=4 --port=8000 your_project.wsgi:application
        # gunicorn --workers 4 your_project.wsgi:application
        # DEPRECATED
        # dev_server = f"python {os.path.join(base_path, 'manage.py')} runserver 0.0.0.0:{port}"
        # gunicorn_server = f"gunicorn --workers 3 --bind 0.0.0.0:{port} 'spartaqube_app'.wsgi:application &"
        # waitress_server = f"waitress-serve --host=0.0.0.0 --port={port} spartaqube_app.wsgi:application &"

        platform = get_platform()
        # server_req = gunicorn_server
        # if platform == 'windows':
        #     server_req = waitress_server

        if platform == 'windows':
            uvicorn_server = f"uvicorn spartaqube_app.asgi:application --workers {workers} --host 0.0.0.0 --port {port} --log-level warning &"
        else:
            uvicorn_server = f"uvicorn 'spartaqube_app'.asgi:application --workers {workers} --host 0.0.0.0 --port {port} --loop uvloop --http httptools --log-level warning &"

        server_req = uvicorn_server

        # server_req = dev_server
        # server_req = f"/usr/local/bin/python3.11 --version"
        # print("server_req > "+str(server_req))
        with open(stderr_file_path, 'w') as stderr_file:
            uvicorn_process = subprocess.Popen(
                server_req, 
                stdout=subprocess.PIPE, 
                stderr=stderr_file,
                # stderr=subprocess.PIPE, 
                shell=True,
                cwd=base_path,
                bufsize=1,
                universal_newlines=True,
            )

            if not silent:
                # Read and print output in real-time
                for line in uvicorn_process.stdout:
                    sys.stdout.write(line)  # Print without extra newline
                    sys.stdout.flush()

            # Start watchdog process
            # start_watchdog(uvicorn_process.pid)

            if is_blocking:
                uvicorn_process.communicate() # This line is important to block the terminal running spartaqube

    # Create a temporary file to hold the stderr output
    stderr_file = tempfile.NamedTemporaryFile(delete=False)
    stderr_file_path = stderr_file.name
    stderr_file.close()

    t_wsgi = threading.Thread(target=thread_job_wsgi, args=(stderr_file_path,))
    t_wsgi.start()
    # thread_job()
    
    i = 0
    while True:
        # animation
        if i > 3:
            i = 0

        if not os.environ.get('IS_REMOTE_SPARTAQUBE_CONTAINER', 'False').lower() == 'true':
            print_ephemeral_line(f'\rStarting SpartaQube server, please wait{i*"."}')

        i += 1

        # Check if the stderr file has any content
        with open(stderr_file_path, 'r') as f:
            stderr_output = f.read()
            if stderr_output is not None:
                if len(stderr_output) > 0:
                    if stderr_output and any(err_word in stderr_output for err_word in ["ERROR", "Traceback", "Exception"]):
                        global thread_failed, thread_error_msg
                        thread_failed = True
                        thread_error_msg = stderr_output

        # if is_server_live(f"http://127.0.0.1:{port}"):
            # break
        
        if check_connection("localhost", port):
            break
        
        

        if thread_failed:  # Check if thread is alive or if it failed
            print("\nThread crashed or command failed. Exiting loop.")
            raise Exception(thread_error_msg)
            # break

        # time.sleep(1)  # Wait for a second before pinging again

    # Clean up the temporary file
    try:
        os.unlink(stderr_file_path)
    except:
        pass
    
    erase_line()

    # Open browser (for spartaqube.sh command especially)
    if b_open_browser:
        webbrowser.open(f"http://localhost:{port}/home")

    # ******************************************************************************************************************
    # Final text message
    # ******************************************************************************************************************
    def draw_boxed_text(text):
        lines = text.split("\n")
        max_length = max(len(line) for line in lines)
        border = "┌" + "─" * (max_length + 2) + "┐"
        bottom_border = "└" + "─" * (max_length + 2) + "┘"

        print(border)
        for line in lines:
            print(f"│ {line.ljust(max_length)} │")
        print(bottom_border)

    silent_msg = 'disabled' if silent else 'enabled'
    http_proxy_msg = os.environ.get('http_proxy', 'No proxy')
    if len(http_proxy_msg) == 0:
        http_proxy_msg = 'No proxy'
    https_proxy_msg = os.environ.get('https_proxy', 'No proxy')
    if len(https_proxy_msg) == 0:
        https_proxy_msg = 'No proxy'

    cmd = f"spartaqube --port {port} --silent {silent} --workers {workers}"
    if len(os.environ.get('http_proxy', '')) > 0:
        cmd += f" --http_proxy {os.environ.get('http_proxy', '')}"
    if len(os.environ.get('https_proxy', '')) > 0:
        cmd += f" --https_proxy {os.environ.get('https_proxy', '')}"

    text = f"""{cmd}
• Logging messages: {silent_msg}
• Worker instances: {workers} ✓ 
• http_proxy: {http_proxy_msg} 
• https_proxy: {https_proxy_msg}
• ctrl+c to kill the application

Application running at: http://localhost:{port}/home
"""
    draw_boxed_text(text)
    # ******************************************************************************************************************

def stop_server(port=None):
    if port is None:
        port = get_last_or_default_wsgi_port()

    if port is not None:
        process = find_process_by_port(port)
        if process:
            print(f"Found process running on port {port}: {process.pid}")
            process.terminate()
            print(f"SpartaQube server stopped")
        else:
            print(f"No process found running on port {port}.")
    else:
        raise Exception("Port not specify")

def start_kernel_server(port=None):
    '''
    Start kernel server
    '''
    if port is None:
        port = generate_free_kernel_port() # Not provided, generate a new available port
    else:
        if is_port_busy(port):
            port = generate_free_kernel_port() # busy, we generate a new available port

    app_data_dict = {'default_port': port}
    current_path = os.path.dirname(__file__)
    with open(os.path.join(current_path, "app_data_kernel.json"), "w") as json_file:
        json.dump(app_data_dict, json_file)

    from spartaqube_kernel import start_kernel_manager
    # start_kernel_manager(port)
    t_kernel_server = threading.Thread(target=start_kernel_manager, args=(port, ))
    t_kernel_server.start()

def django_setup():
    '''
    Set up Django environment
    '''
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spartaqube_app.settings')
    django.setup()

def print_ephemeral_line(msg):
    erase_line()
    sys.stdout.write(msg)
    sys.stdout.flush()

def entrypoint(port, force_startup=False, silent=False, workers=None, b_open_browser=False):
    '''
    port must be free.
    This is for the local server only. If we want to connect to another instance, just use the api token
    '''
    init_logger_strategy()

    # if is_port_busy(port) and not force_startup:
    #     # We do nothing as we should already be connected to the required port
    #     # Application is supposed to be running already on this port. If an error, it will be found in the get_status called after
    #     print("Api port is busy")
    # else:
    # set_spartaqube_shortcut()

    print_ephemeral_line("Init application, please wait...")
    django_setup()

    # has_changes = db_make_migrations()
    # print("--- %s seconds db_make_migrations ---" % (time.time() - start_time))
    # if has_changes:
    #     db_migrate()

    print_ephemeral_line("Preparing the database and underlying services, please wait...")
    db_make_migrations_migrate()

    print_ephemeral_line("Init main models, please wait...")
    create_public_user()
    create_admin_user()

    print_ephemeral_line("Starting the server now, please wait...")
    start_server(port=port, silent=silent, workers=workers, b_open_browser=b_open_browser)

if __name__ == '__main__':
    entrypoint()
