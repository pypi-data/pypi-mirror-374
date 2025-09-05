from .pip_deploy import push_to_pip
from .github_tag import push_github_tag


def app_release_deploy(version):
    '''
    
    '''
    # 1. Push to pip
    push_to_pip(version)

    # 2. Push to dockerhub (# TODO SPARTAQUBE)

    # 3. Push tag to github repo (spartaqube-versioning)
    push_github_tag(version)



if __name__ == '__main__':
    print("Start Global deployment")
