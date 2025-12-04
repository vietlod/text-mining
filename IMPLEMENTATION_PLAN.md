# KẾ HOẠCH TRIỂN KHAI DỰ ÁN TEXT-MINING
## Comprehensive Project Assessment & Implementation Roadmap

**Ngày tạo:** 2025-12-04
**Phiên bản:** 1.0
**Dự án:** Text-Mining Research Tool - Enhancement Phase

---

## 📊 I. ĐÁNH GIÁ TOÀN DIỆN DỰ ÁN

### 1.1. Tổng Quan Hiện Trạng

**Loại dự án:** Ứng dụng phân tích văn bản học thuật (Academic Text-Mining Tool)

**Tech Stack hiện tại:**
- **Frontend:** Streamlit (Python web framework)
- **Backend:** Python 3.8+
- **AI Integration:** Google Gemini API
- **Document Processing:** PyMuPDF, PyPDF2, python-docx, EasyOCR
- **Data Processing:** Pandas, NumPy
- **Visualization:** Plotly, Altair, Matplotlib, WordCloud

**Điểm mạnh:**
✅ Xử lý văn bản tiếng Việt xuất sắc (diacritic normalization, font error correction)
✅ Hỗ trợ đa định dạng (PDF, DOCX, TXT, HTML, Images)
✅ Tích hợp AI (Google Gemini) với 3 chế độ extraction
✅ Giao diện thân thiện, real-time progress tracking
✅ Code structure tốt, modular design
✅ Logging và error handling tốt

**Hạn chế:**
❌ Không có hệ thống authentication/authorization
❌ Chạy hoàn toàn local, không có user management
❌ API key hardcoded trong config file (security risk)
❌ Không hỗ trợ multi-language UI
❌ Không có theme switcher
❌ Không tích hợp cloud storage (Google Drive, OneDrive)
❌ Không có user profile/settings persistence

### 1.2. Phân Tích Các Tính Năng Được Yêu Cầu

#### **Feature 1: Google Sign-in Authentication**
**Độ phức tạp:** 🔴 High
**Tác động:** Yêu cầu refactor toàn bộ architecture từ local app sang web app với backend

**Thách thức kỹ thuật:**
- Streamlit không hỗ trợ traditional OAuth2 flow tốt (no redirect callback)
- Cần session management và user database
- Bảo mật token storage
- Multi-user concurrent access

**Giải pháp đề xuất:**
- **Option A (Recommended):** Sử dụng `streamlit-authenticator` + Firebase Authentication
  - Pros: Nhẹ, tích hợp tốt với Streamlit, Firebase handle OAuth
  - Cons: Phụ thuộc Firebase

- **Option B:** Custom OAuth2 với FastAPI backend + Streamlit frontend
  - Pros: Full control, scalable
  - Cons: Phức tạp, cần deploy backend riêng

**Khuyến nghị:** Option A với Firebase (nhanh, ổn định, cost-effective)

---

#### **Feature 2: GEMINI_API_KEY Input UI**
**Độ phức tạp:** 🟢 Low
**Tác động:** Cải thiện security, user experience

**Yêu cầu:**
- Input field trong UI sidebar
- Validation API key format
- Secure storage (encrypted or session-based)
- Caption với link hướng dẫn: https://aistudio.google.com/app/apikey
- Persist across sessions (user-specific sau khi có auth)

**Thách thức:**
- Lưu trữ an toàn (không dùng plaintext trong config)
- Validate key trước khi sử dụng

**Giải pháp:**
- Use `st.text_input(type="password")` cho input
- Store trong `st.session_state` hoặc Firebase Firestore (sau khi có auth)
- Test API key với lightweight Gemini request

---

#### **Feature 3: Google Drive & OneDrive Integration**
**Độ phức tạp:** 🔴 High
**Tác động:** Tăng tính tiện dụng, hỗ trợ cloud workflow

**Yêu cầu:**
- OAuth2 authorization với Google Drive API
- OAuth2 authorization với OneDrive API (Microsoft Graph)
- File picker UI để chọn folder
- Download files từ cloud về local temp folder
- Upload results (Excel) lên cloud

**Thách thức kỹ thuật:**
- OAuth2 flow trong Streamlit (giống Google Sign-in challenge)
- Token refresh và expiration handling
- File streaming với large files
- Permissions và security scope

**Giải pháp:**
- **Google Drive:** Sử dụng `google-auth`, `google-auth-oauthlib`, `google-api-python-client`
- **OneDrive:** Sử dụng `msal` (Microsoft Authentication Library) + `msgraph-core`
- Implement OAuth2 flow với Streamlit custom components hoặc redirect approach
- Store OAuth tokens trong encrypted user database

**API Requirements:**
- Google: Enable Google Drive API, get OAuth2 credentials
- Microsoft: Register app trong Azure AD, get client ID/secret

---

#### **Feature 4: Theme Switcher (Light/Dark/System)**
**Độ phức tạp:** 🟡 Medium
**Tác động:** Cải thiện UX, accessibility

**Yêu cầu:**
- UI control trong sidebar/header
- 3 options: Light, Dark, System
- Default: System (detect OS theme)
- Persist user preference

**Thách thức:**
- Streamlit có limited theme control (set trong config.toml)
- Không thể dynamic switch theme trong runtime dễ dàng

**Giải pháp:**
- **Option A:** Sử dụng custom CSS injection với `st.markdown(unsafe_allow_html=True)`
  - Define 2 CSS theme classes
  - Toggle class based on user selection

- **Option B:** Sử dụng `streamlit-theme` hoặc custom components
  - More control nhưng cần build JS component

- **System theme detection:**
  ```python
  import darkdetect
  system_theme = darkdetect.theme()  # 'Dark' or 'Light'
  ```

**Khuyến nghị:** Option A với custom CSS (simple, no dependencies)

---

#### **Feature 5: Multi-language Support (English/Vietnamese)**
**Độ phức tạp:** 🟡 Medium
**Tác động:** Tăng accessibility, international usability

**Yêu cầu:**
- Language selector trong UI (en/vi)
- Default: English
- Translate toàn bộ UI text, labels, notifications
- Sentence case formatting cho tiếng Việt
- Persist language preference

**Approach:**
- **i18n Framework:** Tạo translation dictionary files
  ```
  locales/
    ├── en.json
    └── vi.json
  ```

