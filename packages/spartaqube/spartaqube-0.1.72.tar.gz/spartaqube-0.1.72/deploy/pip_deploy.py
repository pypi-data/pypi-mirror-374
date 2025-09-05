import os, subprocess, sys, time
from .pip_secrets import get_pip_secrets
from dotenv import load_dotenv
load_dotenv()


def push_to_pip(version):
    '''
    Push into pip using twine upload
    '''
    # Set the TWINE_USERNAME and TWINE_PASSWORD environment variables
    pip_secrets = get_pip_secrets()
    os.environ['TWINE_USERNAME'] = '__token__'
    os.environ['TWINE_PASSWORD'] = pip_secrets['api_token']  # Replace with your actual API token
    ROOT_DIST_PATH = f"{os.getenv('BMY_PATH_PROJECT')}\\spartaqube_dist\\spartaqube_{version}\\spartaqube\\web"
    cmd = f"python -m twine upload ./dist/spartaqube-{version}*"
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, cwd=ROOT_DIST_PATH)
    stdout, stderr = process.communicate()
    print("Stdout pip twine upload:")
    print(stdout)
    print("Stderr pip twine upload:")
    print(stderr)

if __name__ == '__main__':
    print("Start deployment")