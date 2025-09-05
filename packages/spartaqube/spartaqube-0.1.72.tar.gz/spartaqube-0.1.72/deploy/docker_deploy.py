import os, sys, subprocess, shutil, requests, time, re

# Docker deploy
# We are going to use the dist version (obfuscated for production)

# 1. We must integrate again the removed files and folders (docker folder)
# 2. Build Docker container

def check_version_available_in_pip(version, retry=0) -> str:
    '''
    Wait until the version {version} is available in pypi
    '''
    url = f'https://pypi.org/project/spartaqube/{version}/'

    if retry >= 10:
        raise Exception(f"Pip versioning max retry. Version {version} is still not available at {url}")

    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
    except:
        pass

    print(f"Retry #: {retry+1}")
    time.sleep(30)
    return check_version_available_in_pip(version, retry+1)

def build_docker_container(version):
    '''
    Build docker container
    '''
    # 1. Destroy first
    current_path = os.path.dirname(__file__)
    web_path = os.path.dirname(current_path)
    spartaqube_path = os.path.join(web_path, 'spartaqube')
    process = subprocess.Popen(
        f"docker-compose down --volumes --remove-orphans", 
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
        shell=True, 
        cwd=spartaqube_path,
        bufsize=1,  # Line-buffered output
        universal_newlines=True  # Ensures text output, not bytes
    )
    try:
        for line in iter(process.stdout.readline, ""):
            print(line, end="")  # Avoids extra newlines
    except:
        pass

    # Remove image (rmi)
    process = subprocess.Popen(
        f"docker rmi spartaqube/spartaqube", 
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
        shell=True, 
        cwd=spartaqube_path,
        bufsize=1,  # Line-buffered output
        universal_newlines=True  # Ensures text output, not bytes
    )
    try:
        for line in iter(process.stdout.readline, ""):
            print(line, end="")  # Avoids extra newlines
    except:
        pass
    
    # 1.1 Prune after container is down
    subprocess.run(["docker", "container", "prune", "-f"], check=True)

    # 2. Build docker-compose
    process = subprocess.Popen(
        f"docker-compose build --no-cache", 
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
        shell=True, 
        cwd=spartaqube_path,
        bufsize=1,  # Line-buffered output
        universal_newlines=True  # Ensures text output, not bytes
    )
    try:
        for line in iter(process.stdout.readline, ""):
            print(line, end="")  # Avoids extra newlines
    except:
        pass

    process = subprocess.Popen(
        f"docker-compose up --build", 
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
        shell=True, 
        cwd=spartaqube_path,
        bufsize=1,  # Line-buffered output
        universal_newlines=True  # Ensures text output, not bytes
    )
    try:
        for line in iter(process.stdout.readline, ""):
            print(line, end="")  # Avoids extra newlines
    except:
        pass

def docker_login():
    '''
    Docker login
    '''
    from .docker_secrets import get_docker_secrets
    username = "spartaqube"
    password = get_docker_secrets()['password']
    process = subprocess.run(
        ["docker", "login", "-u", username, "--password-stdin"],
        input=password + "\n",  # Ensure newline at the end
        text=True,
        capture_output=True
    )
    print(process.stdout)
    print(process.stderr)

def docker_tag_and_push(version):
    '''
    Docker tag and push
    '''
    # 1. Docker tag
    process = subprocess.Popen(
        f"docker tag spartaqube-spartaqube spartaqube/spartaqube:{version}", 
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
        shell=True, 
        bufsize=1,  # Line-buffered output
        universal_newlines=True  # Ensures text output, not bytes
    )
    try:
        for line in iter(process.stdout.readline, ""):
            print(line, end="")  # Avoids extra newlines
    except:
        pass
    
    # 2. Docker tag
    process = subprocess.Popen(
        f"docker push spartaqube/spartaqube:{version}", 
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
        shell=True, 
        bufsize=1,  # Line-buffered output
        universal_newlines=True  # Ensures text output, not bytes
    )
    try:
        for line in iter(process.stdout.readline, ""):
            print(line, end="")  # Avoids extra newlines
    except:
        pass

    # Push the latest tag
    process = subprocess.Popen(
        f"docker tag spartaqube-spartaqube spartaqube/spartaqube:latest", 
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
        shell=True, 
        bufsize=1,  # Line-buffered output
        universal_newlines=True  # Ensures text output, not bytes
    )
    try:
        for line in iter(process.stdout.readline, ""):
            print(line, end="")  # Avoids extra newlines
    except:
        pass

    process_latest = subprocess.Popen(
        "docker push spartaqube/spartaqube:latest", 
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
        shell=True, bufsize=1, universal_newlines=True
    )

    try:
        for line in iter(process_latest.stdout.readline, ""):
            print(line, end="")  # Avoids extra newlines
    except:
        pass

def is_docker_running():
    """Check if Docker is running and available."""
    try:
        # Run `docker info` to check if Docker is available
        result = subprocess.run(["docker", "info"], capture_output=True, text=True)
        if result.returncode == 0:
            print("Docker is running and available.")
            return True
        else:
            print("Docker is not available.")
            return False
    except FileNotFoundError:
        print("Docker command not found. Ensure Docker is installed.")
        return False
    
def entrypoint_docker_deploy(version):
    '''
    Docker deployment entrypoint
    '''
    # 1. Copy docker resources
    check_version_available_in_pip(version)

    # 2. Build with docker-compose
    build_docker_container(version)

    # 3. Tests docker version?

    # 4. Push to dockerhub
    docker_login()
    docker_tag_and_push(version)


if __name__ == '__main__':
    # check_version_available_in_pip("0.1.60")
    entrypoint_docker_deploy("0.1.67")