- **Structure:**
  ```json
  {
    "app_title": "Text-mining research tool",
    "sidebar": {
      "upload_files": "Upload files",
      "extraction_mode": "Extraction mode"
    }
  }
  ```

- **Implementation:**
  - Helper function: `t(key)` để get translated text
  - Store selected language trong session_state
  - Reload UI khi language change

**Workload:**
- ~200-300 text strings cần translate
- Professional translation cho accuracy

---

### 1.3. Đánh Giá Tác Động và Ưu Tiên

| Feature | Complexity | Impact | Priority | Estimated Effort |
|---------|-----------|--------|----------|------------------|
| Google Sign-in | High | Critical | 1 | 3-5 days |
| GEMINI_API_KEY Input | Low | High | 2 | 4-6 hours |
| Cloud Integration (Drive/OneDrive) | High | High | 3 | 5-7 days |
| Theme Switcher | Medium | Medium | 4 | 1-2 days |
| Multi-language | Medium | High | 5 | 2-3 days |

**Total Estimated Effort:** 12-19 days (development only, exclude testing)

---

## 📋 II. KẾ HOẠCH TRIỂN KHAI CHI TIẾT

### Architecture Changes Required

**Current Architecture:**
```
Local Desktop App
├── Streamlit UI (Frontend)
├── Python Modules (Backend Logic)
├── Local File System (Data Storage)
└── Google Gemini API (External Service)
```

**Target Architecture:**
```
Multi-User Web Application
├── Streamlit UI (Frontend)
├── Python Modules (Backend Logic)
├── Firebase Authentication (User Management)
├── Firebase Firestore (User Settings & Data)
├── Cloud Storage Integration (Google Drive / OneDrive)
├── Session Management (Secure Token Storage)
└── External APIs (Gemini, Drive, OneDrive)
```

**Key Changes:**
1. Add Firebase SDK
2. Implement user session management
3. Migrate from local file storage to hybrid (local temp + cloud)
4. Add user-specific settings database
5. Implement OAuth2 flows for cloud integrations

---

## 🎯 III. SESSIONS VÀ CHECKPOINTS CỤ THỂ

### **SESSION 1: Project Setup & Infrastructure** ⏱️ 1 day

#### Checkpoint 1.1: Development Environment Setup
- [ ] Create new Git branch: `feature/multi-user-enhancements`
- [ ] Backup current codebase
- [ ] Update `requirements.txt` with new dependencies:
  ```
  firebase-admin==6.3.0
  streamlit-authenticator==0.2.3
  google-auth==2.25.2
  google-auth-oauthlib==1.2.0
  google-api-python-client==2.110.0
  msal==1.26.0
  msgraph-core==1.0.0
  darkdetect==0.8.0
  cryptography==41.0.7
  ```
- [ ] Create new directory structure:
  ```
  app/
    ├── auth/              # Authentication modules
    ├── cloud/             # Cloud storage integrations
    ├── i18n/              # Internationalization
    └── database/          # User data management
  locales/
    ├── en.json
    └── vi.json
  config/
    ├── firebase_config.json
    └── oauth_credentials.json
  ```

#### Checkpoint 1.2: Firebase Project Setup
- [ ] Create Firebase project: https://console.firebase.google.com/
- [ ] Enable Firebase Authentication
  - Enable Google Sign-in provider
- [ ] Enable Cloud Firestore
  - Create collections: `users`, `settings`, `api_keys`
- [ ] Generate Firebase Admin SDK credentials
- [ ] Download `firebase_config.json` to `config/`
- [ ] Set up Firestore security rules:
  ```javascript
  rules_version = '2';
  service cloud.firestore {
    match /databases/{database}/documents {
      match /users/{userId} {
        allow read, write: if request.auth != null && request.auth.uid == userId;
      }
      match /settings/{userId} {
        allow read, write: if request.auth != null && request.auth.uid == userId;
      }
    }
  }
  ```

#### Checkpoint 1.3: Google Cloud & Azure Setup
- [ ] **Google Cloud Console:**
  - Create new project or use existing
  - Enable Google Drive API
  - Create OAuth2 credentials (Web application)
  - Add authorized redirect URIs
  - Download `google_oauth_credentials.json`

- [ ] **Microsoft Azure Portal:**
  - Register new app: https://portal.azure.com/
  - Enable Microsoft Graph API permissions:
    - Files.Read.All
    - Files.ReadWrite.All
    - User.Read
  - Generate client secret
  - Save client ID and secret

**Deliverables:**
- ✅ Development environment ready
- ✅ All cloud services configured
- ✅ Credentials and config files secured

---

### **SESSION 2: Authentication System Implementation** ⏱️ 3-4 days

#### Checkpoint 2.1: Firebase Integration
**File:** `app/auth/firebase_manager.py`

- [ ] Create FirebaseManager class:
  ```python
  class FirebaseManager:
      def __init__(self):
          # Initialize Firebase Admin SDK

      def initialize_app(self):
          # Load credentials and initialize

      def get_auth_instance(self):
          # Return Firebase Auth instance

      def get_firestore_client(self):
          # Return Firestore client
  ```

- [ ] Implement authentication methods:
  ```python
  def verify_id_token(self, id_token):
      # Verify Firebase ID token
      # Return user info

  def create_user_profile(self, user_id, email, display_name):
      # Create Firestore user document

  def get_user_profile(self, user_id):
      # Retrieve user data from Firestore
  ```

- [ ] Test Firebase connection:
  - [ ] Write unit test: `tests/test_firebase_auth.py`
  - [ ] Verify token validation
  - [ ] Test Firestore read/write

**Estimated time:** 1 day

---

#### Checkpoint 2.2: Streamlit Authentication UI
**File:** `app/auth/streamlit_auth.py`

- [ ] Create authentication component:
  ```python
  class StreamlitAuth:
      def __init__(self, firebase_manager):
          self.firebase_manager = firebase_manager

      def render_login_page(self):
          # Display login UI with Google Sign-in button

      def handle_google_signin(self):
          # OAuth2 flow implementation
          # Option: Use streamlit-google-auth component

      def is_authenticated(self):
          # Check session state for valid token

      def logout(self):
          # Clear session state and redirect

      def require_auth(self, func):
          # Decorator for protected pages
  ```

