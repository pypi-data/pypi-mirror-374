# cli.py --> entry point
import sys, re
from .core import download_github_dir, download_single_file
from .help import show_help
from .list import list_github_folder

def parse_github_url(url: str) -> dict:
    """
    Parse GitHub URL and extract owner, repo, branch, path, and type.
    
    Returns dict with keys: owner, repo, branch, path, url_type
    url_type can be: 'repo', 'tree' (directory), 'blob' (file)
    """
    # Remove trailing slash and split
    url = url.rstrip("/")
    
    # Extract the path after github.com/
    try:
        path_part = url.split("github.com/")[1]
        parts = path_part.split("/")
    except (IndexError, ValueError):
        raise ValueError("Invalid GitHub URL format")
    
    if len(parts) < 2:
        raise ValueError("URL must contain owner and repository")
    
    owner = parts[0]
    repo = parts[1]
    
    # Default values
    branch = "main"  # GitHub's default branch is now "main"
    path = ""
    url_type = "repo"
    
    if len(parts) == 2:
        # Just owner/repo - download entire repository
        url_type = "repo"
        path = ""
    elif len(parts) >= 4 and parts[2] in ["tree", "blob"]:
        # Format: owner/repo/tree|blob/branch/path/to/resource
        url_type = parts[2]
        branch = parts[3]
        if len(parts) > 4:
            path = "/".join(parts[4:])
    elif len(parts) > 2:
        # Fallback: treat remaining as path with default branch
        path = "/".join(parts[2:])
        url_type = "tree"  # Assume it's a directory
    
    return {
        "owner": owner,
        "repo": repo,
        "branch": branch,
        "path": path,
        "url_type": url_type
    }

def validate_github_url(url: str) -> bool:
    """
    Validate GitHub repository, subdirectory, or file URL.
    Examples of valid:
      - https://github.com/user/repo
      - https://github.com/user/repo/tree/branch/path/to/dir
      - https://github.com/user/repo/blob/branch/path/to/file.txt
    """
    pattern = re.compile(
        r"^https:\/\/github\.com\/[^\/]+\/[^\/]+(?:\/(?:tree|blob)\/[^\/]+(?:\/.*)?)?$"
    )
    return bool(pattern.match(url))

def main():
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)

    args = sys.argv[1:]

    # -------------------------------
    # Handle commands with no URL
    # -------------------------------
    if args[0] in ("--help", "-h"):
        show_help()
        sys.exit(0)

    if args[0] in ("--version", "-v", "-V"):
        print(f"giget 0.4.7 built by Ronit Naik")
        sys.exit(0)

    # -------------------------------
    # Handle special command: list
    # -------------------------------
    if args[0] == "list":
        if len(args) < 2:
            print("❌ Missing GitHub URL for list command.")
            sys.exit(1)

        url = args[1].rstrip("/")
        if not validate_github_url(url):
            print("❌ Invalid GitHub URL format:", url)
            sys.exit(1)

        try:
            list_github_folder(url)
            sys.exit(0)
        except Exception as e:
            print("❌ Error:", e)
            sys.exit(1)

    # -------------------------------
    # Default: Download mode
    # -------------------------------
    flat = False
    save_dir = "."
    force = False
    rename = False
    url = None

    i = 0
    while i < len(args):
        arg = args[i]

        if arg == "-nf":
            flat = True
        elif arg == "--force":
            force = True
        elif arg == "--rename":
            rename = True
        elif arg == "-o":
            if i + 1 >= len(args):
                print("❌ Missing output directory after -o")
                sys.exit(1)
            save_dir = args[i + 1]
            i += 1
        elif arg.startswith("-"):
            print("❌ Unknown flag:", arg)
            sys.exit(1)
        else:
            if url is not None:
                print("❌ Multiple URLs detected. Only one is allowed.")
                sys.exit(1)
            url = arg.rstrip("/")
        i += 1

    if url is None:
        print("❌ Missing GitHub URL.\n\nUsage: giget [flags] <github_url>")
        sys.exit(1)

    if not validate_github_url(url):
        print("❌ Invalid GitHub URL format:", url)
        sys.exit(1)

    try:
        # Parse the GitHub URL using the new parser
        parsed = parse_github_url(url)
        owner = parsed["owner"]
        repo = parsed["repo"]
        branch = parsed["branch"]
        path = parsed["path"]
        url_type = parsed["url_type"]
        
        print(f"📋 Parsed URL:")
        print(f"   Owner: {owner}")
        print(f"   Repo: {repo}")
        print(f"   Branch: {branch}")
        print(f"   Path: {path}")
        print(f"   Type: {url_type}")
        
    except Exception as e:
        print(f"❌ Invalid GitHub URL structure: {e}")
        sys.exit(1)

    try:
        # Handle different URL types
        if url_type == "blob":
            # Single file download
            download_single_file(owner, repo, path, branch, save_dir, force, rename)
        else:
            # Directory download (includes full repo)
            download_github_dir(owner, repo, path, branch, save_dir, flat, force, rename)
            
        print("✅ Download complete!")
    except Exception as e:
        print("❌ Error:", e)
        sys.exit(1)