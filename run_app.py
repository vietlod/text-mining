import os
import sys
import subprocess

def main():
    print("🚀 Starting Text-Mining App...")
    
    # Check requirements
    print("📦 Checking requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except Exception as e:
        print(f"⚠️ Warning: Failed to install requirements automatically. Please run 'pip install -r requirements.txt' manually.")
    
    # Run Streamlit
    app_path = os.path.join("ui", "main.py")
    print(f"🌟 Launching Streamlit: {app_path}")
    
    # Set PYTHONPATH to include the current directory
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd() + os.pathsep + env.get("PYTHONPATH", "")
    
    try:
        subprocess.run(["streamlit", "run", app_path], check=True, env=env)
    except KeyboardInterrupt:
        print("\n👋 App stopped by user.")
    except Exception as e:
        print(f"❌ Error running app: {e}")

if __name__ == "__main__":
    main()
