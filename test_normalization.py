# -*- coding: utf-8 -*-
"""
Test Vietnamese Normalization
"""

from app.core.text_processor import get_text_processor

processor = get_text_processor()

# Test cases từ user
test_cases = [
    ("Phân tích dữ liệu", "phan tich du lieu"),
    ("dữ liệu lớn", "du lieu lon"),
    ("chấm điểm tín dụng", "cham diem tin dung"),
    ("quản lý rủi ro", "quan ly rui ro"),
    ("dự đoán nhu cầu", "du doan nhu cau"),
    # Additional tests
    ("Ngân hàng Việt Nam", "ngan hang viet nam"),
    ("Đầu tư tài chính", "dau tu tai chinh"),
    ("Công nghệ thông tin", "cong nghe thong tin"),
]

print("=" * 70)
print("VIETNAMESE NORMALIZATION TEST")
print("=" * 70)

all_pass = True
for original, expected in test_cases:
    normalized = processor.normalize_text(original)
    status = "✅ PASS" if normalized == expected else "❌ FAIL"
    
    if normalized != expected:
        all_pass = False
        print(f"\n{status}")
        print(f"  Input:    '{original}'")
        print(f"  Expected: '{expected}'")
        print(f"  Got:      '{normalized}'")
    else:
        print(f"{status} '{original}' → '{normalized}'")

print("\n" + "=" * 70)
if all_pass:
    print("✅ ALL TESTS PASSED!")
else:
    print("❌ SOME TESTS FAILED!")
print("=" * 70)