- [ ] Implement Google Sign-in flow:
  - **Approach:** Use `streamlit-google-auth` library or custom component
  - [ ] Create Google OAuth2 flow with redirect
  - [ ] Handle callback and token exchange
  - [ ] Store ID token in `st.session_state['id_token']`
  - [ ] Store user info in `st.session_state['user']`

- [ ] Design login page UI:
  ```python
  def render_login_page():
      st.title("Text-Mining Research Tool")
      st.markdown("### Welcome! Please sign in to continue")

      col1, col2, col3 = st.columns([1,2,1])
      with col2:
          if st.button("🔐 Sign in with Google", use_container_width=True):
              # Trigger OAuth flow

      st.info("ℹ️ This application requires Google Sign-in for access")
  ```

**Estimated time:** 2 days

---

#### Checkpoint 2.3: Session Management & Protection
**File:** `app/auth/session_manager.py`

- [ ] Create SessionManager class:
  ```python
  class SessionManager:
      @staticmethod
      def initialize_session():
          # Initialize session state variables

      @staticmethod
      def set_user(user_data):
          st.session_state['user'] = user_data
          st.session_state['authenticated'] = True

      @staticmethod
      def get_current_user():
          return st.session_state.get('user')

      @staticmethod
      def is_authenticated():
          return st.session_state.get('authenticated', False)

      @staticmethod
      def logout():
          for key in list(st.session_state.keys()):
              del st.session_state[key]
          st.rerun()
  ```

- [ ] Update `ui/main.py` to require authentication:
  ```python
  def main():
      auth = StreamlitAuth(firebase_manager)

      if not auth.is_authenticated():
          auth.render_login_page()
          return

      # Original app logic here
      render_main_app()
  ```

- [ ] Add logout button in sidebar:
  ```python
  with st.sidebar:
      user = SessionManager.get_current_user()
      st.write(f"👤 {user['email']}")
      if st.button("🚪 Logout"):
          SessionManager.logout()
  ```

**Estimated time:** 1 day

---

#### Checkpoint 2.4: Testing & Validation
- [ ] Manual testing:
  - [ ] Test Google Sign-in flow
  - [ ] Verify token persistence across page reloads
  - [ ] Test logout functionality
  - [ ] Test unauthorized access protection

- [ ] Error handling:
  - [ ] Network errors
  - [ ] Invalid tokens
  - [ ] Firebase connection failures

**Deliverables:**
- ✅ Working Google Sign-in authentication
- ✅ Protected application access
- ✅ Session management functional

---

### **SESSION 3: GEMINI_API_KEY Input Feature** ⏱️ 4-6 hours

#### Checkpoint 3.1: User Settings Database Schema
**Firestore Collection:** `settings/{user_id}`

