# dev

## Usage
```
/dev <feature description>
```

## Example
```
/dev Add OneDrive cloud storage integration alongside Google Drive
```

---

## 5-Phase Feature Development Process

### Phase 1: Requirements & Planning (20 min)
**Goal:** Define what needs to be built and how

**Questions to Answer:**
1. What is the user problem being solved?
2. Which components are affected? (auth, UI, cloud, database, etc.)
3. What data needs to be accessed or modified?
4. Are there any database schema changes?
5. What are the acceptance criteria?

**Design Plan:**
- Backend: New services, database changes, API integrations
- Frontend: New components, state changes, Streamlit UI
- Testing: Unit tests, integration tests
- Documentation: README, guides, code comments

**Example - OneDrive Integration:**
```
User Problem: Users want to upload/process files from OneDrive, not just Google Drive
Components Affected:
  - Backend: OneDrive API manager, OAuth handler
  - Frontend: Cloud storage UI, file selector
  - Database: Store OneDrive tokens in Firestore
  - Auth: OAuth2 flow for Microsoft Azure

Technical Design:
  - Backend: Create OneDriveManager similar to GoogleDriveManager
  - Frontend: Add OneDrive option to cloud storage UI
  - Auth: Implement Azure AD OAuth2 flow
  - Database: Store encrypted tokens in user settings
  
Database: Update user_settings schema for onedrive_token
Testing: Add test_onedrive.py integration tests

Acceptance Criteria:
  - Users can connect OneDrive account
  - Users can browse and select files from OneDrive
  - Files can be processed same as Google Drive files
```

**Deliverable:**
- Feature plan document
- List of files to modify
- Acceptance criteria
- Estimated effort (hours)

---

### Phase 2: Backend Implementation (30 min)
**Goal:** Implement backend logic and integrations

**Steps for OneDrive Integration:**

1. **Create OneDrive Manager Service**
```python
# app/cloud/onedrive_manager.py
from typing import List, Dict, Optional

class OneDriveManager:
    """Manage OneDrive operations via Microsoft Graph API."""
    
    GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"
    
    def __init__(self, access_token: str):
        """Initialize with access token."""
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    async def list_files(
        self,
        drive_id: Optional[str] = None,
        query: Optional[str] = None
    ) -> List[Dict]:
        """
        List files from OneDrive.
        
        Args:
            drive_id: Specific drive ID (optional)
            query: Optional filter query
            
        Returns:
            List of file metadata
        """
        # Implementation
        pass
    
    async def download_file(self, file_id: str) -> bytes:
        """Download file from OneDrive."""
        # Implementation
        pass
```

2. **Implement OAuth Flow**
```python
# app/auth/azure_oauth.py
class AzureOAuthHandler:
    """Handle Azure AD OAuth2 flow."""
    
    def __init__(self, config: Dict):
        """Initialize with Azure app credentials."""
        self.client_id = config['client_id']
        self.client_secret = config['client_secret']
        self.redirect_uri = config['redirect_uri']
    
    def get_authorization_url(self) -> str:
        """Get Azure login URL."""
        # Implementation
        pass
    
    async def exchange_code_for_token(self, code: str) -> Dict:
        """Exchange authorization code for access token."""
        # Implementation
        pass
```

3. **Add to Cloud Storage Registry**
```python
# app/cloud/__init__.py
from .google_drive_manager import GoogleDriveManager
from .onedrive_manager import OneDriveManager

CLOUD_PROVIDERS = {
    'google_drive': GoogleDriveManager,
    'onedrive': OneDriveManager
}
```

4. **Dependencies**
```
# requirements.txt
python-dotenv>=0.19.0
google-auth-oauthlib>=0.4.6
google-api-python-client>=2.50.0
microsoft-graph-core>=0.2.2
requests>=2.28.0
```

**Deliverable:**
- OneDriveManager fully implemented
- OAuth flow working
- Tests passing
- Type hints present
- Error handling added

