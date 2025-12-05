"""Test script to verify all critical imports work correctly"""
import sys

def test_imports():
    """Test all critical module imports"""
    results = []

    # Test core Python libraries
    tests = [
        ("streamlit", "Streamlit web framework"),
        ("firebase_admin", "Firebase Admin SDK"),
        ("google.generativeai", "Google Gemini AI"),
        ("cryptography.fernet", "Fernet encryption"),
        ("pandas", "Pandas data analysis"),
        ("easyocr", "EasyOCR"),
        ("dotenv", "Python dotenv"),
        ("darkdetect", "Dark mode detection"),
    ]

    # Test app modules
    app_modules = [
        ("app.config", "App configuration"),
        ("app.auth.firebase_manager", "Firebase manager"),
        ("app.auth.session_manager", "Session manager"),
        ("app.auth.streamlit_auth", "Streamlit auth"),
        ("app.database.settings_manager", "Settings manager"),
        ("app.i18n.translator", "Translator"),
        ("app.ui.theme_manager", "Theme manager"),
    ]

    print("=" * 70)
    print("IMPORT TESTS - Core Dependencies")
    print("=" * 70)

    for module, description in tests:
        try:
            __import__(module)
            print(f"[PASS] {description:40s} - OK")
            results.append((module, True, None))
        except ImportError as e:
            print(f"[FAIL] {description:40s} - FAILED: {e}")
            results.append((module, False, str(e)))
        except Exception as e:
            print(f"[ERROR] {description:40s} - ERROR: {e}")
            results.append((module, False, str(e)))

    print("\n" + "=" * 70)
    print("IMPORT TESTS - Application Modules")
    print("=" * 70)

    for module, description in app_modules:
        try:
            __import__(module)
            print(f"[PASS] {description:40s} - OK")
            results.append((module, True, None))
        except ImportError as e:
            print(f"[FAIL] {description:40s} - FAILED: {e}")
            results.append((module, False, str(e)))
        except Exception as e:
            print(f"[ERROR] {description:40s} - ERROR: {e}")
            results.append((module, False, str(e)))

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, success, _ in results if success)
    failed = len(results) - passed

    print(f"Total tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {passed/len(results)*100:.1f}%")

    if failed == 0:
        print("\n[SUCCESS] All imports successful!")
        return 0
    else:
        print("\n[WARNING] Some imports failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(test_imports())
