# 📊 Text-Mining Research Tool

> A professional multi-user text-mining application for academic research and analysis with advanced features including Firebase authentication, cloud storage integration, and multi-language support.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B)](https://streamlit.io/)
[![Firebase](https://img.shields.io/badge/Firebase-Admin-orange)](https://firebase.google.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 🌟 Features

### Core Text Mining
- **Multi-format Document Processing**: PDF, DOCX, TXT, HTML, and Images (OCR)
- **Keyword Extraction & Grouping**: Analyze documents against user-defined keyword groups
- **Advanced OCR**: EasyOCR support for Vietnamese and English text
- **Web Search Integration**: Extract and analyze content from URLs
- **Excel Reporting**: Generate comprehensive reports with keyword statistics
- **AI-Powered Analysis**: Google Gemini integration for advanced text understanding

### User Management (✨ New)
- **Firebase Authentication**: Secure Google Sign-in
- **Per-user Settings**: Individual preferences and configurations
- **Session Management**: Persistent sessions across browser refreshes
- **User Profiles**: Firestore-backed user data storage

### Cloud Integration (✨ New)
- **Google Drive**: Connect and access files from Google Drive
- **OneDrive**: Connect and access files from Microsoft OneDrive
- **Cloud Storage**: Upload and sync analysis results to cloud
- **OAuth2 Security**: Secure cloud authentication

### Customization (✨ New)
- **Theme Switcher**: Light, Dark, and System (auto) themes
- **Multi-language**: English and Vietnamese (Sentence case)
- **Custom API Keys**: Per-user Gemini API key configuration
- **Encrypted Storage**: Secure encryption for sensitive data

### Professional UI
- **Modern Interface**: Clean, academic-style interface built with Streamlit
- **Responsive Design**: Works on desktop and mobile devices
- **Intuitive Navigation**: Easy-to-use controls and settings
- **Real-time Updates**: Live processing status and progress tracking

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Features Guide](#-features-guide)
- [Architecture](#-architecture)
- [Security](#-security)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone <repository-url>
cd TEXT-MINING
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Firebase
Follow the [Firebase Setup Guide](SETUP_FIREBASE.md) to configure authentication.

### 4. Launch Application
```bash
streamlit run ui/main.py
```

The app will open at `http://localhost:8501`

---

## 📦 Prerequisites

### Required
- **Python 3.8 or higher**
- **pip package manager**
- **Google Firebase project** (for authentication)

### Optional
- **Google Cloud project** (for Google Drive integration)
- **Azure AD app** (for OneDrive integration)
- **Google Gemini API key** (for AI features)

---

## 🔧 Installation

### Standard Installation

1. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**:
   ```bash
   python -c "import streamlit; print(f'Streamlit {streamlit.__version__}')"
   ```

### Development Installation

For development with additional tools:
```bash
pip install -r requirements.txt
pip install pytest black flake8 pip-audit
```

---

## ⚙️ Configuration

### 1. Firebase Authentication (Required)

Create a Firebase project and download credentials:

```bash
# 1. Go to https://console.firebase.google.com/
# 2. Create a new project
# 3. Enable Google Sign-in authentication
# 4. Download service account credentials
# 5. Save as config/firebase_config.json
```

📖 Detailed guide: [SETUP_FIREBASE.md](SETUP_FIREBASE.md)

### 2. Google Drive Integration (Optional)

Enable Google Drive API and configure OAuth:

```bash
# 1. Go to https://console.cloud.google.com/
# 2. Enable Google Drive API
# 3. Create OAuth 2.0 credentials
# 4. Save as config/google_oauth_credentials.json
```

📖 Detailed guide: [SETUP_GOOGLE_CLOUD.md](SETUP_GOOGLE_CLOUD.md)

### 3. OneDrive Integration (Optional)

Register app in Azure AD:

```bash
# 1. Go to https://portal.azure.com/
# 2. Register application in Azure AD
# 3. Create client secret
# 4. Save config as config/azure_config.json
```

📖 Detailed guide: [SETUP_AZURE.md](SETUP_AZURE.md)

### 4. Environment Variables

Create `config/.env` file:

```env
# Encryption key (auto-generated if not provided)
ENCRYPTION_KEY=your-fernet-encryption-key

# Optional: Google Gemini API (default)
GEMINI_API_KEY=your-default-gemini-api-key

# Optional: Firebase credentials path
FIREBASE_CREDENTIALS_PATH=config/firebase_config.json

# Environment
ENVIRONMENT=development  # or 'production'
```

---

## 💡 Usage

### First Time User

1. **Launch application**:
   ```bash
   streamlit run ui/main.py
   ```

2. **Sign in with Google**:
   - Click "Sign in with Google" button
   - Authorize the application
   - You'll be redirected to the main interface

3. **Configure settings**:
   - Open "⚙️ Settings" in the left sidebar
   - Add your Gemini API key (optional)
   - Choose your preferred language
   - Select your theme preference

4. **Start analyzing**:
   - Upload keyword file (CSV, XLSX, or TXT)
   - Upload documents to analyze
   - Click "Process Documents"
   - View and download results

### Typical Workflow

```
┌─────────────────┐
│  1. Sign In     │
└────────┬────────┘
         │
┌────────▼────────┐
│ 2. Upload       │
│    Keywords     │
└────────┬────────┘
         │
┌────────▼────────┐
│ 3. Select       │
│    Files        │
│  (Local/Cloud)  │
└────────┬────────┘
         │
┌────────▼────────┐
│ 4. Choose       │
│    Extraction   │
│    Mode         │
└────────┬────────┘
         │
┌────────▼────────┐
│ 5. Process      │
│    Documents    │
└────────┬────────┘
         │
┌────────▼────────┐
│ 6. View &       │
│    Export       │
│    Results      │
└─────────────────┘
```

---

## 📚 Features Guide

### Authentication

**Google Sign-in**: Secure authentication powered by Firebase

- **Single Sign-On (SSO)**: Use your Google account
- **Session persistence**: Stay logged in across refreshes
- **Secure logout**: Complete session cleanup

📖 Guide: [AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md)

### API Key Management

**Per-user API Keys**: Each user can configure their own Google Gemini API key

- **Encrypted storage**: Keys encrypted with Fernet
- **Validation**: Test API key before saving
- **Show/hide**: Toggle visibility for security

📖 Guide: [API_KEY_GUIDE.md](API_KEY_GUIDE.md)

### Cloud Storage

**Google Drive & OneDrive**: Connect cloud storage accounts

- **OAuth2 authentication**: Secure cloud connection
- **File browsing**: Browse and select files from cloud
- **Direct processing**: Process cloud files without downloading
- **Per-user credentials**: Individual cloud connections

📖 Setup:
- [SETUP_GOOGLE_CLOUD.md](SETUP_GOOGLE_CLOUD.md)
- [SETUP_AZURE.md](SETUP_AZURE.md)

### Theme Switcher

**Visual customization**: Choose your preferred theme

- **Light theme**: Bright, high-contrast interface
- **Dark theme**: Easy on eyes in low-light
- **System theme**: Auto-match OS theme
- **Instant switching**: No page reload required

Features:
- 40+ customized CSS variables
- Consistent styling across all components
- Accessible color contrasts

### Multi-language Support

**Bilingual interface**: Switch between English and Vietnamese

- **English**: Full feature support
- **Vietnamese (Tiếng Việt)**: Sentence case formatting
- **Per-user preference**: Language choice persists
- **Instant switching**: UI updates immediately

📖 Guide: [LANGUAGE_GUIDE.md](LANGUAGE_GUIDE.md)

### Text Extraction Modes

**Choose extraction method based on your needs:**

1. **Local OCR**:
   - Fast and free
   - Uses EasyOCR and regex
   - Best for: Clear, typed documents

2. **OCR AI**:
   - High accuracy
   - Uses Gemini Vision as OCR
   - Best for: Handwritten or low-quality scans
   - Requires: Gemini API key

3. **ALL AI**:
   - Full semantic understanding
   - Advanced context analysis
   - Best for: Complex documents
   - Requires: Gemini API key

---

## 🏗️ Architecture

### Project Structure

```
TEXT-MINING/
├── app/
│   ├── auth/                   # Authentication modules
│   │   ├── firebase_manager.py     # Firebase Admin SDK
│   │   ├── session_manager.py      # Session state management
│   │   └── streamlit_auth.py       # Login UI
│   ├── cloud/                  # Cloud storage integrations
│   │   ├── google_drive_manager.py # Google Drive API
│   │   └── onedrive_manager.py     # Microsoft Graph API
│   ├── core/                   # Core text mining logic
│   │   ├── extractor.py            # Text extraction
│   │   ├── analyzer.py             # Keyword analysis
│   │   └── ai_service.py           # Gemini AI integration
│   ├── database/               # Data persistence
│   │   └── settings_manager.py     # User settings & encryption
│   ├── i18n/                   # Internationalization
│   │   └── translator.py           # Translation service
│   ├── ui/                     # UI managers
│   │   └── theme_manager.py        # Theme switching
│   ├── utils/                  # Utilities
│   └── config.py               # Application configuration
├── ui/
│   ├── components/             # Reusable UI components
│   │   ├── api_key_input.py        # API key configuration
│   │   ├── cloud_storage.py        # Cloud storage UI
│   │   ├── theme_selector.py       # Theme selection
│   │   └── language_selector.py    # Language selection
│   ├── main.py                 # Authentication wrapper
│   └── main_app.py             # Main application logic
├── locales/                    # Translation files
│   ├── en.json                 # English translations
│   └── vi.json                 # Vietnamese translations
├── config/                     # Configuration files (excluded)
│   ├── firebase_config.json        # Firebase credentials
│   ├── google_oauth_credentials.json
│   ├── azure_config.json
│   └── .env                        # Environment variables
├── data/
│   ├── input/                  # Input documents
│   └── output/                 # Analysis results
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

### Technology Stack

#### Backend
- **Python 3.8+**: Core language
- **Firebase Admin SDK**: Authentication & database
- **Google Generative AI**: Gemini API integration
- **Cryptography (Fernet)**: Data encryption
- **EasyOCR**: Optical character recognition
- **Pandas**: Data manipulation
- **PyMuPDF**: PDF processing

#### Frontend
- **Streamlit**: Web framework
- **Altair**: Data visualization
- **Matplotlib**: Charts and graphs

#### Cloud & APIs
- **Firebase Firestore**: User data storage
- **Google Drive API**: Cloud file access
- **Microsoft Graph API**: OneDrive integration
- **Google Gemini API**: AI-powered analysis

#### Security
- **Fernet Encryption**: Symmetric encryption
- **OAuth 2.0**: Cloud authentication
- **Firebase Authentication**: User management
- **Environment Variables**: Secrets management

---

## 🔒 Security

### Security Features

✅ **Authentication**
- Firebase Google Sign-in
- Server-side token verification
- Secure session management

✅ **Data Encryption**
- Fernet encryption for API keys
- Encrypted cloud credentials
- Environment variable protection

✅ **Access Control**
- Per-user data isolation
- Firestore document-level security
- No cross-user data access

✅ **Best Practices**
- Credentials excluded from git
- HTTPS recommended for production
- Regular dependency updates
- Input validation

### Security Rating: ⭐⭐⭐⭐ (4/5)

📖 Full security audit: [SECURITY_AUDIT.md](SECURITY_AUDIT.md)

### Security Recommendations

For production deployment:
1. ✅ Enable HTTPS
2. ✅ Configure Firestore security rules
3. ✅ Set up production OAuth redirect URIs
4. ✅ Implement rate limiting
5. ✅ Use cloud secrets manager

---

## 🚢 Deployment

### Local Development

```bash
# Development mode (default)
streamlit run ui/main.py
```

### Production Deployment

#### Option 1: Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add secrets in Streamlit Cloud dashboard
5. Deploy

#### Option 2: Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "ui/main.py", "--server.address=0.0.0.0"]
```

```bash
docker build -t text-mining-app .
docker run -p 8501:8501 text-mining-app
```

#### Option 3: Cloud Run (Google Cloud)

```bash
# Build and deploy
gcloud run deploy text-mining-app \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

📖 Detailed guide: [DEPLOYMENT.md](DEPLOYMENT.md) *(coming soon)*

---

## 🐛 Troubleshooting

### Common Issues

#### "Firebase credentials not found"
```bash
# Solution: Download Firebase service account credentials
# Save as config/firebase_config.json
# See SETUP_FIREBASE.md for details
```

#### "API key validation failed"
```bash
# Solution: Verify your Gemini API key
# Get a valid key at: https://aistudio.google.com/app/apikey
```

#### "Cloud storage not connecting"
```bash
# Solution: Check OAuth credentials
# For Drive: See SETUP_GOOGLE_CLOUD.md
# For OneDrive: See SETUP_AZURE.md
```

#### "Encryption key error"
```bash
# Solution: Encryption key will auto-generate
# Or set manually in config/.env:
# ENCRYPTION_KEY=your-fernet-key
```

### Getting Help

1. **Check documentation**: Review the relevant guide
2. **Check logs**: Look for error messages in console
3. **Verify configuration**: Ensure all config files present
4. **Test connection**: Use provided connection test scripts

📖 Full testing checklist: [TESTING_CHECKLIST.md](TESTING_CHECKLIST.md)

---

## 📖 Documentation

### Setup Guides
- [Firebase Setup](SETUP_FIREBASE.md) - Authentication configuration
- [Google Cloud Setup](SETUP_GOOGLE_CLOUD.md) - Drive integration
- [Azure Setup](SETUP_AZURE.md) - OneDrive integration

### Feature Guides
- [Authentication Guide](AUTHENTICATION_GUIDE.md) - User management
- [API Key Guide](API_KEY_GUIDE.md) - API key configuration
- [Language Guide](LANGUAGE_GUIDE.md) - Multi-language support

### Technical Documentation
- [Implementation Plan](IMPLEMENTATION_PLAN.md) - Development roadmap
- [Testing Checklist](TESTING_CHECKLIST.md) - QA procedures
- [Security Audit](SECURITY_AUDIT.md) - Security assessment

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Areas for Contribution
- 🌐 Additional language translations
- 🎨 New themes
- 📊 Advanced analytics features
- 🔌 Additional cloud storage providers
- 📝 Documentation improvements
- 🐛 Bug fixes

### Development Process

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes** and test thoroughly
4. **Commit changes**: `git commit -m 'feat: Add amazing feature'`
5. **Push to branch**: `git push origin feature/amazing-feature`
6. **Open Pull Request**

### Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test additions or changes
- `chore:` Maintenance tasks

---

## 📊 Project Status

### Implementation Progress

| Session | Feature | Status |
|---------|---------|--------|
| Session 1 | Project Setup & Infrastructure | ✅ Complete |
| Session 2 | Firebase Authentication | ✅ Complete |
| Session 3 | API Key Management | ✅ Complete |
| Session 4 | Cloud Storage Integration | ✅ Complete |
| Session 5 | Theme Switcher | ✅ Complete |
| Session 6 | Multi-language Support | ✅ Complete |
| Session 7 | Testing & Documentation | ✅ Complete |

**Overall: 7/7 sessions complete (100%)** 🎉

### Version History

- **v1.0.0** (Current) - Full multi-user system with all planned features
- **v0.5.0** - Original single-user text mining tool

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Firebase** - Authentication and database
- **Google Cloud** - Drive API and Gemini AI
- **Microsoft Azure** - OneDrive integration
- **Streamlit** - Amazing web framework
- **EasyOCR** - Optical character recognition
- **All contributors** - Thank you! 🎉

---

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Email**: your-email@example.com

---

<div align="center">

**Built with ❤️ for the research community**

[⬆ Back to Top](#-text-mining-research-tool)

</div>
