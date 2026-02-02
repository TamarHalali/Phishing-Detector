#!/usr/bin/env python3
"""
Version Calculator Script
Calculates version based on git commit count
"""

import subprocess
import sys
import os
from datetime import datetime

def get_commit_count():
    """Get total commit count from git"""
    try:
        result = subprocess.run(['git', 'rev-list', '--count', 'HEAD'], 
                              capture_output=True, text=True, check=True)
        count = int(result.stdout.strip())
        print(f"Raw commit count from git: {count}")
        return count
    except subprocess.CalledProcessError as e:
        print(f"Error getting commit count: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error parsing commit count: {e}")
        sys.exit(1)

def get_latest_commit():
    """Get latest commit hash (short)"""
    try:
        result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting commit hash: {e}")
        return "unknown"

def calculate_version():
    """Calculate version in format MAJOR.MINOR.PATCH"""
    commit_count = get_commit_count()
    latest_commit = get_latest_commit()
    timestamp = datetime.now().strftime('%Y%m%d%H%M')
    
    # Version format: 1.0.X where X is commit count
    major = 1
    minor = 0
    patch = commit_count
    
    version = f"{major}.{minor}.{patch}"
    timestamp_version = f"{major}.{minor}.{patch}-{timestamp}"
    
    print(f"=== VERSION CALCULATION ===")
    print(f"Total commits: {commit_count}")
    print(f"Latest commit: {latest_commit}")
    print(f"Generated version: {version}")
    print(f"Timestamp version: {timestamp_version}")
    print(f"==========================")
    
    # Set GitHub Actions outputs
    if os.getenv('GITHUB_OUTPUT'):
        with open(os.getenv('GITHUB_OUTPUT'), 'a') as f:
            f.write(f"version={version}\n")
            f.write(f"timestamp_version={timestamp_version}\n")
            f.write(f"commit_count={commit_count}\n")
            f.write(f"latest_commit={latest_commit}\n")
        print(f"GitHub Actions outputs written to {os.getenv('GITHUB_OUTPUT')}")
    else:
        print("GITHUB_OUTPUT not set - running locally")
    
    return {
        'version': version,
        'timestamp_version': timestamp_version,
        'commit_count': commit_count,
        'latest_commit': latest_commit
    }

if __name__ == "__main__":
    result = calculate_version()
    print(f"\nFinal result: {result}")