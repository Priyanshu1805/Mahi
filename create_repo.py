import requests
import json

token = "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN"
repo_name = "Mahi"
url = "https://api.github.com/user/repos"
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json"
}
data = {
    "name": repo_name,
    "description": "Mahi AI Voice Assistant - Iron Man Style HUD",
    "private": False
}

response = requests.post(url, headers=headers, data=json.dumps(data))
if response.status_code == 201:
    print(f"SUCCESS: Created repo {repo_name}")
elif response.status_code == 422:
    print(f"INFO: Repo {repo_name} already exists.")
else:
    print(f"FAILED: {response.status_code}")
    print(response.text)
