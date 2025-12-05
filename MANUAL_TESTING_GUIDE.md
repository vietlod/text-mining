# Manual Testing Guide - Text-Mining Application

**Version:** 1.0.0
**Date:** December 5, 2025
**Purpose:** Step-by-step manual testing procedures to verify all features

---

## 📋 Table of Contents

1. [Pre-requisites](#pre-requisites)
2. [Session 2: Authentication Testing](#session-2-authentication-testing)
3. [Session 3: API Key Management](#session-3-api-key-management)
4. [Session 4: Cloud Storage Integration](#session-4-cloud-storage-integration)
5. [Session 5: Theme Switcher](#session-5-theme-switcher)
6. [Session 6: Multi-language Support](#session-6-multi-language-support)
7. [Core Features: Document Processing](#core-features-document-processing)
8. [Browser Compatibility](#browser-compatibility)
9. [Mobile Responsiveness](#mobile-responsiveness)
10. [Performance Testing](#performance-testing)
11. [Issue Reporting Template](#issue-reporting-template)

---

## Pre-requisites

### Before You Start:

- [ ] Application is running: `streamlit run ui/main.py`
- [ ] Firebase credentials configured: `config/firebase_config.json`
- [ ] (Optional) Gemini API key ready
- [ ] (Optional) Google Cloud OAuth credentials for Drive
- [ ] (Optional) Azure AD credentials for OneDrive
- [ ] Test documents ready (PDF, DOCX, images)
- [ ] Keyword file ready (CSV/XLSX/TXT)

### Test Environment:

- **URL:** http://localhost:8501
- **Browser:** (Your primary browser)
- **Screen Size:** (Note your screen resolution)
- **OS:** (Windows/Mac/Linux)

---

## Session 2: Authentication Testing

### Test 2.1: First-time Login

**Purpose:** Verify Google Sign-in works correctly

**Steps:**
1. [ ] Open application URL in browser
2. [ ] Verify you see the login page with:
   - [ ] App title and subtitle
   - [ ] Welcome message
   - [ ] "Sign in with Google" button
   - [ ] Proper styling (professional appearance)

3. [ ] Click "Sign in with Google" button
4. [ ] Verify redirect to Google OAuth page
5. [ ] Select your Google account
6. [ ] Grant permissions if prompted
7. [ ] Verify redirect back to application

**Expected Results:**
- [ ] Successfully authenticated
- [ ] User profile visible in sidebar
- [ ] Main application interface loads
- [ ] No error messages

**Actual Results:**
```
(Record what actually happened)

```

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

---

### Test 2.2: Session Persistence

**Purpose:** Verify session remains active across page refreshes

**Steps:**
1. [ ] Ensure you are logged in
2. [ ] Refresh the browser page (F5 or Ctrl+R)
3. [ ] Verify you remain logged in
4. [ ] Check user profile still visible

**Expected Results:**
- [ ] No re-login required
- [ ] Session state preserved
- [ ] User data intact

**Actual Results:**
```
(Record what actually happened)

```

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

---

### Test 2.3: Logout Functionality

**Purpose:** Verify logout clears session properly

**Steps:**
1. [ ] Ensure you are logged in
2. [ ] Locate "Sign out" button (usually in sidebar)
3. [ ] Click "Sign out"
4. [ ] Verify redirect to login page
5. [ ] Try to navigate back in browser
6. [ ] Verify you cannot access protected pages

**Expected Results:**
- [ ] Successfully logged out
- [ ] Redirected to login page
- [ ] Session completely cleared
- [ ] Cannot access app without re-login

**Actual Results:**
```
(Record what actually happened)

```

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

---

### Test 2.4: Multi-tab Behavior

**Purpose:** Verify authentication works across multiple tabs

**Steps:**
1. [ ] Login in Tab 1
2. [ ] Open new tab (Tab 2) with same URL
3. [ ] Verify authentication status in Tab 2
4. [ ] Logout in Tab 1
5. [ ] Refresh Tab 2
6. [ ] Verify Tab 2 also logged out

**Expected Results:**
- [ ] Tab 2 recognizes authentication from Tab 1
- [ ] Logout in Tab 1 affects Tab 2

**Actual Results:**
```
(Record what actually happened)

```

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

---

## Session 3: API Key Management

### Test 3.1: API Key Configuration

**Purpose:** Verify API key can be saved securely

**Steps:**
1. [ ] Login to application
2. [ ] Navigate to Settings (sidebar)
3. [ ] Locate "Google Gemini API" section
4. [ ] Verify you see:
   - [ ] API key input field
   - [ ] Show/hide toggle
   - [ ] "Get API key" link
   - [ ] Save button

5. [ ] Enter a **valid** Gemini API key
6. [ ] Click "Save API key"
7. [ ] Verify success message appears

**Expected Results:**
- [ ] API key saved successfully
- [ ] Success message displayed
- [ ] API key persists after page refresh

**Actual Results:**
```
(Record what actually happened)

```

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

---

### Test 3.2: API Key Validation

**Purpose:** Verify invalid API keys are rejected

**Steps:**
1. [ ] Navigate to Settings
2. [ ] Enter an **invalid** API key (e.g., "invalid-key-123")
3. [ ] Click "Save API key"
4. [ ] Verify error message appears

**Expected Results:**
- [ ] Validation fails
- [ ] Clear error message shown
- [ ] API key NOT saved

**Actual Results:**
```
(Record what actually happened)

```

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

---

### Test 3.3: API Key Show/Hide

**Purpose:** Verify API key visibility toggle works

**Steps:**
1. [ ] Navigate to Settings
2. [ ] Enter an API key
3. [ ] Verify key is masked (••••••••)
4. [ ] Click "Show API key" toggle
5. [ ] Verify key becomes visible
6. [ ] Click toggle again
7. [ ] Verify key is masked again

**Expected Results:**
- [ ] Key masked by default
- [ ] Toggle shows/hides key correctly
- [ ] No console errors

**Actual Results:**
```
(Record what actually happened)

```

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

---

### Test 3.4: API Key Persistence

**Purpose:** Verify API key survives logout/login

**Steps:**
1. [ ] Save a valid API key
2. [ ] Logout
3. [ ] Login again
4. [ ] Navigate to Settings
5. [ ] Verify API key is still configured (shows as configured)

**Expected Results:**
- [ ] API key persists across sessions
- [ ] User doesn't need to re-enter

**Actual Results:**
```
(Record what actually happened)

```

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

---

## Session 4: Cloud Storage Integration

### Test 4.1: Google Drive Connection

**Purpose:** Verify Google Drive can be connected

**Prerequisites:**
- [ ] Google OAuth credentials configured (`config/google_oauth_credentials.json`)

**Steps:**
1. [ ] Navigate to Settings
2. [ ] Locate "Cloud Storage Integration" section
3. [ ] Find "Google Drive" connection status
4. [ ] Verify initial status shows "Not connected"
5. [ ] Click "Connect" button
6. [ ] Verify redirect to Google OAuth consent screen
7. [ ] Grant permissions
8. [ ] Verify redirect back to app
9. [ ] Check connection status now shows "Connected"

**Expected Results:**
- [ ] OAuth flow completes successfully
- [ ] Status changes to "Connected"
- [ ] No error messages

**Actual Results:**
```
(Record what actually happened)

```

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

---

### Test 4.2: Google Drive File Selection

**Purpose:** Verify files can be browsed and selected from Drive

**Prerequisites:**
- [ ] Google Drive connected (Test 4.1 passed)

**Steps:**
1. [ ] Navigate to main page
2. [ ] Locate "File Source" selector
3. [ ] Select "Google Drive"
4. [ ] Verify file browser appears
5. [ ] Browse folders (if any)
6. [ ] Select one or more files
7. [ ] Verify selected files are listed

**Expected Results:**
- [ ] File browser loads
- [ ] Can navigate folders
- [ ] Can select files
- [ ] Selected files displayed correctly

**Actual Results:**
```
(Record what actually happened)

```

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

---

### Test 4.3: Google Drive Disconnect

**Purpose:** Verify Google Drive can be disconnected

**Steps:**
1. [ ] Ensure Google Drive is connected
2. [ ] Navigate to Settings
3. [ ] Click "Disconnect" button for Google Drive
4. [ ] Verify confirmation (if any)
5. [ ] Confirm disconnection
6. [ ] Check status changes to "Not connected"

**Expected Results:**
- [ ] Successfully disconnected
- [ ] Status updated correctly
- [ ] No errors

**Actual Results:**
```
(Record what actually happened)

```

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

---

### Test 4.4: OneDrive Connection

**Purpose:** Verify OneDrive can be connected

**Prerequisites:**
- [ ] Azure AD credentials configured (`config/azure_config.json`)

**Steps:**
1. [ ] Navigate to Settings
2. [ ] Find "OneDrive" connection status
3. [ ] Verify initial status shows "Not connected"
4. [ ] Click "Connect" button
5. [ ] Verify redirect to Microsoft login
6. [ ] Login with Microsoft account
7. [ ] Grant permissions
8. [ ] Verify redirect back to app
9. [ ] Check connection status shows "Connected"

**Expected Results:**
- [ ] OAuth flow completes successfully
- [ ] Status changes to "Connected"
- [ ] No error messages

**Actual Results:**
```
(Record what actually happened)

```

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

---

### Test 4.5: OneDrive File Selection

**Purpose:** Verify files can be browsed from OneDrive

**Prerequisites:**
- [ ] OneDrive connected (Test 4.4 passed)

**Steps:**
1. [ ] Navigate to main page
2. [ ] Select "OneDrive" as file source
3. [ ] Verify file browser appears
4. [ ] Browse folders
5. [ ] Select files
6. [ ] Verify selected files listed

**Expected Results:**
- [ ] File browser loads
- [ ] Can navigate folders
- [ ] Can select files
- [ ] Files displayed correctly

**Actual Results:**
```
(Record what actually happened)

```

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

---

## Session 5: Theme Switcher

### Test 5.1: Light Theme

**Purpose:** Verify Light theme applies correctly

**Steps:**
1. [ ] Navigate to Settings
2. [ ] Locate "Theme" section
3. [ ] Verify current theme shown
4. [ ] Click "Light" theme card
5. [ ] Verify theme changes immediately
6. [ ] Check all UI elements:
   - [ ] Background is light
   - [ ] Text is dark/readable
   - [ ] Buttons have proper contrast
   - [ ] Sidebar styled correctly

**Expected Results:**
- [ ] Theme applies instantly (no page reload)
- [ ] All elements properly styled
- [ ] Text readable
- [ ] No visual glitches

**Actual Results:**
```
(Record what actually happened)

```

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

---

### Test 5.2: Dark Theme

**Purpose:** Verify Dark theme applies correctly

**Steps:**
1. [ ] Navigate to Settings
2. [ ] Click "Dark" theme card
3. [ ] Verify theme changes immediately
4. [ ] Check all UI elements:
   - [ ] Background is dark
   - [ ] Text is light/readable
   - [ ] Buttons have proper contrast
   - [ ] Charts/visualizations visible
   - [ ] Sidebar styled correctly

**Expected Results:**
- [ ] Theme applies instantly
- [ ] All elements properly styled
- [ ] Text readable on dark background
- [ ] No visual glitches

**Actual Results:**
```
(Record what actually happened)

```

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

---

### Test 5.3: System Theme

**Purpose:** Verify System theme auto-detects OS theme

**Steps:**
1. [ ] Navigate to Settings
2. [ ] Click "System" theme card
3. [ ] Verify theme matches your OS theme
4. [ ] (Optional) Change OS theme
5. [ ] (Optional) Refresh page
6. [ ] (Optional) Verify app theme updates

**Expected Results:**
- [ ] Matches OS theme correctly
- [ ] Updates when OS theme changes (after refresh)

**Actual Results:**
```
(Record what actually happened)

```

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

---

### Test 5.4: Theme Persistence

**Purpose:** Verify theme choice persists across sessions

**Steps:**
1. [ ] Select "Dark" theme
2. [ ] Refresh the page
3. [ ] Verify theme is still Dark
4. [ ] Logout
5. [ ] Login again
6. [ ] Verify theme is still Dark

**Expected Results:**
- [ ] Theme persists across refreshes
- [ ] Theme persists across login sessions

**Actual Results:**
```
(Record what actually happened)

```

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

---

## Session 6: Multi-language Support

### Test 6.1: Switch to Vietnamese

**Purpose:** Verify language can be switched to Vietnamese

**Steps:**
1. [ ] Navigate to Settings
2. [ ] Locate "Language" section
3. [ ] Verify current language shown
4. [ ] Click "Vietnamese" (Tiếng Việt) card
5. [ ] Verify UI updates immediately
6. [ ] Check key UI elements are translated:
   - [ ] Sidebar labels
   - [ ] Settings section titles
   - [ ] Buttons
   - [ ] Messages

**Expected Results:**
- [ ] Language changes instantly (no reload)
- [ ] All UI text in Vietnamese
- [ ] Proper Vietnamese formatting (Sentence case)
- [ ] No missing translations

**Actual Results:**
```
(Record what actually happened)

```

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

---

### Test 6.2: Switch to English

**Purpose:** Verify language can be switched to English

**Steps:**
1. [ ] Ensure you're in Vietnamese
2. [ ] Navigate to Settings (Cài đặt)
3. [ ] Click "English" card
4. [ ] Verify UI updates to English
5. [ ] Check all text is in English

**Expected Results:**
- [ ] Language changes instantly
- [ ] All UI text in English
- [ ] No missing translations

**Actual Results:**
```
(Record what actually happened)

```

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

---

### Test 6.3: Language Persistence

**Purpose:** Verify language choice persists

**Steps:**
1. [ ] Select "Vietnamese"
2. [ ] Refresh the page
3. [ ] Verify language is still Vietnamese
4. [ ] Logout
5. [ ] Login again
6. [ ] Verify language is still Vietnamese

**Expected Results:**
- [ ] Language persists across refreshes
- [ ] Language persists across sessions

**Actual Results:**
```
(Record what actually happened)

```

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

---

### Test 6.4: Translation Quality Check

**Purpose:** Verify Vietnamese translations are accurate

**Steps:**
1. [ ] Switch to Vietnamese
2. [ ] Navigate through all pages
3. [ ] Check translations for:
   - [ ] Accuracy (correct meaning)
   - [ ] Grammar (proper Vietnamese)
   - [ ] Consistency (same terms used throughout)
   - [ ] Sentence case formatting

**Expected Results:**
- [ ] All translations accurate
- [ ] Natural Vietnamese phrasing
- [ ] Consistent terminology
- [ ] Proper formatting

**Actual Results:**
```
(Record any translation issues found)

```

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

---

## Core Features: Document Processing

### Test 7.1: Keyword Upload (CSV)

**Purpose:** Verify keyword files can be uploaded

**Prerequisites:**
- [ ] Sample CSV keyword file ready

**Steps:**
1. [ ] Navigate to main page
2. [ ] Locate "Keywords" section in sidebar
3. [ ] Click "Upload" tab
4. [ ] Click "Browse files" or drag-and-drop
5. [ ] Select CSV keyword file
6. [ ] Verify file uploads
7. [ ] Check keywords are displayed
8. [ ] Verify keyword count shown

**Expected Results:**
- [ ] File uploads successfully
- [ ] Keywords parsed and displayed
- [ ] Count shown correctly
- [ ] No errors

**Actual Results:**
```
(Record what actually happened)

```

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

---

### Test 7.2: Local File Upload (PDF)

**Purpose:** Verify local PDF files can be processed

**Prerequisites:**
- [ ] Keywords uploaded (Test 7.1 passed)
- [ ] Sample PDF file ready

**Steps:**
1. [ ] Select "Local Upload" as file source
2. [ ] Upload a PDF file
3. [ ] Select "Local OCR" extraction mode
4. [ ] Click "Process Documents" (or equivalent)
5. [ ] Wait for processing
6. [ ] Verify progress indicator shown
7. [ ] Check results when complete

**Expected Results:**
- [ ] File uploads successfully
- [ ] Processing completes without errors
- [ ] Results displayed correctly
- [ ] Keywords found (if applicable)

**Actual Results:**
```
(Record what actually happened)

```

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

---

### Test 7.3: Image OCR Processing

**Purpose:** Verify OCR works on image files

**Prerequisites:**
- [ ] Keywords uploaded
- [ ] Sample image file ready (PNG/JPG with text)

**Steps:**
1. [ ] Upload image file
2. [ ] Select "Local OCR" mode
3. [ ] Process document
4. [ ] Verify OCR extracts text
5. [ ] Check keyword matches

**Expected Results:**
- [ ] OCR extracts text from image
- [ ] Keywords detected if present
- [ ] Results accurate

**Actual Results:**
```
(Record what actually happened)

```

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

---

### Test 7.4: AI-Powered Processing (OCR AI)

**Purpose:** Verify Gemini AI OCR mode works

**Prerequisites:**
- [ ] Valid Gemini API key configured
- [ ] Keywords uploaded
- [ ] Sample document ready

**Steps:**
1. [ ] Upload document
2. [ ] Select "OCR AI" extraction mode
3. [ ] Process document
4. [ ] Verify AI processing completes
5. [ ] Check results quality

**Expected Results:**
- [ ] AI processing completes
- [ ] Higher accuracy than local OCR
- [ ] Keywords detected correctly

**Actual Results:**
```
(Record what actually happened)

```

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

---

### Test 7.5: Report Download

**Purpose:** Verify analysis reports can be downloaded

**Prerequisites:**
- [ ] Documents processed (previous tests passed)

**Steps:**
1. [ ] Complete document processing
2. [ ] Locate "Download Report" button
3. [ ] Click download
4. [ ] Verify Excel file downloads
5. [ ] Open Excel file
6. [ ] Check report contents:
   - [ ] Keywords listed
   - [ ] Counts accurate
   - [ ] Formatting correct

**Expected Results:**
- [ ] Excel file downloads
- [ ] Report well-formatted
- [ ] Data accurate

**Actual Results:**
```
(Record what actually happened)

```

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

---

## Browser Compatibility

### Test 8.1: Google Chrome

**Browser:** Chrome (latest)
**Version:** ___________

**Test Checklist:**
- [ ] Login works
- [ ] All features functional
- [ ] UI displays correctly
- [ ] No console errors
- [ ] File uploads work
- [ ] Downloads work

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

**Notes:**
```


```

---

### Test 8.2: Mozilla Firefox

**Browser:** Firefox (latest)
**Version:** ___________

**Test Checklist:**
- [ ] Login works
- [ ] All features functional
- [ ] UI displays correctly
- [ ] No console errors
- [ ] File uploads work
- [ ] Downloads work

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

**Notes:**
```


```

---

### Test 8.3: Microsoft Edge

**Browser:** Edge (latest)
**Version:** ___________

**Test Checklist:**
- [ ] Login works
- [ ] All features functional
- [ ] UI displays correctly
- [ ] No console errors
- [ ] File uploads work
- [ ] Downloads work

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

**Notes:**
```


```

---

### Test 8.4: Safari (Mac only)

**Browser:** Safari (latest)
**Version:** ___________

**Test Checklist:**
- [ ] Login works
- [ ] All features functional
- [ ] UI displays correctly
- [ ] No console errors
- [ ] File uploads work
- [ ] Downloads work

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

**Notes:**
```


```

---

## Mobile Responsiveness

### Test 9.1: Mobile Phone (Portrait)

**Device/Screen Size:** < 576px
**Device Used:** ___________

**Test Checklist:**
- [ ] Login page displays correctly
- [ ] Text readable (not too small)
- [ ] Buttons touchable (adequate size)
- [ ] No horizontal scrolling
- [ ] Sidebar accessible
- [ ] Forms usable
- [ ] All features accessible

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

**Screenshots/Notes:**
```


```

---

### Test 9.2: Tablet (Landscape)

**Device/Screen Size:** 768-992px
**Device Used:** ___________

**Test Checklist:**
- [ ] Layout adapts properly
- [ ] All features accessible
- [ ] Touch targets adequate
- [ ] No UI elements cut off
- [ ] Good use of space

**Status:** [ ] PASS [ ] FAIL [ ] BLOCKED

**Screenshots/Notes:**
```


```

---

## Performance Testing

### Test 10.1: Load Time

**Purpose:** Verify app loads quickly

**Steps:**
1. [ ] Clear browser cache
2. [ ] Open app URL
3. [ ] Measure time to interactive
4. [ ] Verify < 5 seconds

**Results:**
- Load time: _______ seconds
- Status: [ ] PASS (< 5s) [ ] FAIL (> 5s)

---

### Test 10.2: Large File Processing

**Purpose:** Verify app handles large files

**Steps:**
1. [ ] Upload large PDF (> 10MB)
2. [ ] Process document
3. [ ] Verify no crashes
4. [ ] Check memory usage

**Results:**
- File size: _______ MB
- Processing time: _______ seconds
- Status: [ ] PASS [ ] FAIL

---

## Issue Reporting Template

When you find a bug, use this template:

```markdown
### Issue #___

**Title:** (Brief description)

**Severity:** [ ] Critical [ ] High [ ] Medium [ ] Low

**Test:** (Which test from this guide)

**Steps to Reproduce:**
1.
2.
3.

**Expected Result:**


**Actual Result:**


**Screenshots/Logs:**


**Environment:**
- Browser:
- OS:
- App Version: 1.0.0

**Status:** [ ] New [ ] In Progress [ ] Fixed [ ] Verified
```

---

## Testing Summary

**Testing Date:** ___________
**Tested By:** ___________
**Version Tested:** 1.0.0

### Overall Results:

| Category | Tests | Passed | Failed | Blocked | Pass Rate |
|----------|-------|--------|--------|---------|-----------|
| Authentication | 4 | ___ | ___ | ___ | ___% |
| API Key Management | 4 | ___ | ___ | ___ | ___% |
| Cloud Storage | 5 | ___ | ___ | ___ | ___% |
| Theme Switcher | 4 | ___ | ___ | ___ | ___% |
| Multi-language | 4 | ___ | ___ | ___ | ___% |
| Document Processing | 5 | ___ | ___ | ___ | ___% |
| Browser Compatibility | 4 | ___ | ___ | ___ | ___% |
| Mobile Responsiveness | 2 | ___ | ___ | ___ | ___% |
| Performance | 2 | ___ | ___ | ___ | ___% |
| **TOTAL** | **34** | **___** | **___** | **___** | **___%** |

### Issues Found: ___

### Critical Issues: ___

### Production Ready: [ ] YES [ ] NO (if >= 95% pass rate with 0 critical issues)

---

**Sign-off:**

Tester: ________________
Date: ________________
Signature: ________________

---

**End of Manual Testing Guide**