```javascript
{
  "user_id": "string",
  "gemini_api_key": "encrypted_string",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

- [ ] Create `app/database/settings_manager.py`:
  ```python
  class SettingsManager:
      def __init__(self, firestore_client):
          self.db = firestore_client

      def save_api_key(self, user_id, api_key):
          # Encrypt and save to Firestore
          encrypted_key = self._encrypt(api_key)
          self.db.collection('settings').document(user_id).set({
              'gemini_api_key': encrypted_key,
              'updated_at': firestore.SERVER_TIMESTAMP
          }, merge=True)

      def get_api_key(self, user_id):
          # Retrieve and decrypt API key
          doc = self.db.collection('settings').document(user_id).get()
          if doc.exists:
              encrypted_key = doc.to_dict().get('gemini_api_key')
              return self._decrypt(encrypted_key)
          return None

      def _encrypt(self, text):
          # Use cryptography.fernet for encryption

      def _decrypt(self, encrypted_text):
          # Decrypt using stored key
  ```

**Estimated time:** 2 hours

---

#### Checkpoint 3.2: API Key Input UI
**File:** `ui/components/api_key_input.py`

- [ ] Create input component:
  ```python
  def render_api_key_input(settings_manager, user_id):
      st.subheader("🔑 Google Gemini API Configuration")

      # Load existing key
      existing_key = settings_manager.get_api_key(user_id)
      if existing_key:
          st.success("✅ API key configured")
          if st.checkbox("Show API key"):
              st.code(existing_key)

      # Input field
      api_key = st.text_input(
          "Gemini API Key",
          value=existing_key or "",
          type="password",
          help="Enter your Google Gemini API key"
      )

      # Caption with link
      st.caption(
          "💡 Don't have an API key? "
          "[Get your free API key here](https://aistudio.google.com/app/apikey)"
      )

      # Save button
      if st.button("💾 Save API Key"):
          if api_key:
              # Validate key first
              if validate_gemini_key(api_key):
                  settings_manager.save_api_key(user_id, api_key)
                  st.success("API key saved successfully!")
                  st.rerun()
              else:
                  st.error("Invalid API key. Please check and try again.")
          else:
              st.warning("Please enter an API key")
  ```

**Estimated time:** 2 hours

---

#### Checkpoint 3.3: API Key Validation
**File:** `app/core/ai_service.py`

- [ ] Update GeminiService to validate API key:
  ```python
  def validate_api_key(api_key: str) -> bool:
      """Test API key with lightweight request"""
      try:
          genai.configure(api_key=api_key)
          model = genai.GenerativeModel('gemini-1.5-flash')
          response = model.generate_content("Test")
          return True
      except Exception as e:
          logger.error(f"API key validation failed: {e}")
          return False
  ```

- [ ] Update GeminiService to use user-specific API key:
  ```python
  def __init__(self, api_key=None):
      if api_key:
          self.api_key = api_key
      else:
          # Fallback to config (for backward compatibility)
          self.api_key = config.GEMINI_API_KEY

      genai.configure(api_key=self.api_key)
  ```

**Estimated time:** 1 hour

---

#### Checkpoint 3.4: Integration with Main App
- [ ] Update `ui/main.py`:
  ```python
  def render_main_app():
      user = SessionManager.get_current_user()
      user_id = user['user_id']

      # Settings manager
      settings_manager = SettingsManager(firebase_manager.get_firestore_client())

      # Check if API key exists
      api_key = settings_manager.get_api_key(user_id)

      with st.sidebar:
          with st.expander("⚙️ Settings", expanded=not api_key):
              render_api_key_input(settings_manager, user_id)

      # Rest of app logic
      if not api_key:
          st.warning("⚠️ Please configure your Gemini API key in Settings")
          st.stop()

      # Initialize GeminiService with user's API key
      gemini_service = GeminiService(api_key=api_key)
  ```

**Estimated time:** 1 hour

**Deliverables:**
- ✅ User-specific API key storage
- ✅ Secure encryption
- ✅ Validation before save
- ✅ Helpful UI with documentation link

---

### **SESSION 4: Cloud Storage Integration** ⏱️ 5-7 days

#### Checkpoint 4.1: Google Drive Integration
**File:** `app/cloud/google_drive_manager.py`

##### Step 1: OAuth2 Flow Implementation (2 days)

- [ ] Create GoogleDriveManager class:
  ```python
  from google.oauth2.credentials import Credentials
  from google_auth_oauthlib.flow import Flow
  from googleapiclient.discovery import build

  class GoogleDriveManager:
      SCOPES = ['https://www.googleapis.com/auth/drive.readonly',
                'https://www.googleapis.com/auth/drive.file']

      def __init__(self, credentials_path):
          self.credentials_path = credentials_path
          self.flow = None

      def get_authorization_url(self, redirect_uri):
          """Generate OAuth2 authorization URL"""
          self.flow = Flow.from_client_secrets_file(
              self.credentials_path,
              scopes=self.SCOPES,
              redirect_uri=redirect_uri
          )
          auth_url, state = self.flow.authorization_url(
              access_type='offline',
              include_granted_scopes='true',
              prompt='consent'
          )
          return auth_url, state

      def exchange_code_for_token(self, code):
          """Exchange authorization code for access token"""
          self.flow.fetch_token(code=code)
          credentials = self.flow.credentials
          return {
              'token': credentials.token,
              'refresh_token': credentials.refresh_token,
              'token_uri': credentials.token_uri,
              'client_id': credentials.client_id,
              'client_secret': credentials.client_secret,
              'scopes': credentials.scopes
          }

      def get_drive_service(self, credentials_dict):
          """Create Drive service from stored credentials"""
          credentials = Credentials.from_authorized_user_info(credentials_dict)
          service = build('drive', 'v3', credentials=credentials)
          return service
  ```

- [ ] Handle OAuth callback in Streamlit:
  ```python
  # Use query parameters for OAuth callback
  query_params = st.experimental_get_query_params()

  if 'code' in query_params:
      code = query_params['code'][0]
      # Exchange code for token
      token_data = drive_manager.exchange_code_for_token(code)
      # Save to Firestore
      settings_manager.save_drive_credentials(user_id, token_data)
      st.success("Google Drive connected!")
      st.experimental_set_query_params()  # Clear query params
  ```

##### Step 2: File Picker UI (1 day)

- [ ] Create folder selector component:
  ```python
  def render_drive_folder_picker(drive_service):
      st.subheader("📁 Select Google Drive Folder")

      # List folders
      results = drive_service.files().list(
          q="mimeType='application/vnd.google-apps.folder'",
          pageSize=20,
          fields="files(id, name)"
      ).execute()

      folders = results.get('files', [])

      folder_options = {f['name']: f['id'] for f in folders}
      selected_folder = st.selectbox(
          "Choose folder",
          options=list(folder_options.keys())
      )

      if st.button("✅ Confirm Selection"):
          folder_id = folder_options[selected_folder]
          return folder_id

      return None
  ```

##### Step 3: File Operations (1 day)

- [ ] Implement file listing and download:
  ```python
  def list_files_in_folder(self, service, folder_id, file_types=['pdf', 'docx', 'txt']):
      """List all supported files in folder"""
      mime_types = {
          'pdf': 'application/pdf',
          'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
          'txt': 'text/plain'
      }

      query = f"'{folder_id}' in parents and ("
      query += " or ".join([f"mimeType='{mime_types[ft]}'" for ft in file_types])
      query += ")"

      results = service.files().list(
          q=query,
          pageSize=100,
          fields="files(id, name, mimeType, size)"
      ).execute()

      return results.get('files', [])

  def download_file(self, service, file_id, destination_path):
      """Download file from Drive to local path"""
      request = service.files().get_media(fileId=file_id)

      fh = io.FileIO(destination_path, 'wb')
      downloader = MediaIoBaseDownload(fh, request)

      done = False
      while not done:
          status, done = downloader.next_chunk()
          if status:
              progress = int(status.progress() * 100)
              yield progress  # For progress bar

  def upload_file(self, service, file_path, folder_id, file_name=None):
      """Upload result file back to Drive"""
      if not file_name:
          file_name = os.path.basename(file_path)

      file_metadata = {
          'name': file_name,
          'parents': [folder_id]
      }

      media = MediaFileUpload(file_path, resumable=True)
      file = service.files().create(
          body=file_metadata,
          media_body=media,
          fields='id'
      ).execute()

      return file.get('id')
  ```

**Estimated time:** 4 days

---

#### Checkpoint 4.2: OneDrive Integration
**File:** `app/cloud/onedrive_manager.py`

##### Step 1: Microsoft Authentication (2 days)

- [ ] Create OneDriveManager class:
  ```python
  from msal import ConfidentialClientApplication
  import requests

  class OneDriveManager:
      SCOPES = ['Files.Read.All', 'Files.ReadWrite.All', 'User.Read']

      def __init__(self, client_id, client_secret, tenant_id='common'):
          self.client_id = client_id
          self.client_secret = client_secret
          self.authority = f'https://login.microsoftonline.com/{tenant_id}'

          self.app = ConfidentialClientApplication(
              client_id=self.client_id,
              client_credential=self.client_secret,
              authority=self.authority
          )

      def get_authorization_url(self, redirect_uri):
          """Generate Microsoft auth URL"""
          auth_url = self.app.get_authorization_request_url(
              scopes=self.SCOPES,
              redirect_uri=redirect_uri
          )
          return auth_url

      def exchange_code_for_token(self, code, redirect_uri):
          """Get access token from authorization code"""
          result = self.app.acquire_token_by_authorization_code(
              code=code,
              scopes=self.SCOPES,
              redirect_uri=redirect_uri
          )

          if 'access_token' in result:
              return result
          else:
              raise Exception(f"Auth error: {result.get('error_description')}")

      def refresh_access_token(self, refresh_token):
          """Refresh expired access token"""
          result = self.app.acquire_token_by_refresh_token(
              refresh_token=refresh_token,
              scopes=self.SCOPES
          )
          return result
  ```

##### Step 2: OneDrive API Operations (1 day)

- [ ] Implement file operations:
  ```python
  def list_folders(self, access_token):
      """List OneDrive folders"""
      headers = {'Authorization': f'Bearer {access_token}'}
      url = 'https://graph.microsoft.com/v1.0/me/drive/root/children'
      params = {'$filter': "folder ne null"}

      response = requests.get(url, headers=headers, params=params)
      response.raise_for_status()

      return response.json().get('value', [])

  def list_files_in_folder(self, access_token, folder_id):
      """List files in specific folder"""
      headers = {'Authorization': f'Bearer {access_token}'}
      url = f'https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}/children'

      response = requests.get(url, headers=headers)
      response.raise_for_status()

      files = response.json().get('value', [])
      # Filter by supported types
      supported_files = [
          f for f in files
          if f.get('file') and any(
              f['name'].lower().endswith(ext)
              for ext in ['.pdf', '.docx', '.txt']
          )
      ]

      return supported_files

  def download_file(self, access_token, file_id, destination_path):
      """Download file from OneDrive"""
      headers = {'Authorization': f'Bearer {access_token}'}
      url = f'https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content'

      response = requests.get(url, headers=headers, stream=True)
      response.raise_for_status()

      total_size = int(response.headers.get('content-length', 0))

      with open(destination_path, 'wb') as f:
          downloaded = 0
          for chunk in response.iter_content(chunk_size=8192):
              f.write(chunk)
              downloaded += len(chunk)
              if total_size:
                  progress = int((downloaded / total_size) * 100)
                  yield progress

  def upload_file(self, access_token, file_path, folder_id):
      """Upload file to OneDrive"""
      headers = {
          'Authorization': f'Bearer {access_token}',
          'Content-Type': 'application/octet-stream'
      }

      file_name = os.path.basename(file_path)
      url = f'https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}:/{file_name}:/content'

      with open(file_path, 'rb') as f:
          response = requests.put(url, headers=headers, data=f)

      response.raise_for_status()
      return response.json()
  ```

**Estimated time:** 3 days

---

#### Checkpoint 4.3: Cloud Integration UI
**File:** `ui/components/cloud_storage.py`

- [ ] Create cloud storage settings panel:
  ```python
  def render_cloud_storage_settings(settings_manager, user_id):
      st.subheader("☁️ Cloud Storage Integration")

      tab1, tab2 = st.tabs(["Google Drive", "OneDrive"])

      with tab1:
          render_google_drive_settings(settings_manager, user_id)

      with tab2:
          render_onedrive_settings(settings_manager, user_id)

  def render_google_drive_settings(settings_manager, user_id):
      # Check if connected
      credentials = settings_manager.get_drive_credentials(user_id)

      if credentials:
          st.success("✅ Google Drive connected")
          st.info(f"📁 Linked folder: {credentials.get('folder_name', 'Not selected')}")

          col1, col2 = st.columns(2)
          with col1:
              if st.button("📂 Change Folder"):
                  # Show folder picker
                  pass
          with col2:
              if st.button("🔌 Disconnect"):
                  settings_manager.remove_drive_credentials(user_id)
                  st.rerun()
      else:
          st.info("Connect your Google Drive to access files directly")

          # Caption with guide link
          st.caption(
              "💡 [How to enable Google Drive API]"
              "(https://developers.google.com/drive/api/quickstart/python)"
          )

          if st.button("🔗 Connect Google Drive"):
              # Redirect to OAuth flow
              drive_manager = GoogleDriveManager(config.GOOGLE_OAUTH_CREDENTIALS)
              redirect_uri = st.experimental_get_query_params().get('redirect_uri', ['http://localhost:8501'])[0]
              auth_url, state = drive_manager.get_authorization_url(redirect_uri)

              st.session_state['oauth_state'] = state
              st.markdown(f"[Click here to authorize]({auth_url})")
  ```

- [ ] Integrate with file upload flow:
  ```python
  def render_file_input_section():
      st.subheader("📄 Input Files")

      source = st.radio(
          "File source",
          options=["Local Upload", "Google Drive", "OneDrive"],
          horizontal=True
      )

      if source == "Local Upload":
          uploaded_files = st.file_uploader(
              "Upload documents",
              type=['pdf', 'docx', 'txt', 'html'],
              accept_multiple_files=True
          )
          return uploaded_files

      elif source == "Google Drive":
          # Check connection
          credentials = settings_manager.get_drive_credentials(user_id)
          if not credentials:
              st.warning("Please connect Google Drive in Settings first")
              return []

          # Get folder files
          drive_manager = GoogleDriveManager()
          service = drive_manager.get_drive_service(credentials)
          folder_id = credentials.get('folder_id')

          files = drive_manager.list_files_in_folder(service, folder_id)

          selected_files = st.multiselect(
              "Select files to process",
              options=[f['name'] for f in files]
          )

          if st.button("📥 Download Selected Files"):
              # Download to temp directory
              downloaded_paths = []
              progress_bar = st.progress(0)

              for idx, file_name in enumerate(selected_files):
                  file_info = next(f for f in files if f['name'] == file_name)
                  temp_path = f"data/temp/{file_name}"

                  for progress in drive_manager.download_file(service, file_info['id'], temp_path):
                      progress_bar.progress(progress / 100)

                  downloaded_paths.append(temp_path)
                  progress_bar.progress((idx + 1) / len(selected_files))

              st.success(f"Downloaded {len(downloaded_paths)} files")
              return downloaded_paths

      elif source == "OneDrive":
          # Similar logic for OneDrive
          pass
  ```

**Estimated time:** 1 day

---

#### Checkpoint 4.4: Testing & Error Handling
- [ ] Test OAuth flows:
  - [ ] Google Drive authorization
  - [ ] OneDrive authorization
  - [ ] Token refresh on expiration

- [ ] Test file operations:
  - [ ] List folders
  - [ ] List files
  - [ ] Download files (various sizes)
  - [ ] Upload results

- [ ] Error handling:
  - [ ] Network errors
  - [ ] Permission errors
  - [ ] Token expiration
  - [ ] Large file handling (timeout)

**Deliverables:**
- ✅ Google Drive integration working
- ✅ OneDrive integration working
- ✅ File download/upload functional
- ✅ User-friendly UI with guides

---

### **SESSION 5: Theme Switcher Implementation** ⏱️ 1-2 days

#### Checkpoint 5.1: Theme System Design
**File:** `app/ui/theme_manager.py`

- [ ] Define theme configurations:
  ```python
  THEMES = {
      'light': {
          '--background-color': '#FFFFFF',
          '--secondary-background': '#F0F2F6',
          '--text-color': '#262730',
          '--primary-color': '#FF4B4B',
          '--font': 'sans-serif'
      },
      'dark': {
          '--background-color': '#0E1117',
          '--secondary-background': '#262730',
          '--text-color': '#FAFAFA',
          '--primary-color': '#FF4B4B',
          '--font': 'sans-serif'
      }
  }

  class ThemeManager:
      def __init__(self, settings_manager, user_id):
          self.settings_manager = settings_manager
          self.user_id = user_id

      def get_current_theme(self):
          """Get user's theme preference"""
          user_theme = self.settings_manager.get_theme_preference(self.user_id)

          if user_theme == 'system':
              return self._detect_system_theme()
          else:
              return user_theme or 'light'

      def _detect_system_theme(self):
          """Detect OS theme"""
          try:
              import darkdetect
              system_theme = darkdetect.theme()  # Returns 'Dark' or 'Light'
              return system_theme.lower()
          except:
              return 'light'  # Fallback

      def set_theme(self, theme_name):
          """Save theme preference"""
          self.settings_manager.save_theme_preference(self.user_id, theme_name)

      def apply_theme(self, theme_name):
          """Inject CSS for theme"""
          theme_config = THEMES.get(theme_name, THEMES['light'])

          css_vars = '\n'.join([
              f'{key}: {value};'
              for key, value in theme_config.items()
          ])

          css = f"""
          <style>
          :root {{
              {css_vars}
          }}

          .stApp {{
              background-color: var(--background-color);
              color: var(--text-color);
          }}

          .sidebar .sidebar-content {{
              background-color: var(--secondary-background);
          }}

          /* Additional custom styling */
          .stButton>button {{
              background-color: var(--primary-color);
              color: white;
          }}

          .stTextInput>div>div>input {{
              background-color: var(--secondary-background);
              color: var(--text-color);
          }}
          </style>
          """

          st.markdown(css, unsafe_allow_html=True)
  ```

**Estimated time:** 4 hours

---

#### Checkpoint 5.2: Theme Selector UI
**File:** `ui/components/theme_selector.py`

- [ ] Create theme selector component:
  ```python
  def render_theme_selector(theme_manager):
      st.sidebar.divider()
      st.sidebar.subheader("🎨 Theme")

      current_theme_pref = theme_manager.settings_manager.get_theme_preference(
          theme_manager.user_id
      ) or 'system'

      theme_option = st.sidebar.radio(
          "Select theme",
          options=['Light', 'Dark', 'System'],
          index=['light', 'dark', 'system'].index(current_theme_pref.lower()),
          horizontal=True,
          label_visibility='collapsed'
      )

      theme_name = theme_option.lower()

      if theme_name != current_theme_pref:
          theme_manager.set_theme(theme_name)
          st.rerun()

      # Apply theme
      actual_theme = theme_manager.get_current_theme()
      theme_manager.apply_theme(actual_theme)
  ```

**Estimated time:** 2 hours

---

#### Checkpoint 5.3: Persistence & Testing
- [ ] Update SettingsManager to store theme:
  ```python
  def save_theme_preference(self, user_id, theme):
      self.db.collection('settings').document(user_id).set({
          'theme': theme,
          'updated_at': firestore.SERVER_TIMESTAMP
      }, merge=True)

  def get_theme_preference(self, user_id):
      doc = self.db.collection('settings').document(user_id).get()
      if doc.exists:
          return doc.to_dict().get('theme', 'system')
      return 'system'
  ```

- [ ] Testing:
  - [ ] Test all three theme options
  - [ ] Verify system theme detection on different OS
  - [ ] Test theme persistence across sessions
  - [ ] Check all UI components render correctly in both themes

**Estimated time:** 2 hours

**Deliverables:**
- ✅ Theme switcher functional
- ✅ Light/Dark/System modes working
- ✅ Preferences saved per user

---

### **SESSION 6: Multi-language Support** ⏱️ 2-3 days

#### Checkpoint 6.1: Translation Infrastructure
**File:** `app/i18n/translator.py`

- [ ] Create translation system:
  ```python
  import json

  class Translator:
      def __init__(self, language='en'):
          self.language = language
          self.translations = self._load_translations(language)

      def _load_translations(self, language):
          """Load translation file"""
          with open(f'locales/{language}.json', 'r', encoding='utf-8') as f:
              return json.load(f)

      def t(self, key, **kwargs):
          """Translate a key with optional parameters"""
          # Support nested keys: 'sidebar.upload_files'
          keys = key.split('.')
          value = self.translations

          for k in keys:
              value = value.get(k)
              if value is None:
                  return f"[Missing: {key}]"

          # Format with parameters
          if kwargs:
              return value.format(**kwargs)

          return value

      def set_language(self, language):
          """Change language"""
          self.language = language
          self.translations = self._load_translations(language)
  ```

**Estimated time:** 3 hours

---

#### Checkpoint 6.2: Create Translation Files

##### English Translation (`locales/en.json`)

- [ ] Create comprehensive English translation file:
  ```json
  {
    "app_title": "Text-mining research tool",
    "auth": {
      "welcome": "Welcome! Please sign in to continue",
      "sign_in": "Sign in with Google",
      "sign_out": "Sign out",
      "required": "This application requires Google Sign-in for access"
    },
    "sidebar": {
      "settings": "Settings",
      "theme": "Theme",
      "language": "Language",
      "upload_files": "Upload files",
      "extraction_mode": "Extraction mode",
      "keywords": "Keywords",
      "process": "Process documents"
    },
    "settings": {
      "api_key_title": "Google Gemini API configuration",
      "api_key_placeholder": "Enter your Google Gemini API key",
      "api_key_help": "Don't have an API key?",
      "api_key_link_text": "Get your free API key here",
      "api_key_save": "Save API key",
      "api_key_success": "API key saved successfully",
      "api_key_error": "Invalid API key. Please check and try again",
      "api_key_configured": "API key configured"
    },
    "cloud": {
      "title": "Cloud storage integration",
      "google_drive": "Google Drive",
      "onedrive": "OneDrive",
      "connected": "Connected",
      "not_connected": "Not connected",
      "connect": "Connect",
      "disconnect": "Disconnect",
      "select_folder": "Select folder",
      "change_folder": "Change folder",
      "guide_text": "How to enable"
    },
    "processing": {
      "uploading": "Uploading files",
      "extracting": "Extracting text",
      "analyzing": "Analyzing keywords",
      "generating_report": "Generating report",
      "complete": "Processing complete",
      "error": "An error occurred"
    },
    "results": {
      "title": "Analysis results",
      "total_files": "Total files",
      "total_keywords": "Total keywords found",
      "download_report": "Download report",
      "view_details": "View details"
    }
  }
  ```

**Estimated time:** 4 hours

---

##### Vietnamese Translation (`locales/vi.json`)

- [ ] Create Vietnamese translation file (Sentence case):
  ```json
  {
    "app_title": "Công cụ phân tích văn bản nghiên cứu",
    "auth": {
      "welcome": "Chào mừng! Vui lòng đăng nhập để tiếp tục",
      "sign_in": "Đăng nhập với Google",
      "sign_out": "Đăng xuất",
      "required": "Ứng dụng này yêu cầu đăng nhập bằng tài khoản Google"
    },
    "sidebar": {
      "settings": "Cài đặt",
      "theme": "Giao diện",
      "language": "Ngôn ngữ",
      "upload_files": "Tải tệp lên",
      "extraction_mode": "Chế độ trích xuất",
      "keywords": "Từ khóa",
      "process": "Xử lý tài liệu"
    },
    "settings": {
      "api_key_title": "Cấu hình Google Gemini API",
      "api_key_placeholder": "Nhập khóa API Google Gemini của bạn",
      "api_key_help": "Chưa có khóa API?",
      "api_key_link_text": "Tạo khóa API miễn phí tại đây",
      "api_key_save": "Lưu khóa API",
      "api_key_success": "Đã lưu khóa API thành công",
      "api_key_error": "Khóa API không hợp lệ. Vui lòng kiểm tra và thử lại",
      "api_key_configured": "Đã cấu hình khóa API"
    },
    "cloud": {
      "title": "Tích hợp lưu trữ đám mây",
      "google_drive": "Google Drive",
      "onedrive": "OneDrive",
      "connected": "Đã kết nối",
      "not_connected": "Chưa kết nối",
      "connect": "Kết nối",
      "disconnect": "Ngắt kết nối",
      "select_folder": "Chọn thư mục",
      "change_folder": "Thay đổi thư mục",
      "guide_text": "Hướng dẫn bật"
    },
    "processing": {
      "uploading": "Đang tải tệp lên",
      "extracting": "Đang trích xuất văn bản",
      "analyzing": "Đang phân tích từ khóa",
      "generating_report": "Đang tạo báo cáo",
      "complete": "Hoàn tất xử lý",
      "error": "Đã xảy ra lỗi"
    },
    "results": {
      "title": "Kết quả phân tích",
      "total_files": "Tổng số tệp",
      "total_keywords": "Tổng số từ khóa tìm thấy",
      "download_report": "Tải báo cáo",
      "view_details": "Xem chi tiết"
    }
  }
  ```

**Note:** All Vietnamese text follows Sentence case formatting as requested.

**Estimated time:** 5 hours

---

#### Checkpoint 6.3: Language Selector UI
**File:** `ui/components/language_selector.py`

- [ ] Create language selector:
  ```python
  def render_language_selector(settings_manager, user_id):
      st.sidebar.divider()
      st.sidebar.subheader("🌐 Language")

      current_lang = settings_manager.get_language_preference(user_id) or 'en'

      language_option = st.sidebar.radio(
          "Select language",
          options=['English', 'Tiếng Việt'],
          index=0 if current_lang == 'en' else 1,
          horizontal=True,
          label_visibility='collapsed'
      )

      new_lang = 'en' if language_option == 'English' else 'vi'

      if new_lang != current_lang:
          settings_manager.save_language_preference(user_id, new_lang)
          st.rerun()

      return new_lang
  ```

**Estimated time:** 2 hours

---

#### Checkpoint 6.4: Integration with Main App
- [ ] Update `ui/main.py` to use Translator:
  ```python
  def main():
      # ... authentication ...

      user_id = SessionManager.get_current_user()['user_id']

      # Initialize translator
      language = settings_manager.get_language_preference(user_id) or 'en'
      translator = Translator(language)

      # Store in session state for global access
      st.session_state['translator'] = translator
      st.session_state['t'] = translator.t

      # Update all UI text
      st.title(translator.t('app_title'))

      with st.sidebar:
          st.header(translator.t('sidebar.settings'))
          # ... rest of sidebar ...
  ```

- [ ] Update all UI components to use `t()` function:
  ```python
  # Before:
  st.button("Upload files")

  # After:
  t = st.session_state['t']
  st.button(t('sidebar.upload_files'))
  ```

**Estimated time:** 8 hours (updating all UI text)

---

#### Checkpoint 6.5: Testing & Quality Assurance
- [ ] Testing checklist:
  - [ ] All UI elements translated
  - [ ] No missing translation keys
  - [ ] Sentence case for Vietnamese
  - [ ] Language persists across sessions
  - [ ] Dynamic content (errors, notifications) translated
  - [ ] Numbers and dates formatted correctly per locale

- [ ] Create translation coverage test:
  ```python
  def test_translation_coverage():
      """Ensure all keys exist in both languages"""
      with open('locales/en.json', 'r') as f:
          en_keys = json.load(f)
      with open('locales/vi.json', 'r') as f:
          vi_keys = json.load(f)

      # Compare keys
      assert en_keys.keys() == vi_keys.keys()
  ```

**Estimated time:** 4 hours

**Deliverables:**
- ✅ English and Vietnamese translations complete
- ✅ Language switcher functional
- ✅ All UI text translatable
- ✅ User preferences saved

---

### **SESSION 7: Integration Testing & Bug Fixes** ⏱️ 2-3 days

#### Checkpoint 7.1: End-to-End Testing

- [ ] Test complete user flows:
  1. **New user onboarding:**
     - [ ] Sign in with Google
     - [ ] Configure Gemini API key
     - [ ] Connect cloud storage
     - [ ] Set theme and language preferences

  2. **Document processing:**
     - [ ] Upload local files
     - [ ] Select files from Google Drive
     - [ ] Select files from OneDrive
     - [ ] Process documents in all 3 extraction modes
     - [ ] View results
     - [ ] Download report

  3. **Settings management:**
     - [ ] Change theme
     - [ ] Change language
     - [ ] Update API key
     - [ ] Disconnect/reconnect cloud storage

- [ ] Cross-browser testing:
  - [ ] Chrome
  - [ ] Firefox
  - [ ] Edge
  - [ ] Safari (if applicable)

- [ ] Performance testing:
  - [ ] Large file handling
  - [ ] Multiple concurrent users
  - [ ] API rate limiting

**Estimated time:** 1 day

---

#### Checkpoint 7.2: Security Audit

- [ ] Security checklist:
  - [ ] API keys encrypted in database
  - [ ] OAuth tokens securely stored
  - [ ] No sensitive data in logs
  - [ ] Input validation on all forms
  - [ ] HTTPS enforcement
  - [ ] CSRF protection
  - [ ] Rate limiting on API calls

- [ ] Firebase security rules audit:
  - [ ] Verify users can only access own data
  - [ ] Test unauthorized access attempts

**Estimated time:** 4 hours

---

#### Checkpoint 7.3: Bug Fixes & Polish

- [ ] Common issues to check:
  - [ ] Token expiration handling
  - [ ] Error message clarity
  - [ ] Loading states and spinners
  - [ ] Empty state handling
  - [ ] File size limits
  - [ ] Browser console errors

- [ ] UI/UX improvements:
  - [ ] Consistent spacing and alignment
  - [ ] Helpful tooltips
  - [ ] Clear error messages
  - [ ] Progress indicators
  - [ ] Responsive design

**Estimated time:** 1 day

---

#### Checkpoint 7.4: Documentation

- [ ] Update README.md:
  - [ ] New setup instructions
  - [ ] Firebase configuration steps
  - [ ] OAuth setup guides
  - [ ] Environment variables
  - [ ] Deployment instructions

- [ ] Create user guide:
  - [ ] Getting started
  - [ ] Feature overview
  - [ ] Troubleshooting
  - [ ] FAQ

- [ ] Code documentation:
  - [ ] Docstrings for all new functions
  - [ ] Architecture diagram
  - [ ] API reference

**Estimated time:** 4 hours

**Deliverables:**
- ✅ All features tested and working
- ✅ Security verified
- ✅ Documentation complete
- ✅ Ready for deployment

---

## 📊 IV. TỔNG KẾT VÀ TIMELINE

### Effort Summary

| Session | Deliverables | Estimated Time |
|---------|-------------|----------------|
| Session 1 | Project setup & infrastructure | 1 day |
| Session 2 | Google Sign-in authentication | 3-4 days |
| Session 3 | GEMINI_API_KEY input feature | 0.5-1 day |
| Session 4 | Cloud storage integration | 5-7 days |
| Session 5 | Theme switcher | 1-2 days |
| Session 6 | Multi-language support | 2-3 days |
| Session 7 | Testing & documentation | 2-3 days |
| **TOTAL** | **All features complete** | **15-21 days** |

### Critical Dependencies

```
Session 1 (Setup)
    ↓
