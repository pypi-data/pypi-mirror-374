import os, sys, shutil, site, subprocess, argparse, socket, time

def is_port_available_fast(port:int) -> bool:
    try:
        # Create a socket object
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Try to connect to the specified port
            s.bind(("localhost", port))
            return True
    except socket.error:
        return False

def is_port_busy(port:int) -> bool:
    return not is_port_available_fast(port)

def get_spartaqube_path():
    '''
    Get spartaqube path within site-packages
    '''
    site_packages_dir = site.getsitepackages()
    site_packages_folders = [elem for elem in site_packages_dir if 'site-packages' in elem]
    if len(site_packages_folders) == 0:
        site_packages_folders = [elem for elem in site_packages_dir if 'dist-packages' in elem]
    site_packages_path = site_packages_folders[0]
    return os.path.join(site_packages_path, 'spartaqube')

                
def print_welcome():
    print("""
███████╗  ██████╗  
██╔════╝ ██╔═══██╗ 
███████╗ ██║   ██║ 
╚════██║ ██║   ██║ 
███████║ ╚██████╔╝ 
╚══════╝  ╚═╝  ██║ 
               ╚═╝  

Welcome to SpartaQube""")

if __name__ == '__main__':
    b_open_browser = True

    # 1. PORT (inside container, by default 8664)
    port = os.environ.get('port', 8664)
    if port is None:
        port = 8664
    else:
        if len(str(port)) == 0:
            port = 8664
    port = int(port)

    # 2. Silent mode
    silent_str = str(os.environ.get('SQ_SILENT', 'FALSE'))
    silent = silent_str.lower() == 'true'
    if silent:
        os.environ['SQ_SILENT'] = 'TRUE'
    else:
        os.environ['SQ_SILENT'] = 'FALSE'

    # 3. Number of workers uvicorn
    workers = os.environ.get('workers', None)
    if workers is not None:
        if len(str(workers)) == 0:
            workers = None
        else:
            workers = int(workers)

    # 4. Start SpartaQube application
    print_welcome()

    sys.stdout.write("Preparing SpartaQube, please wait...")
    sys.stdout.flush()

    base_path = get_spartaqube_path()
    # api_folder = os.path.join(base_path, 'api')
    sys.path.insert(0, base_path)
    from spartaqube.api import spartaqube_install
    from spartaqube.api.spartaqube_utils import reinstall_channels
    
    while is_port_busy(port):
        port += 1

    try:
        spartaqube_install.entrypoint(port=port, silent=silent, workers=workers, b_open_browser=True)
    except Exception as e:
        print("An error occurred")
        print(e)

        if "cannot import name '__version__' from 'channels'" in str(e):
            reinstall_channels()

            time.sleep(1)

            # Restart script
            os.execv(sys.executable, [sys.executable] + sys.argv)

