#!/usr/bin/env python3
"""
Create GitHub Release
"""

import sys
import os
import subprocess
import json

def create_release(version, commit, repo, token, username):
    """Create GitHub release"""
    
    release_body = f"""🚀 **Phishing Detector v{version}**

**Docker Images:**
- `{username}/phishing-detector-backend:{version}`
- `{username}/phishing-detector-frontend:{version}`
- `{username}/phishing-detector-nginx:{version}`

**Changes:**
- Commit: {commit}
- Tests passed ✅
- Images published to Docker Hub 🐳
- Auto-deployed to EC2 🚀"""

    release_data = {
        "tag_name": f"v{version}",
        "name": f"Release v{version}",
        "body": release_body,
        "draft": False,
        "prerelease": False
    }
    
    cmd = [
        "curl", "-X", "POST",
        "-H", "Accept: application/vnd.github+json",
        "-H", f"Authorization: Bearer {token}",
        "-H", "X-GitHub-Api-Version: 2022-11-28",
        f"https://api.github.com/repos/{repo}/releases",
        "-d", json.dumps(release_data)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Release v{version} created successfully")
        else:
            print(f"⚠️ Release might already exist or failed: {result.stderr}")
    except Exception as e:
        print(f"⚠️ Error creating release: {e}")

if __name__ == "__main__":
    version = os.getenv('VERSION')
    commit = os.getenv('COMMIT')
    repo = os.getenv('GITHUB_REPOSITORY')
    token = os.getenv('GITHUB_TOKEN')
    username = os.getenv('DOCKERHUB_USERNAME')
    
    if not all([version, commit, repo, token, username]):
        print("❌ Missing required environment variables")
        sys.exit(1)
    
    create_release(version, commit, repo, token, username)
