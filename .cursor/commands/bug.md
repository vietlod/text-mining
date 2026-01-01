# bug

## Usage
```
/bug <error description>
```

## Example
```
/bug Firebase authentication failing with "Invalid config" error
```

---

## 5-Phase Bug Fixing Process

### Phase 1: Reproduction & Documentation (15 min)
**Goal:** Confirm bug exists and document exact conditions

**Steps:**
1. Identify affected feature (auth, OCR, cloud storage, etc.)
2. Create reproducible test case
3. Document error message, stack trace, browser console logs
4. Note: OS, browser, Python version, auth status
5. Check if bug in latest code or old deployment

**Deliverable:**
- Exact steps to reproduce
- Error logs (backend console + Streamlit logs)
- Expected vs actual behavior

---

### Phase 2: Root Cause Analysis (20 min)
**Goal:** Understand WHY the bug happens

**Investigation:**
1. Read error message carefully
2. Check git diff recent changes
3. Review related code paths
4. Check Firebase/cloud credentials
5. Test with different inputs

**Examples:**
- **Firebase auth bug:** Invalid credentials? Token expired? Network issue?
- **OCR bug:** Unsupported file format? Memory error? API timeout?
- **Cloud storage bug:** Invalid OAuth token? Permission denied? Rate limit?
- **Gemini API bug:** Invalid API key? Quota exceeded? Network timeout?

**Deliverable:**
- Root cause identified
- Code section causing issue
- Why it worked before (if regression)

---

### Phase 3: Fix Implementation (20 min)
**Goal:** Write minimal fix addressing root cause ONLY

**Rules:**
1. Single, focused fix (don't refactor unless necessary)
2. Follow rules.mdc standards
3. Add error handling if missing
4. Update type hints
5. Add logging for debugging

**Example - Firebase Auth Bug:**
```python
# WRONG: Refactor while fixing
async def authenticate_user(email, password=None):
    # Rewrite entire auth logic...

# RIGHT: Minimal fix
async def authenticate_user(email: str, password: Optional[str] = None):
    try:
        # Existing implementation
        if not firebase_admin.get_app():
            logger.error("Firebase not initialized")
            raise ValueError("Firebase app not configured")
        
        # Rest of function...
    except firebase_admin.exceptions.InvalidArgumentError as e:
        logger.error(f"Firebase auth failed: {str(e)}")
        raise ValueError("Invalid Firebase configuration")
```

**Deliverable:**
- Minimal code changes
- Comments explaining fix
- No unrelated refactoring

---

### Phase 4: Testing (20 min)
**Goal:** Verify fix works and doesn't break anything

**Test Checklist:**
1. **Reproduce Original Bug:** Confirm it's fixed
2. **Edge Cases:** Test with boundary conditions
3. **Regression Tests:** Run existing test suite (>90%)
4. **Related Features:** Test similar functionality

**Testing Examples:**
```python
# Test Firebase auth fix
def test_firebase_auth_with_invalid_config():
    """Firebase auth should handle invalid config gracefully."""
    with pytest.raises(ValueError) as exc:
        asyncio.run(authenticate_user('test@example.com'))
    
    assert "Invalid Firebase configuration" in str(exc.value)

# Test OCR fix
def test_ocr_with_unsupported_format():
    """OCR should handle unsupported formats."""
    with pytest.raises(FileTypeError):
        extract_text_ocr('document.exe')

# Run all tests
pytest --cov=app --cov-fail-under=90
```

**Deliverable:**
- All tests passing (>90%)
- Bug reproduction test added
- No regression in related features

---

### Phase 5: Documentation & Deployment (10 min)
**Goal:** Document fix and deploy to production

**Documentation:**
1. Create/update CHANGELOG.md entry:
   - Error: What users experienced
   - Root cause: Why it happened
   - Solution: How it's fixed
   - Files changed: What was modified
2. Add inline code comments
3. Update README if needed

**Example CHANGELOG Entry:**
```markdown
### Fixed
- **Firebase Auth Failing**: Fixed "Invalid config" error when Firebase app not initialized
  - Issue: Google Sign-in button causing 500 error, blocking all users
  - Root cause: Firebase Admin SDK not initialized before use
  - Solution: Added initialization check in authenticate_user() function
  - Files: [session_manager.py](app/auth/session_manager.py#L45-52)
  - Git commit: `abc123d`
  - Testing: Added test_firebase_auth_with_invalid_config() test case
```

**Deployment:**
```bash
git add -A
git commit -m "fix(auth): handle missing Firebase initialization"
git push origin dev
# PR review → merge → auto-deploy
```

**Deliverable:**
- CHANGELOG.md updated
- Code comments added
- PR description clear
- Ready for production

---

## Quick Bug Fixing Checklist

### Before Fixing
- [ ] Bug can be reproduced with clear steps
- [ ] Root cause identified and documented
- [ ] Impact scope understood (affecting how many users?)

### While Fixing
- [ ] Only change what's necessary (no refactoring)
- [ ] Follow type safety (Rule 2)
- [ ] Add error handling (Rule 4)
- [ ] Add logging for monitoring (Rule 10)

### Before Deployment
- [ ] Bug is fixed (reproducible bug test passes)
- [ ] No regressions (>90% test suite passing)
- [ ] CHANGELOG.md updated with details
- [ ] Code comments explain the fix
- [ ] Conventional commit message: `fix(scope): description`

---

## Common Bug Patterns in TEXT-MINING

| Bug Type | Example | Fix Location |
|----------|---------|--------------|
| **Firebase Errors** | "Invalid config" on sign-in | `app/auth/session_manager.py` - Check initialization |
| **Authentication** | 403 Forbidden on Firestore read | `app/auth/firebase_manager.py` - Check security rules |
| **OCR Issues** | "EasyOCR not found" error | `app/core/ocr_service.py` - Missing library or model |
| **Cloud Storage** | "Permission denied" from Drive | Check OAuth scopes, token refresh logic |
| **API Errors** | Gemini API returning 429 (quota) | `app/core/ai_service.py` - Add rate limiting |
| **Encryption** | "Invalid token" on API key decrypt | `app/utils/encryption.py` - Wrong encryption key |
| **File Upload** | "File too large" error | `app/utils/validators.py` - Check file size limits |
| **Session** | "User logged out unexpectedly" | `app/auth/session_manager.py` - Token expiration |

---

*Last Updated: December 31, 2025*
*Project: TEXT-MINING v1.0*
*Status: Production Ready*
