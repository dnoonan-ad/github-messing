import os
from requests import get, post, patch
from dotenv import load_dotenv
import tempfile
from datetime import datetime

# Load environment variables from the specified file
load_dotenv(os.getenv("ENV_FILE_PATH", ".env"))

def get_request(url, access_token):
    
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    response = get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def create_github_commit(username, repo_name, access_token, branch, commit_message, file_path):
    
    base_url = f"https://api.github.com/repos/{username}/{repo_name}"
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Get the current brach sha
    url = f'{base_url}/git/ref/heads/{branch}'
    current_content = get_request(url, access_token)
    obj_url = current_content["object"]["url"]
    commit_sha = current_content["object"]["sha"]
    # get the current tree
    current_content = get_request(obj_url, access_token)
    tree_sha = current_content["tree"]["sha"]

    # Get the current file content
    url = f'{base_url}/contents/{file_path}'
    current_content = get_request(url, access_token)
    resp = get(current_content["download_url"], headers=headers)

    # add a . to the file
    tmpf = tempfile.NamedTemporaryFile()
    with open(tmpf.name, "w") as f:
        f.write(resp.text + ".")

    with open(tmpf.name, "r") as f:
        content = f.read()

    tmpf.close()

    # upload the content as a blob
    body = {
        "content": content,
        "encoding": "utf-8",
    }
    url = f'{base_url}/git/blobs'
    resp = post(url, json=body, headers=headers)
    resp = resp.json()
    blob_sha = resp["sha"]
    # create a new tree
    body = {
        "base_tree": tree_sha,
        "tree": [
            {
                "path": file_path,
                "mode": "100644",
                "type": "blob",
                "sha": blob_sha,
            },
        ],
    }
    url = f'{base_url}/git/trees'
    resp = post(url, json=body, headers=headers)
    resp = resp.json()
    new_tree_sha = resp["sha"]
    # create a new commit
    body = {
        "message": commit_message,
        "tree": new_tree_sha,
        "parents": [commit_sha],
    }
    url = f'{base_url}/git/commits'
    resp = post(url, json=body, headers=headers)
    resp = resp.json()
    new_commit_sha = resp["sha"]

    # update the head to point to the new commit
    url = f'{base_url}/git/refs/heads/main'
    body = {"sha": new_commit_sha, "force": True}
    patch(url, json=body, headers=headers)

    print(f"Commit successful. New commit SHA: {new_commit_sha}")

def read_designs(start_date):
    file_path = "designs/hi.txt"

    with open(file_path, "r") as file:
        data_array = file.read().splitlines()

    set_date = datetime.strptime(start_date, "%d/%m/%Y").date()
    today_date = datetime.now().date()
    days_difference = (today_date - set_date).days
    if str(days_difference) in data_array:
        return 20
    else:
        return 0

    

def main():

    username = os.environ.get('USERNAME')
    repo_name = os.environ.get('REPO_NAME')
    access_token = os.environ.get('ACCESS_TOKEN')
    branch = os.environ.get('BRANCH')
    file_path = os.environ.get('FILE_PATH')
    commit_message = os.environ.get('COMMIT_MESSAGE')
    start_date = os.environ.get('START_DATE')
    
    loop_amount = read_designs(start_date)
    print(f'creating {loop_amount} commits')
    for i in range(int(loop_amount)):
        create_github_commit(username, repo_name, access_token, branch, commit_message, file_path)
    print("Program ran successfully")

if __name__ == "__main__":
    main()