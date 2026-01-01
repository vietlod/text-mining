"""
Quick helper to open Firebase Console in browser.

This script opens the Firebase Console page where you can get your Web API Key.

Usage:
    python open_firebase_console.py
"""

import webbrowser
import sys
from pathlib import Path
import json


def get_project_id():
    """Get project ID from firebase_config.json."""
    config_path = Path(__file__).parent / 'config' / 'firebase_config.json'
    
    if not config_path.exists():
        return None
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config.get('project_id')
    except:
        return None


def main():
    """Open Firebase Console."""
    print("=" * 70)
    print("Opening Firebase Console...")
    print("=" * 70)
    print()
    
    project_id = get_project_id()
    
    if project_id:
        url = f"https://console.firebase.google.com/project/{project_id}/settings/general"
        print(f"Opening project settings for: {project_id}")
    else:
        url = "https://console.firebase.google.com/"
        print("Opening Firebase Console (project not detected)")
    
    print()
    print("Instructions:")
    print("1. Scroll down to 'Your apps' section")
    print("2. If no web app exists, click Web icon (</>) to add one")
    print("3. Copy the firebaseConfig object values")
    print("4. Run: python setup_firebase_web_config.py")
    print()
    
    try:
        webbrowser.open(url)
        print("✅ Browser opened!")
        print()
        print("After getting your API Key, run:")
        print("  python setup_firebase_web_config.py")
    except Exception as e:
        print(f"❌ Error opening browser: {e}")
        print()
        print(f"Please manually open: {url}")


if __name__ == '__main__':
    main()

