# Text-Mining Research Tool

A professional text-mining application for academic research and analysis.

## Features

- **Multi-format Document Processing**: PDF, DOCX, TXT, HTML, and Images (with OCR)
- **Keyword Extraction & Grouping**: Analyze documents against user-defined keyword groups
- **Advanced OCR**: EasyOCR support for Vietnamese and English
- **Web Search Integration**: Extract and analyze content from URLs
- **Excel Reporting**: Generate comprehensive reports with keyword statistics
- **Automation**: File watchdog service for monitoring input directories
- **Professional UI**: Clean, academic-style interface built with Streamlit

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Start

1. **Clone or download this repository**

2. **Run the setup script**:
   ```bash
   python setup.py
   ```

3. **Launch the application**:
   ```bash
   python run_app.py
   ```

The app will open in your default web browser at `http://localhost:8501`

## Configuration

### API Keys (Optional)

For advanced features, you can configure API keys by setting environment variables:

- **GEMINI_API_KEY**: Google Gemini API for advanced text analysis
  - Get yours at: https://aistudio.google.com/app/apikey
  
- **GOOGLE_SEARCH_API_KEY** & **GOOGLE_SEARCH_ENGINE_ID**: For web search functionality
  - Get yours at: https://console.cloud.google.com/

You can set these in your environment or edit `text_mining_app/app/config.py` directly.

## Usage

1. **Upload Keywords**:
   - In the sidebar, upload a CSV or XLSX file with your keyword groups
   - Format: Column 1 = Group ID, Column 2 = Keywords (comma-separated)
   - Example provided in `docs/fintech_keywords.csv`

2. **Process Documents**:
   - Go to "File Processing" tab
   - Upload documents (PDF, DOCX, TXT, or images)
   - Click "Start Processing"

3. **View Results**:
   - Check the "Analysis Results" tab for visualizations
   - Reports are automatically saved to `text_mining_app/data/output/`

## Directory Structure

```
text_mining_app/
├── app/                    # Core application logic
│   ├── core/              # Main processing modules
│   │   ├── analyzer.py    # Keyword analysis
│   │   ├── extractor.py   # Text extraction (PDF, OCR, etc.)
│   │   ├── web_search.py  # Web scraping
│   │   └── watchdog_service.py  # File monitoring
│   ├── utils/             # Utility functions
│   └── config.py          # Configuration settings
├── ui/                    # Streamlit UI
│   ├── main.py           # Main application entry
│   └── styles.css        # Custom styling
└── data/                  # Data directory
    ├── input/            # Place files here for processing
    └── output/           # Generated reports

```

## Troubleshooting

### ModuleNotFoundError: No module named 'app'

Make sure you're running the app from the project root directory (TEXT-MINING), not from inside text_mining_app.

### OCR not working

EasyOCR will download language models on first run. This may take a few minutes and requires internet connection.

### Memory issues with large PDFs

For very large documents, consider:
- Processing fewer files at once
- Enabling GPU support in config.py (if you have a compatible GPU)

## Credits

Built with:
- Streamlit - Web UI framework
- PyMuPDF & PyPDF2 - PDF processing
- EasyOCR - OCR engine
- OpenCV - Image processing
- Pandas & OpenPyXL - Data analysis and Excel export

## License

For academic research purposes.