---

### Phase 3: Frontend Implementation (30 min)
**Goal:** Build UI components and integrate with backend

**Steps for OneDrive UI:**

1. **Create Cloud Storage Component**
```python
# ui/components/cloud_storage.py
import streamlit as st
from typing import Optional, List

def render_cloud_storage_selector() -> Optional[bytes]:
    """
    Render cloud storage file selector.
    
    Returns:
        Selected file content or None
    """
    st.subheader("📁 Cloud Storage")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔵 Google Drive"):
            st.session_state.cloud_provider = 'google_drive'
    with col2:
        if st.button("🟢 OneDrive"):
            st.session_state.cloud_provider = 'onedrive'
    
    if 'cloud_provider' in st.session_state:
        provider = st.session_state.cloud_provider
        
        if provider == 'google_drive':
            return _render_google_drive_selector()
        elif provider == 'onedrive':
            return _render_onedrive_selector()
    
    return None

def _render_onedrive_selector() -> Optional[bytes]:
    """Render OneDrive file selector."""
    st.write("**OneDrive Files**")
    
    if 'onedrive_token' not in st.session_state:
        if st.button("Connect OneDrive Account"):
            # Trigger OAuth flow
            st.session_state.show_onedrive_auth = True
    else:
        # List and select OneDrive files
        # Implementation...
        pass
    
    return None
```

2. **Update State Management**
```python
# Initialize session state
if 'cloud_provider' not in st.session_state:
    st.session_state.cloud_provider = None

if 'onedrive_token' not in st.session_state:
    st.session_state.onedrive_token = None
```

3. **Update Main Settings UI**
```python
# ui/components/settings.py
def render_settings_panel():
    """Render user settings."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Settings")
    
    with st.sidebar.expander("Cloud Storage"):
        # Google Drive settings
        if st.checkbox("Enable Google Drive"):
            st.write("✅ Google Drive configured")
        
        # OneDrive settings (NEW)
        if st.checkbox("Enable OneDrive"):
            if st.button("Connect OneDrive"):
                # Trigger OAuth
                pass
            st.write("✅ OneDrive configured")
```

**Deliverable:**
- Cloud storage UI component created
- OneDrive option integrated
- Backend API integrated
- Type safety verified
- No console errors

---

### Phase 4: Testing (20 min)
**Goal:** Verify feature works correctly

**Unit Tests:**
```python
# tests/unit/test_onedrive_manager.py
import pytest
from app.cloud.onedrive_manager import OneDriveManager

class TestOneDriveManager:
    """Test OneDrive manager functionality."""
    
    @pytest.fixture
    def manager(self):
        """Create OneDrive manager with test token."""
        return OneDriveManager(access_token="test_token_123")
    
    @pytest.mark.asyncio
    async def test_list_files(self, manager, mock_requests):
        """Test listing OneDrive files."""
        mock_requests.get.return_value.json.return_value = {
            'value': [
                {'id': 'file1', 'name': 'document.pdf'},
                {'id': 'file2', 'name': 'spreadsheet.xlsx'}
            ]
        }
        
        files = await manager.list_files()
        assert len(files) == 2
        assert files[0]['name'] == 'document.pdf'
    
    @pytest.mark.asyncio
    async def test_download_file(self, manager, mock_requests):
        """Test downloading OneDrive file."""
        file_content = b'test file content'
        mock_requests.get.return_value.content = file_content
        
        result = await manager.download_file('file1')
        assert result == file_content
```

**Integration Tests:**
```python
# tests/integration/test_onedrive_oauth.py
import pytest
from app.auth.azure_oauth import AzureOAuthHandler

def test_authorization_url_generation():
    """Test Azure OAuth authorization URL."""
    config = {
        'client_id': 'test_client_id',
        'client_secret': 'test_secret',
        'redirect_uri': 'http://localhost:8501'
    }
    
    handler = AzureOAuthHandler(config)
    url = handler.get_authorization_url()
    
    assert 'https://login.microsoftonline.com' in url
    assert 'test_client_id' in url
    assert 'redirect_uri' in url
```