Session 2 (Authentication) ← BLOCKER for all other sessions
    ↓
    ├─→ Session 3 (API Key) ──┐
    ├─→ Session 4 (Cloud) ────┤
    ├─→ Session 5 (Theme) ────┤→ Session 7 (Testing)
    └─→ Session 6 (i18n) ─────┘
```

**Note:** Session 2 (Authentication) must be completed first as it's a dependency for all other features.

### Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| OAuth complexity in Streamlit | High | Use proven libraries, consider FastAPI backend if needed |
| Token refresh failures | Medium | Implement robust error handling and retry logic |
| Cloud API rate limits | Medium | Add caching, queue requests |
| Translation accuracy | Low | Professional review of Vietnamese translations |
| Browser compatibility | Low | Test early and often |

### Success Criteria

✅ **Functional Requirements:**
- Users can sign in with Google
- API keys stored securely per user
- Files can be accessed from Google Drive and OneDrive
- Theme switcher works across all pages
- Full English and Vietnamese language support

✅ **Non-Functional Requirements:**
- Application remains fast and responsive
- Security best practices followed
- Code is maintainable and documented
- User experience is intuitive

✅ **Acceptance Criteria:**
- All features work in end-to-end flow
- No critical bugs
- Documentation complete
- Ready for production deployment

---

## 🚀 V. NEXT STEPS

### Immediate Actions (Before Starting)

1. **Get stakeholder approval:**
   - Review this plan with project owner
   - Confirm feature requirements
   - Approve estimated timeline
   - Budget approval for cloud services

2. **Set up accounts:**
   - Create Firebase project
   - Set up Google Cloud Console project
   - Register Azure AD application
   - Generate all credentials

3. **Prepare development environment:**
   - Install new dependencies
   - Configure IDE
   - Set up version control branch

### After Completion

1. **Deployment:**
   - Deploy to production server
   - Configure environment variables
   - Set up monitoring and logging
   - Create backup strategy

2. **User onboarding:**
   - Create onboarding tutorial
   - Notify existing users of changes
   - Provide migration guide

3. **Maintenance:**
   - Monitor error logs
   - Track usage analytics
   - Collect user feedback
   - Plan next iteration

---

## 📞 VI. SUPPORT & RESOURCES

### Documentation Links

- **Firebase:** https://firebase.google.com/docs
- **Google Drive API:** https://developers.google.com/drive/api/guides/about-sdk
- **Microsoft Graph:** https://learn.microsoft.com/en-us/graph/overview
- **Streamlit:** https://docs.streamlit.io
- **OAuth2:** https://oauth.net/2/

### Tools & Libraries

- `firebase-admin`: Firebase Python SDK
- `streamlit-authenticator`: Streamlit auth component
- `google-auth-oauthlib`: Google OAuth2
- `msal`: Microsoft Authentication Library
- `darkdetect`: OS theme detection
- `cryptography`: Secure encryption

---

**Document Version:** 1.0
**Last Updated:** 2025-12-04
**Author:** Claude Code Assistant
**Status:** Ready for Review & Approval
