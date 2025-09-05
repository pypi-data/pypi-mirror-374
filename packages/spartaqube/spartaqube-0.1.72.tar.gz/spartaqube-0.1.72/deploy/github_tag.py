import os, json
import requests
import base64
from packaging.version import parse

def get_tags() -> dict:
    '''
    
    '''
    api_url = "https://api.github.com/repos/SpartaQube/spartaqube-version/tags"
    response = requests.get(api_url)
    tags = json.loads(response.text)
    return tags

def get_commits_sha() -> str:
    '''
    Get sha
    '''
    tags = get_tags()
    latest_tag = max(tags, key=lambda t: parse(t["name"]))
    return latest_tag['commit']['sha']

def get_github_config() -> dict:
    '''
    Get config (repo name, owner, and app token)
    '''
    current_path = os.path.dirname(__file__)
    # JSON file path in the current folder
    json_file = os.path.join(current_path, "github_secrets.json")
    with open(json_file, "r") as file:
        github_config_dict = json.load(file)    

    return github_config_dict

def push_github_tag(tag_name):
    """
    Push a new tag to a GitHub repository.

    Args:
        tag_name (str): Name of the new tag (e.g., "v1.2.0").
        commit_sha (str): The commit SHA the tag will point to.
        access_token (str): GitHub Personal Access Token.

    Returns:
        dict: Response from the GitHub API.
    """
    github_config_dict = get_github_config()
    repo_owner = github_config_dict['repo_owner']     
    repo_name = github_config_dict['repo_name']     
    commit_sha = get_commits_sha()
    access_token = github_config_dict['access_token']     
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/git/refs"

    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    payload = {
        "ref": f"refs/tags/{tag_name}",
        "sha": commit_sha
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()  # Raise HTTP errors if any
        json_res = response.json()
        print(json_res)
        return json_res
    except requests.RequestException as e:
        print(f"Error creating tag: {e}")
        print(f"Response: {response.text}")
        return None

def delete_tag(tag_name):
    """
    Delete a tag from a GitHub repository.

    Args:
        repo_owner (str): GitHub username or organization.
        repo_name (str): Repository name.
        tag_name (str): The tag name to delete (e.g., "v1.0.0").
        access_token (str): GitHub Personal Access Token.
    """
    # API URL to delete the tag
    github_config_dict = get_github_config()
    repo_owner = github_config_dict['repo_owner']     
    repo_name = github_config_dict['repo_name']     
    access_token = github_config_dict['access_token']         
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/git/refs/tags/{tag_name}"
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        response = requests.delete(api_url, headers=headers)
        if response.status_code == 204:
            print(f"Tag '{tag_name}' successfully deleted from GitHub.")
        elif response.status_code == 404:
            print(f"Tag '{tag_name}' not found in the repository.")
        else:
            print(f"Failed to delete tag '{tag_name}'. Status Code: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.RequestException as e:
        print(f"Error deleting tag: {e}")

# Example usage
if __name__ == "__main__":
    # Examples
    push_github_tag("0.1.28")
    delete_tag("0.1.28")
    