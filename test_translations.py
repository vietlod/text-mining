"""Test translation files completeness"""
import json
from pathlib import Path

def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_all_keys(d, prefix=''):
    """Recursively get all keys from nested dict"""
    keys = []
    for k, v in d.items():
        key_path = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            keys.extend(get_all_keys(v, key_path))
        else:
            keys.append(key_path)
    return keys

def test_translations():
    """Test translation completeness"""
    print("=" * 70)
    print("TRANSLATION FILES VALIDATION")
    print("=" * 70)

    # Load files
    en_file = Path('locales/en.json')
    vi_file = Path('locales/vi.json')

    if not en_file.exists():
        print("[FAIL] en.json not found")
        return 1

    if not vi_file.exists():
        print("[FAIL] vi.json not found")
        return 1

    en_data = load_json(en_file)
    vi_data = load_json(vi_file)

    print(f"[PASS] Loaded en.json ({en_file.stat().st_size} bytes)")
    print(f"[PASS] Loaded vi.json ({vi_file.stat().st_size} bytes)")

    # Get all keys
    en_keys = set(get_all_keys(en_data))
    vi_keys = set(get_all_keys(vi_data))

    print(f"\n[INFO] English keys: {len(en_keys)}")
    print(f"[INFO] Vietnamese keys: {len(vi_keys)}")

    # Check for missing keys
    missing_in_vi = en_keys - vi_keys
    missing_in_en = vi_keys - en_keys

    print("\n" + "=" * 70)
    print("KEY COMPLETENESS CHECK")
    print("=" * 70)

    if missing_in_vi:
        print(f"\n[WARNING] {len(missing_in_vi)} keys missing in Vietnamese:")
        for key in sorted(missing_in_vi)[:10]:  # Show first 10
            print(f"  - {key}")
        if len(missing_in_vi) > 10:
            print(f"  ... and {len(missing_in_vi) - 10} more")
    else:
        print("\n[PASS] All English keys present in Vietnamese")

    if missing_in_en:
        print(f"\n[WARNING] {len(missing_in_en)} extra keys in Vietnamese:")
        for key in sorted(missing_in_en)[:10]:
            print(f"  - {key}")
        if len(missing_in_en) > 10:
            print(f"  ... and {len(missing_in_en) - 10} more")
    else:
        print("[PASS] No extra keys in Vietnamese")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if not missing_in_vi and not missing_in_en:
        print("[SUCCESS] Translation files are complete and synchronized!")
        print(f"Total translation keys: {len(en_keys)}")
        return 0
    else:
        print(f"[WARNING] Found {len(missing_in_vi)} missing and {len(missing_in_en)} extra keys")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(test_translations())