**UI Tests:**
```python
# tests/ui/test_cloud_storage.py
from streamlit.testing.v1 import AppTest

def test_cloud_storage_component():
    """Test cloud storage selector component."""
    at = AppTest.from_file("ui/components/cloud_storage.py")
    at.run()
    
    # Check both storage options present
    buttons = [b.label for b in at.button]
    assert "🔵 Google Drive" in buttons
    assert "🟢 OneDrive" in buttons
```

**Run All Tests:**
```bash
pytest --cov=app --cov=ui --cov-fail-under=90
```

**Deliverable:**
- All tests passing (>90%)
- Feature works end-to-end
- Edge cases covered
- No console errors

---

### Phase 5: Documentation & Deployment (10 min)
**Goal:** Document feature and deploy to production

**Update Documentation:**

1. **CHANGELOG.md:**
```markdown
## [1.1.0] - 2025-12-31
### Added
- **OneDrive Integration**: Connect OneDrive account and process files
  - OAuth2 authentication with Azure AD
  - File browser and selector UI
  - Same processing pipeline as Google Drive
  - Files: [onedrive_manager.py](app/cloud/onedrive_manager.py), [azure_oauth.py](app/auth/azure_oauth.py), [cloud_storage.py](ui/components/cloud_storage.py)
  - Git commit: `abc123d`

### Technical Details
- **Build Performance:**
  - Build time: 8.2s (local)
  - Zero errors during deployment
```

2. **README.md Update:**
```markdown
### Cloud Storage Integration

TEXT-MINING supports multiple cloud storage providers:

- **Google Drive**: Upload documents directly from Google Drive
- **OneDrive**: Access files from Microsoft OneDrive

Each provider can be enabled independently in Settings.
```

3. **Code Comments:**
```python
def _render_onedrive_selector() -> Optional[bytes]:
    """
    Render OneDrive file selector with authentication.
    
    This component handles:
    - OAuth2 flow with Azure AD
    - Token management and refresh
    - File browsing and selection
    - Direct file download and processing
    
    Note:
        Requires Microsoft Azure app registration with:
        - client_id and client_secret configured
        - OAuth redirect URI matching app config
    """
    # Implementation
```

**Deployment:**
```bash
git add -A
git commit -m "feat(cloud): add OneDrive integration with Azure OAuth"
git push origin dev

# Wait for GitHub Actions checks ✅
# Get code review approval ✅
# Deploy with /dep
```

**Deliverable:**
- CHANGELOG.md updated
- README.md updated with OneDrive mention
- Code comments explain feature
- Conventional commit message
- Ready for production

---

## Quick Feature Development Checklist

### Planning Phase
- [ ] Feature requirements documented
- [ ] Affected components identified
- [ ] Database schema changes planned (if any)
- [ ] Acceptance criteria defined

### Backend Phase
- [ ] New services implemented
- [ ] OAuth/API integrations working
- [ ] Database operations tested
- [ ] Error handling added
- [ ] Type hints present

### Frontend Phase
- [ ] New components created
- [ ] Backend API integrated
- [ ] Type safety verified
- [ ] Responsive design tested
- [ ] No console errors

### Testing Phase
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] UI tests passing
- [ ] Overall coverage >90%
- [ ] Edge cases covered

### Documentation Phase
- [ ] CHANGELOG.md updated
- [ ] README.md updated
- [ ] Code comments added
- [ ] Conventional commit ready

### Deployment
- [ ] All checks passing
- [ ] Code review approved
- [ ] Pre-flight checks passed
- [ ] Deployment successful
- [ ] Health checks verify

---

*Last Updated: December 31, 2025*
*Project: TEXT-MINING v1.0*
*Status: Production Ready*
