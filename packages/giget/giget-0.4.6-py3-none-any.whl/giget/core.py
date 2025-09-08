# core.py
import requests, os

def download_single_file(owner, repo, file_path, branch, save_dir=".", force=False, rename=False):
    """Download a single file from GitHub."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={branch}"
    
    print(f"🔍 Fetching file info: {url}")
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch file: {response.status_code} - {response.text}")
    
    file_info = response.json()
    
    if file_info.get("type") != "file":
        raise Exception(f"The specified path is not a file: {file_path}")
    
    # Determine save path
    filename = os.path.basename(file_path)
    save_path = os.path.join(save_dir, filename)
    
    # Handle existing file
    if os.path.exists(save_path):
        if force:
            print(f"⚠️ Overwriting {save_path}")
        elif rename:
            base, ext = os.path.splitext(save_path)
            counter = 1
            new_path = f"{base}_{counter}{ext}"
            while os.path.exists(new_path):
                counter += 1
                new_path = f"{base}_{counter}{ext}"
            save_path = new_path
            print(f"📄 Renamed and saving as {save_path}")
        else:
            raise FileExistsError(
                f"❌ File already exists: {save_path}\n"
                f"Use --force to overwrite or --rename to save with a new name."
            )
    
    # Download the file
    print(f"⬇️  Downloading {file_info['download_url']}")
    file_data = requests.get(file_info["download_url"]).content
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)
    
    with open(save_path, "wb") as f:
        f.write(file_data)
    
    print(f"✅ File saved: {save_path}")

def download_github_dir(owner, repo, path, branch="main", save_dir=".", flat=False, force=False, rename=False):
    """Download a GitHub folder recursively with overwrite/rename options."""
    
    # Handle empty path (root directory)
    if not path:
        url = f"https://api.github.com/repos/{owner}/{repo}/contents?ref={branch}"
    else:
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
    
    print(f"🔍 Fetching directory: {url}")
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch directory: {response.status_code} - {response.text}")
    
    response_data = response.json()
    
    if isinstance(response_data, dict) and response_data.get("message"):
        raise Exception(f"GitHub API error: {response_data['message']}")
    
    if not isinstance(response_data, list):
        raise Exception(f"Expected directory contents, got: {type(response_data)}")

    for item in response_data:
        if item["type"] == "file":
            if flat:
                item_path = os.path.join(save_dir, os.path.basename(item["path"]))
            else:
                # For non-flat mode, preserve the relative structure from the requested path
                if path:
                    # Remove the requested path prefix to get relative path
                    relative_path = item["path"]
                    if relative_path.startswith(path + "/"):
                        relative_path = relative_path[len(path) + 1:]
                    elif relative_path == path:
                        relative_path = os.path.basename(path)
                    item_path = os.path.join(save_dir, relative_path)
                else:
                    item_path = os.path.join(save_dir, item["path"])
                
                # Create parent directories
                parent_dir = os.path.dirname(item_path)
                if parent_dir:
                    os.makedirs(parent_dir, exist_ok=True)

            # Handle existing file
            if os.path.exists(item_path):
                if force:
                    print(f"⚠️ Overwriting {item_path}")
                elif rename:
                    base, ext = os.path.splitext(item_path)
                    counter = 1
                    new_path = f"{base}_{counter}{ext}"
                    while os.path.exists(new_path):
                        counter += 1
                        new_path = f"{base}_{counter}{ext}"
                    item_path = new_path
                    print(f"📄 Renamed and saving as {item_path}")
                else:
                    raise FileExistsError(
                        f"❌ File already exists: {item_path}\n"
                        f"Use --force to overwrite or --rename to save with a new name."
                    )

            print(f"⬇️  Downloading {item['download_url']}")
            file_data = requests.get(item["download_url"]).content
            with open(item_path, "wb") as f:
                f.write(file_data)

        elif item["type"] == "dir":
            if flat:
                # Skip making directories in flat mode, just recurse inside
                download_github_dir(owner, repo, item["path"], branch, save_dir, flat, force, rename)
            else:
                # Calculate the relative directory path
                if path:
                    relative_path = item["path"]
                    if relative_path.startswith(path + "/"):
                        relative_path = relative_path[len(path) + 1:]
                    dir_path = os.path.join(save_dir, relative_path)
                else:
                    dir_path = os.path.join(save_dir, item["path"])

                # Handle existing directory
                if os.path.exists(dir_path):
                    if force:
                        print(f"⚠️ Directory exists: {dir_path}")
                    elif rename:
                        counter = 1
                        new_path = f"{dir_path}_{counter}"
                        while os.path.exists(new_path):
                            counter += 1
                            new_path = f"{dir_path}_{counter}"
                        dir_path = new_path
                        print(f"📂 Renamed directory to {dir_path}")
                    else:
                        print(f"📂 Directory exists: {dir_path}")

                os.makedirs(dir_path, exist_ok=True)

                # Recurse into subdirectory
                download_github_dir(owner, repo, item["path"], branch, save_dir, flat, force, rename)