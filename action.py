import os
import requests
from requests.auth import HTTPBasicAuth

def edit_text_file(file_path):
    try:
        # Open the file in read mode to read its content
        with open(file_path, 'r') as file:
            content = file.read()

        # Allow the user to edit the content
        edited_content = content + "."

        # Open the file in write mode to save the edited content
        with open(file_path, 'w') as file:
            file.write(edited_content)

        print(f"Changes saved successfully to {file_path}")

    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Example usage:



def create_github_commit(username, repo_name, access_token, branch, commit_message, file_path, new_content):
    base_url = f'https://api.github.com/repos/{username}/{repo_name}/contents/{file_path}'
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Get the current file content
    response = requests.get(base_url, headers=headers)
    response.raise_for_status()
    current_content = response.json()['content']
    
    # Encode the content for comparison
    current_content_decoded = current_content.encode('utf-8')
    
    # Create the new content
    new_content_encoded = new_content.encode('utf-8')
    
    # Check if the content has changed
    if current_content_decoded == new_content_encoded:
        print("No changes to commit.")
        return
    
    # Create a new commit
    commit_data = {
        'message': commit_message,
        'content': new_content_encoded.decode('utf-8'),
        'sha': current_content
    }

    commit_url = f'https://api.github.com/repos/{username}/{repo_name}/git/commits'
    response = requests.post(commit_url, headers=headers, json=commit_data)
    response.raise_for_status()
    new_commit_sha = response.json()['sha']

    # Update the reference (branch) to point to the new commit
    update_ref_url = f'https://api.github.com/repos/{username}/{repo_name}/git/refs/heads/{branch}'
    update_ref_data = {'sha': new_commit_sha}
    response = requests.patch(update_ref_url, headers=headers, json=update_ref_data)
    response.raise_for_status()

    print(f"Commit successful. New commit SHA: {new_commit_sha}")






# Example usage:
file_path = 'text.txt'  # Replace with the path to your text file

repository_path = 'https://github.com/dnoonan-ad/github-messing'
commit_message = 'test'

# edit_text_file(file_path)
commit_to_repo(repository_path, commit_message)


# Example usage:
username = 'dnoonan-ad'
repo_name = 'github-messing'
access_token = 'your_access_token'
branch = 'main'
file_path = 'path/to/your/file.txt'
commit_message = 'Your commit message here'
new_content = 'Your new file content here'

create_github_commit(username, repo_name, access_token, branch, commit_message, file_path, new_content)
