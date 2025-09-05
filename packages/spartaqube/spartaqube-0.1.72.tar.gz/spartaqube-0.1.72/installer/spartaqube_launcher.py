import os, sys, site, subprocess, argparse, socket, time

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
    parser = argparse.ArgumentParser(description='SpartaQube Launcher Script')
    parser.add_argument('--silent', type=str, help='Run the script in silent mode', default=None)
    parser.add_argument('--port', type=int, help='Port to use for the web server', default=None)
    parser.add_argument('--workers', type=int, help='Number of workers to face the application traffic', default=None)
    parser.add_argument('--http_proxy', type=str, help='http_proxy parameter', default=None)
    parser.add_argument('--https_proxy', type=str, help='https_proxy parameter', default=None)
    # Parse the arguments
    args = parser.parse_args()

    b_open_browser = True
    port = args.port
    silent = args.silent
    workers = args.workers
    http_proxy = args.http_proxy
    https_proxy = args.https_proxy
    # if len(sys.argv) > 1:
    #     args = sys.argv[1:]

    # ******************************************************************************************************************
    # Set proxy environment variable
    # ******************************************************************************************************************
    if http_proxy is None:
        os.environ['http_proxy'] = ''
    else:
        os.environ['http_proxy'] = http_proxy
        if https_proxy is None:
            os.environ['https_proxy'] = http_proxy
    
    if https_proxy is not None:
        os.environ['https_proxy'] = https_proxy

    #*******************************************************************************************************************
    # Silent logs
    #*******************************************************************************************************************
    if silent is None:
        silent = True
        os.environ['SQ_SILENT'] = 'TRUE'
    else:
        if silent.lower() == 'false':
            silent = False
            os.environ['SQ_SILENT'] = 'FALSE'
        else:
            silent = True
            os.environ['SQ_SILENT'] = 'TRUE'

    print_welcome()

    sys.stdout.write("Preparing SpartaQube, please wait...")
    sys.stdout.flush()

    base_path = get_spartaqube_path()
    # api_folder = os.path.join(base_path, 'api')
    sys.path.insert(0, base_path)
    from spartaqube.api.spartaqube_utils import reinstall_channels
    from spartaqube.api import spartaqube_install

    if port is None:
        port = 8664
    
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
