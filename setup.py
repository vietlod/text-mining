# Setup script for first-time installation
import subprocess
import sys

print("🔧 Setting up Text-Mining App...")
print("=" * 60)

# Install requirements
print("\n📦 Installing Python dependencies...")
try:
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "-r", 
        "requirements.txt", "--upgrade"
    ])
    print("✅ Dependencies installed successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nPlease run manually: pip install -r text_mining_app/requirements.txt")

print("\n" + "=" * 60)
print("🎉 Setup complete!")
print("\n📝 Next steps:")
print("1. (Optional) Set environment variables for API keys:")
print("   - GEMINI_API_KEY: For advanced text analysis")
print("   - GOOGLE_SEARCH_API_KEY: For web search")
print("   - GOOGLE_SEARCH_ENGINE_ID: For web search")
print("\n2. Run the app: python run_app.py")
print("=" * 60)
