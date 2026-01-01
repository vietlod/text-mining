"""
Main application logic (refactored from original main.py).

This module contains the core application functionality,
separated from authentication logic for better maintainability.
"""

import streamlit as st
import os
import sys
import pandas as pd
import time
import datetime
import matplotlib.pyplot as plt
import altair as alt

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.config import APP_TITLE, APP_VERSION, INPUT_DIR, OUTPUT_DIR
from app.core.extractor import TextExtractor
from app.core.analyzer import KeywordAnalyzer
from app.core.ai_service import GeminiService
from app.utils.file_handler import load_keywords, export_to_excel
from app.utils.logger import setup_logger
from app.auth.firebase_manager import firebase_manager
from app.auth.session_manager import SessionManager
from app.database.settings_manager import SettingsManager
from app.ui.theme_manager import ThemeManager
from ui.components.api_key_input import render_api_key_input
from ui.components.cloud_storage import render_cloud_storage_settings, render_file_source_selector, _load_files_from_drive
from ui.components.theme_selector import render_compact_theme_selector

logger = setup_logger("UI")

# Try to import wordcloud
try:
    from wordcloud import WordCloud
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False


# Load CSS
def local_css(file_name):
    """Load custom CSS file."""
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass


def render_main_app():
    """Render the main application UI and logic."""
    
    # Load custom CSS
    local_css(os.path.join(os.path.dirname(__file__), "styles.css"))
    
    # Initialize Session State
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = []
    if 'keywords_map' not in st.session_state:
        st.session_state.keywords_map = {}
    if 'max_group' not in st.session_state:
        st.session_state.max_group = 0
    if 'logs' not in st.session_state:
        st.session_state.logs = []
    if 'total_tokens' not in st.session_state:
        st.session_state.total_tokens = 0
    if 'all_keyword_counts' not in st.session_state:
        st.session_state.all_keyword_counts = {}
    if 'all_group_counts' not in st.session_state:
        st.session_state.all_group_counts = {}
    if 'ai_insights' not in st.session_state:
        st.session_state.ai_insights = ""

    def log_message(msg):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        st.session_state.logs.append(f"[{timestamp}] {msg}")

    # Main Layout
    st.title(f"📊 {APP_TITLE}")

    # Get current user and setup managers
    user = SessionManager.get_current_user()
    user_id = user['uid'] if user else None
    
    # If no user, create guest user for Drive connection
    # Use unique session ID for each browser session
    if not user_id:
        if 'guest_session_id' not in st.session_state:
            import uuid
            st.session_state.guest_session_id = str(uuid.uuid4())[:8]
            logger.info(f"Generated unique guest session ID: {st.session_state.guest_session_id}")
        
        guest_user_id = f'guest_{st.session_state.guest_session_id}'
        guest_user = {
            'uid': guest_user_id,
            'email': f'guest_{st.session_state.guest_session_id}@local.app',
            'name': f'Guest User ({st.session_state.guest_session_id})',
            'email_verified': False
        }
        SessionManager.set_user(guest_user, None)
        user_id = guest_user_id
        logger.info(f"Guest user created for Drive connection: {user_id}")

    # Initialize settings manager
    settings_manager = SettingsManager(firebase_manager.get_firestore_client())

    # CRITICAL: Check for OAuth callbacks (Drive/OneDrive) FIRST, before anything else
    # This needs to be checked early, before initializing other components
    # Drive OAuth callbacks work with guest user too
    query_params = st.query_params

    # Check for Drive callback if there's a code in URL
    # Works with both authenticated users and guest users
    if 'code' in query_params and user_id:
        # Wrap EVERYTHING in try-except to prevent blocking the app
        try:
            # CRITICAL: Capture and decode code FIRST, before any processing
            current_code = query_params.get('code')
            import urllib.parse
            decoded_code = urllib.parse.unquote(current_code)
            current_code = decoded_code  # Use decoded code for all operations
            
            # CRITICAL: Use a processing lock to prevent ANY duplicate processing
            # Use decoded code for lock key to ensure consistency
            processing_lock_key = f'oauth_processing_{hash(current_code)}'

            if st.session_state.get(processing_lock_key, False):
                # This code is ALREADY being processed in this session - ABORT immediately
                logger.warning(f"DUPLICATE: OAuth code is already being processed! Aborting. Code hash: {hash(current_code)}")
                # Clear query params and release lock
                st.query_params.clear()
                if processing_lock_key in st.session_state:
                    del st.session_state[processing_lock_key]
                # Don't stop - let the app continue
            else:
                # Set the processing lock IMMEDIATELY - before doing ANYTHING else
                st.session_state[processing_lock_key] = True
                logger.info(f"✓ Processing lock acquired for code: {hash(current_code)}")

                # Now capture the state
                current_state = query_params.get('state', '')
                
                # CRITICAL: Clear query params IMMEDIATELY to prevent re-processing
                # Do this BEFORE any other processing
                logger.info(f"Clearing query params immediately (code: {hash(current_code)})")
                st.query_params.clear()

                # Check if this is Drive OAuth by checking:
                # 1. Session state (oauth_type, drive_oauth_state)
                # 2. Firestore state (persistent across redirects)
                oauth_type = st.session_state.get('oauth_type')
                drive_oauth_state = st.session_state.get('drive_oauth_state')
                
                # Check Firestore for persistent OAuth state
                oauth_state_from_firestore = None
                if current_state:
                    # Try with user_id first
                    oauth_state_from_firestore = settings_manager.get_oauth_state(user_id, current_state)
                    # If not found, try without user_id (search by state only)
                    if not oauth_state_from_firestore:
                        oauth_state_from_firestore = settings_manager.get_oauth_state('', current_state)
                        if oauth_state_from_firestore:
                            logger.info(f"Found OAuth state in Firestore (without user_id): type={oauth_state_from_firestore.get('oauth_type')}")
                
                # More precise detection: Handle as Drive callback if:
                # 1. oauth_type is explicitly 'drive' in session, OR
                # 2. drive_oauth_state exists in session, OR
                # 3. OAuth state exists in Firestore with oauth_type='drive', OR
                # 4. User is authenticated AND no Firebase callback indicators (fallback)
                firestore_oauth_type = oauth_state_from_firestore.get('oauth_type') if oauth_state_from_firestore else None
                
                is_drive_callback = (
                    oauth_type == 'drive' or 
                    drive_oauth_state is not None or
                    firestore_oauth_type == 'drive' or
                    # Fallback: If user authenticated and no Firebase indicators, assume Drive callback
                    (user_id and oauth_type is None and drive_oauth_state is None and firestore_oauth_type != 'firebase')
                )
                
                if oauth_state_from_firestore:
                    logger.info(f"✅ Found OAuth state in Firestore: type={firestore_oauth_type}, user_id={oauth_state_from_firestore.get('user_id')}")
                else:
                    logger.warning(f"⚠️ OAuth state not found in Firestore. State: {current_state[:20] if current_state else 'None'}...")
                    if user_id:
                        logger.info(f"Using fallback detection: user exists (authenticated or guest), assuming Drive callback")

                # Query params already cleared above
                # Now process Drive callback if detected
                if is_drive_callback:
                    from ui.components.cloud_storage import _handle_drive_oauth_callback

                    logger.info(f"→ Handling Drive OAuth callback (oauth_type: {oauth_type}, user: {user_id[:8]}...)")
                    logger.info(f"  Code hash: {hash(current_code)}")
                    logger.info(f"  Processing lock: {processing_lock_key}")

                    # Language feature removed - using Vietnamese text directly
                    t = {'connected': 'Đã kết nối', 'not_connected': 'Chưa kết nối'}

                    # Log before processing
                    logger.info(f"→ About to exchange OAuth code (hash: {hash(current_code)})")

                    # Process the callback with the captured code
                    # Note: Processing lock will be released inside _handle_drive_oauth_callback
                    _handle_drive_oauth_callback(settings_manager, user_id, current_code, current_state, t)

                    logger.info(f"✓ OAuth callback completed")
                    
                    # Lock is released in _handle_drive_oauth_callback, but ensure it's released here too
                    if processing_lock_key in st.session_state:
                        del st.session_state[processing_lock_key]
                        logger.info(f"✓ Processing lock released in main_app.py")
                else:
                    # Not a Drive callback - could be leftover code or invalid callback
                    # Clear query params and release lock
                    logger.warning(f"Code detected but not identified as Drive callback. oauth_type: {oauth_type}, drive_oauth_state exists: {drive_oauth_state is not None}, firestore_type: {firestore_oauth_type}, user_id: {user_id}")
                    logger.warning(f"  This might be an invalid or expired OAuth callback")
                    # Ensure query params are cleared (already cleared above, but double-check)
                    if 'code' in st.query_params:
                        st.query_params.pop('code')
                    if 'state' in st.query_params:
                        st.query_params.pop('state')
                    # Release lock if not processing
                    if processing_lock_key in st.session_state:
                        del st.session_state[processing_lock_key]
                        logger.info(f"✓ Processing lock released (not Drive callback)")
        except Exception as e:
            # If ANYTHING goes wrong, just log and continue - don't block the app
            logger.error(f"✗ Error in OAuth callback handling: {e}", exc_info=True)
            # Clear query params to allow access to app
            st.query_params.clear()
            # Clear any locks
            try:
                if 'processing_lock_key' in locals():
                    if processing_lock_key in st.session_state:
                        del st.session_state[processing_lock_key]
            except:
                pass
            # Show brief error but don't stop the app
            st.error("⚠️ OAuth error occurred. Please try connecting again from Settings.")
            # Continue to render the app normally

    # Hardcode English - language selector removed
    # Language feature removed - using Vietnamese text directly

    # Initialize theme manager and apply theme
    theme_manager = ThemeManager(settings_manager, user_id)
    theme_manager.apply_theme()

    # Get user's API key
    user_api_key = settings_manager.get_api_key(user_id) if user_id else None

    # Create 2 columns
    left_col, right_col = st.columns([1, 2], gap="large")

    # --- Sidebar: Global Settings ---
    with st.sidebar:
        st.markdown("### ⚙️ Cài đặt")
        
        # 1. Theme
        render_compact_theme_selector(theme_manager)
        st.markdown('<div class="sidebar-separator"></div>', unsafe_allow_html=True)
        
        # 2. API Key
        with st.expander("🔑 Gemini API Key", expanded=not user_api_key):
            has_api_key = render_api_key_input(settings_manager, user_id)
            if not has_api_key:
                st.warning("⚠️ Vui lòng nhập API Key để sử dụng tính năng AI")
        
        # 3. Cloud Storage
        with st.expander("☁️ Cloud Storage", expanded=False):
            render_cloud_storage_settings(settings_manager, user_id)

    with left_col:
        # Removed "Task Configuration" header as requested

        # --- 1. Document Input (Task Card) ---
        with st.container(border=True):
            st.markdown("""
            <div style="background-color: #e3f2fd; padding: 10px; border-radius: 5px; margin-bottom: 15px; border-left: 5px solid #2196f3;">
                <h3 style="margin: 0; color: #0d47a1; font-size: 1.2rem;">📁 Document Input</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # File source selector
            file_source = render_file_source_selector(settings_manager, user_id)
            
            uploaded_files = []
            
            if file_source == 'local':
                # Local file upload
                uploaded_files = st.file_uploader("Upload Documents", 
                                                type=['pdf', 'docx', 'txt', 'png', 'jpg', 'html'], 
                                                accept_multiple_files=True)
            elif file_source == 'google_drive':
                # Google Drive file selection
                uploaded_files = _load_files_from_drive(settings_manager, user_id)
                if uploaded_files:
                    st.caption(f"📁 {len(uploaded_files)} file(s) selected from Google Drive")
            elif file_source == 'onedrive':
                # OneDrive file selection (to be implemented)
                st.info("OneDrive file selection coming soon!")
                uploaded_files = []

        # --- 2. Keyword Management (Task Card) ---
        with st.container(border=True):
            st.markdown("""
            <div style="background-color: #e8f5e9; padding: 10px; border-radius: 5px; margin-bottom: 15px; border-left: 5px solid #4caf50;">
                <h3 style="margin: 0; color: #1b5e20; font-size: 1.2rem;">🔑 Quản lý Từ khóa</h3>
            </div>
            """, unsafe_allow_html=True)
            
            st.info(f"Đã tải: **{len(st.session_state.keywords_map)}** từ khóa")

            kw_tab1, kw_tab2 = st.tabs(["📤 Tải lên", "✍️ Nhập thủ công"])
        
            with kw_tab1:
                uploaded_kw = st.file_uploader("Upload Keywords (CSV/XLSX/TXT)", type=['csv', 'xlsx', 'txt', 'md'])
                if uploaded_kw:
                    temp_path = os.path.join(INPUT_DIR, uploaded_kw.name)
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_kw.getbuffer())
                
                    kw_map, max_g = load_keywords(temp_path)
                    if kw_map:
                        st.session_state.keywords_map = kw_map
                        st.session_state.max_group = max_g
                        st.success(f"✅ Loaded {len(kw_map)} keywords!")
                        log_message(f"Loaded keywords from {uploaded_kw.name}")
                    else:
                        st.error("❌ Failed to load keywords. Check file format.")

            with kw_tab2:
                manual_kw = st.text_area("Enter keywords (comma or newline separated)", height=150,
                                       placeholder="fintech, blockchain\nai, machine learning")
                if st.button("Load Manual Keywords"):
                    if manual_kw:
                        kw_map = {}
                        lines = manual_kw.replace('\n', ',').split(',')
                        for k in lines:
                            k = k.strip()
                            if k:
                                kw_map[k] = 0
                    
                        if kw_map:
                            st.session_state.keywords_map = kw_map
                            st.session_state.max_group = 0
                            st.success(f"✅ Loaded {len(kw_map)} keywords!")
                            log_message("Loaded manual keywords")

        # --- 3. Extraction Mode (Task Card) ---
        with st.container(border=True):
            st.markdown("""
            <div style="background-color: #f3e5f5; padding: 10px; border-radius: 5px; margin-bottom: 15px; border-left: 5px solid #9c27b0;">
                <h3 style="margin: 0; color: #4a148c; font-size: 1.2rem;">🤖 Extraction Mode</h3>
            </div>
            """, unsafe_allow_html=True)
    
            mode_descriptions = {
                "🔧 Local OCR": "Uses Python library OCR and Regex code to extract and count keywords",
                "🔥 OCR AI": "Uses Gemini Vision purely as a Super OCR engine, and uses Python code to find and count keywords",
                "🎯 ALL AI": "Uses Gemini Vision to analyze and count directly"
            }
        
            ai_mode = st.radio(
                "Select Extraction Mode:",
                options=list(mode_descriptions.keys()),
                captions=["Fast, free, no tokens", "High accuracy, uses tokens", "Semantic understanding, uses tokens"],
                help="Select the technology used for text extraction and keyword counting."
            )
        
            # Display detailed description of selected mode
            st.info(f"**{ai_mode}**: {mode_descriptions[ai_mode]}")
        
            # Set mode flags based on selection and store in session state
            st.session_state.force_ai = (ai_mode == "🔥 OCR AI")
            st.session_state.ai_keyword_search = (ai_mode == "🎯 ALL AI")
        
            # Semantic similarity slider (only visible for AI modes)
            if st.session_state.force_ai or st.session_state.ai_keyword_search:
                semantic_threshold = st.slider(
                    "Semantic Similarity Threshold",
                    min_value=70,
                    max_value=100,
                    value=85,
                    help="AI will match keywords with similarity ≥ this value. 85% is recommended."
                )
                st.session_state.semantic_threshold = semantic_threshold
            else:
                st.session_state.semantic_threshold = 85  # Default
    
        # Initialize processing state
        if 'is_processing' not in st.session_state:
            st.session_state.is_processing = False
        if 'run_completed' not in st.session_state:
            st.session_state.run_completed = False
        if 'last_run_time' not in st.session_state:
            st.session_state.last_run_time = 0
        if 'last_run_mode' not in st.session_state:
            st.session_state.last_run_mode = ""

        def start_processing_click():
            st.session_state.is_processing = True
            st.session_state.run_completed = False
            st.session_state.total_tokens = 0  # Reset tokens for new run
    
        start_btn = st.button("🚀 Start Processing", type="primary", use_container_width=True,
                              disabled=st.session_state.is_processing or not uploaded_files or not st.session_state.keywords_map,
                              on_click=start_processing_click)

    def create_bubble_chart(keyword_counts):
        """Create a bubble chart from keyword counts."""
        if not keyword_counts:
            return None
    
        data = []
        for k, v in keyword_counts.items():
            if v > 0:
                # Simple hash for consistent position
                h = hash(k)
                # Use hash to generate pseudo-random but stable x, y coordinates
                x = (h % 100) + (h % 10) * 0.1
                y = ((h // 100) % 100) + (h % 5) * 0.1
                data.append({"Keyword": k, "Count": v, "x": x, "y": y})
            
        if not data:
            return None
        
        df = pd.DataFrame(data)
    
        # Create Chart
        chart = alt.Chart(df).mark_circle().encode(
            x=alt.X('x', axis=None),
            y=alt.Y('y', axis=None),
            size=alt.Size('Count', scale=alt.Scale(range=[200, 2000]), legend=None),
            color=alt.Color('Count', scale=alt.Scale(scheme='blues'), legend=None),
            tooltip=['Keyword', 'Count']
        ).properties(
            title="Real-time Keywords (Bubble Cloud)",
            height=300
        ).configure_view(strokeWidth=0).configure_axis(grid=False)
    
        return chart

    with right_col:
        st.markdown("### 📈 Analysis Dashboard")
    
        # Show token usage at top of dashboard (updates in real-time)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Files Processed", len(st.session_state.processed_files))
        with col2:
            st.metric("Total Keywords", sum(r['total_keywords'] for r in st.session_state.processed_files) if st.session_state.processed_files else 0)
        with col3:
            st.metric("Gemini Tokens", f"{st.session_state.total_tokens:,}")
    
        tab_progress, tab_results, tab_insights, tab_logs = st.tabs(["⏳ Progress", "📊 Results", "💡 AI Insights", "📝 Logs"])
    
        with tab_progress:
            if st.session_state.is_processing and uploaded_files:
                st.toast("🚀 Processing started! Please wait...", icon="⏳")
                progress_bar = st.progress(0)
            
                # Create 2 columns for Status and Bubble Chart
                col_status, col_chart = st.columns([1, 1])
            
                with col_status:
                    status_box = st.empty()
            
                with col_chart:
                    chart_box = st.empty()
            
                extractor = TextExtractor()
                analyzer = KeywordAnalyzer()
                ai_service = GeminiService(api_key=user_api_key)
            
                # Show AI Status
                ai_status = ai_service.get_status()
                if "❌" in ai_status:
                    st.error(f"AI Status: {ai_status}")
                else:
                    st.success(f"AI Status: {ai_status}")
            
                total_files = len(uploaded_files)
                start_time = time.time()
            
                results = []
                all_kws = {}
                all_groups = {}
            
                # Use session state for mode flags
                force_ai = st.session_state.force_ai
                ai_keyword_search = st.session_state.ai_keyword_search
                semantic_threshold = st.session_state.get('semantic_threshold', 85)
            
                for i, uploaded_file in enumerate(uploaded_files):
                    current_file_name = uploaded_file.name
                    elapsed_time = time.time() - start_time
                    avg_time_per_file = elapsed_time / (i + 1) if i > 0 else 0
                    est_remaining = avg_time_per_file * (total_files - i)
                
                    tech_used = "Local OCR"
                    if force_ai:
                        tech_used = f"OCR AI (Gemini, {semantic_threshold}% sim)"
                    elif ai_keyword_search:
                        tech_used = f"ALL AI (Gemini, {semantic_threshold}% sim)"
                
                    status_box.markdown(f"""
                    **Processing:** `{current_file_name}`
                
                    | Metric | Value |
                    |---|---|
                    | **Progress** | {i+1}/{total_files} |
                    | **Mode** | {tech_used} |
                    | **Page** | Processing... |
                    | **Time** | {elapsed_time:.1f}s |
                    """)
                
                    log_message(f"Processing {current_file_name} [{tech_used}]...")
                
                    # Save file (handle both Streamlit UploadedFile and BytesIO from Drive)
                    file_path = os.path.join(INPUT_DIR, current_file_name)
                    try:
                        if hasattr(uploaded_file, 'getbuffer'):
                            # Streamlit UploadedFile
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                        elif hasattr(uploaded_file, 'read'):
                            # BytesIO from Drive (with getbuffer method added)
                            uploaded_file.seek(0)  # Reset to beginning
                            if hasattr(uploaded_file, 'getbuffer'):
                                # Use getbuffer if available (added in _load_files_from_drive)
                                with open(file_path, "wb") as f:
                                    f.write(uploaded_file.getbuffer())
                            else:
                                # Fallback to read
                                with open(file_path, "wb") as f:
                                    f.write(uploaded_file.read())
                        else:
                            logger.error(f"Unknown file type: {type(uploaded_file)}")
                            continue
                    except Exception as e:
                        logger.error(f"Failed to save file {current_file_name}: {e}", exc_info=True)
                        st.warning(f"⚠️ Failed to save {current_file_name}: {e}")
                        continue
                
                    tokens_used = 0
                    current_page_info = {"page": 0, "total": 0}
                
                    # Define progress callback for real-time updates
                    def update_page_progress(current_page, total_pages, tokens_so_far, keywords_so_far=0, keyword_counts=None):
                        current_page_info["page"] = current_page
                        current_page_info["total"] = total_pages
                        elapsed = time.time() - start_time
                        
                        # Calculate progress percentage
                        progress_pct = (current_page / total_pages * 100) if total_pages > 0 else 0
                        
                        # Estimate remaining time
                        if current_page > 0 and elapsed > 0:
                            time_per_page = elapsed / current_page
                            remaining_pages = total_pages - current_page
                            est_remaining = time_per_page * remaining_pages
                            est_remaining_str = f"{est_remaining:.1f}s"
                        else:
                            est_remaining_str = "Calculating..."
                    
                        # Update status box - this should trigger UI update
                        status_box.markdown(f"""
                        **Processing:** `{current_file_name}`
                    
                        | Metric | Value |
                        |---|---|
                        | **Progress** | {i+1}/{total_files} files |
                        | **Mode** | {tech_used} |
                        | **Page** | {current_page}/{total_pages} ({progress_pct:.1f}%) |
                        | **Keywords Found** | {keywords_so_far} |
                        | **Tokens Used** | {tokens_so_far:,} |
                        | **Elapsed Time** | {elapsed:.1f}s |
                        | **Est. Remaining** | {est_remaining_str} |
                        """)
                    
                        # Update progress bar
                        if total_pages > 0:
                            progress_bar.progress(progress_pct / 100)
                    
                        # Update Bubble Chart with real-time keyword counts
                        if keyword_counts:
                            chart = create_bubble_chart(keyword_counts)
                            if chart:
                                chart_box.altair_chart(chart, use_container_width=True, key=f"chart_{current_page}")
                        
                        # Force Streamlit to update UI by yielding control
                        # This allows Streamlit to process the updates
                        time.sleep(0.01)  # Small delay to allow UI update
                
                    if ai_keyword_search and ai_service.model:
                        # AI Keyword Search Mode (ALL AI) - Optimized
                        # Strategy: Try direct text extraction first, only use image search if quality is poor
                        import fitz
                        try:
                            if file_path.lower().endswith('.pdf'):
                                doc = fitz.open(file_path)
                                total_pages = len(doc)
                                doc.close()
                                
                                kw_counts = {}
                                total_keywords_found = 0
                                text_length = 0
                                
                                # Step 1: Try direct PDF extraction first (optimized)
                                update_page_progress(0, total_pages, tokens_used, 0, {})
                                logger.info("ALL AI: Attempting optimized direct extraction...")
                                
                                direct_text, direct_tokens, quality_score = ai_service.extract_text_from_pdf_direct(file_path)
                                tokens_used += direct_tokens
                                
                                # Update progress after direct extraction
                                update_page_progress(0, total_pages, tokens_used, 0, {})
                                
                                # Step 2: Assess quality and decide strategy
                                quality_threshold = 50  # Use image search if quality < 50
                                
                                # Check completeness similar to OCR AI mode
                                estimated_min_length = total_pages * 1000
                                is_complete = len(direct_text) >= estimated_min_length * 0.5
                                
                                # Check keyword count with baseline comparison
                                has_sufficient_keywords = True
                                baseline_keyword_count = None
                                
                                if direct_text:
                                    kw_check, _ = analyzer.analyze(direct_text, st.session_state.keywords_map)
                                    kw_count_check = sum(kw_check.values())
                                    
                                    # Get baseline from local extraction for comparison
                                    try:
                                        import fitz
                                        doc_baseline = fitz.open(file_path)
                                        baseline_text = ""
                                        for page in doc_baseline:
                                            baseline_text += page.get_text() + "\n"
                                        doc_baseline.close()
                                        
                                        if baseline_text:
                                            baseline_kw, _ = analyzer.analyze(baseline_text, st.session_state.keywords_map)
                                            baseline_keyword_count = sum(baseline_kw.values())
                                            
                                            # AI models with semantic understanding should extract AT LEAST as many keywords as Local OCR
                                            # If AI has fewer keywords than baseline, it's likely incomplete or not leveraging its full capabilities
                                            # Target: AI should have ≥ 100% of baseline keywords (ideally more due to semantic understanding)
                                            if baseline_keyword_count > 0:
                                                keyword_ratio = kw_count_check / baseline_keyword_count
                                                if keyword_ratio < 1.0:  # AI should have at least 100% of baseline
                                                    has_sufficient_keywords = False
                                                    logger.warning(f"ALL AI: Direct extraction has {kw_count_check} keywords vs baseline {baseline_keyword_count} ({keyword_ratio:.1%}) - AI should extract ≥100% due to semantic understanding. Falling back to Vision API...")
                                                elif keyword_ratio >= 1.0:
                                                    logger.info(f"✅ ALL AI: Direct extraction has {kw_count_check} keywords vs baseline {baseline_keyword_count} ({keyword_ratio:.1%}) - AI leveraging semantic understanding effectively")
                                    except Exception as e:
                                        logger.debug(f"ALL AI: Could not get baseline for comparison: {e}")
                                    
                                    # Fallback check
                                    if has_sufficient_keywords and total_pages > 10 and kw_count_check < 5:
                                        has_sufficient_keywords = False
                                        logger.warning(f"ALL AI: Direct extraction has only {kw_count_check} keywords - likely incomplete")
                                
                                if quality_score >= quality_threshold and len(direct_text) > 100 and is_complete and has_sufficient_keywords:
                                    # Good quality - analyze keywords in extracted text
                                    logger.info(f"ALL AI: Direct extraction quality good ({quality_score}/100). Analyzing keywords in text...")
                                    text_length = len(direct_text)
                                    
                                    # Analyze keywords using standard analyzer (faster than image search)
                                    kw_counts, group_counts = analyzer.analyze(direct_text, st.session_state.keywords_map)
                                    total_keywords_found = sum(kw_counts.values())
                                    
                                    update_page_progress(total_pages, total_pages, tokens_used, total_keywords_found, kw_counts)
                                    logger.info(f"ALL AI: Found {total_keywords_found} keywords via direct extraction")
                                else:
                                    # Poor quality or incomplete - use image-based semantic search
                                    if not is_complete:
                                        logger.info(f"ALL AI: Direct extraction incomplete ({len(direct_text):,} chars). Using image-based semantic search...")
                                    elif not has_sufficient_keywords:
                                        logger.info(f"ALL AI: Direct extraction has insufficient keywords. Using image-based semantic search...")
                                    else:
                                        logger.info(f"ALL AI: Direct extraction quality insufficient ({quality_score}/100). Using image-based semantic search...")
                                    
                                    doc = fitz.open(file_path)
                                    for page_num in range(total_pages):  # Process ALL pages
                                        # Update progress BEFORE processing
                                        update_page_progress(page_num + 1, total_pages, tokens_used, total_keywords_found, kw_counts)
                                    
                                        page = doc[page_num]
                                        pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))
                                        img_bytes = pix.tobytes("png")
                                    
                                        page_kw, page_tokens = ai_service.search_keywords_in_image(
                                            img_bytes, 
                                            list(st.session_state.keywords_map.keys()),
                                            semantic_threshold=semantic_threshold
                                        )
                                        tokens_used += page_tokens
                                    
                                        # Update total keywords found
                                        page_kw_count = sum(page_kw.values())
                                        total_keywords_found += page_kw_count
                                    
                                        for k, v in page_kw.items():
                                            kw_counts[k] = kw_counts.get(k, 0) + v
                                        
                                        # Update progress again with new counts AFTER processing
                                        update_page_progress(page_num + 1, total_pages, tokens_used, total_keywords_found, kw_counts)
                                    doc.close()
                                
                                # Calculate group counts
                                group_counts = {}
                                for kw, count in kw_counts.items():
                                    g = st.session_state.keywords_map.get(kw, 0)
                                    group_counts[g] = group_counts.get(g, 0) + count
                            
                                if text_length == 0:
                                    text_length = len(direct_text) if direct_text else 0
                            else:
                                # For non-PDF, fall back to standard
                                text, tokens_used = extractor.extract_from_file(file_path, st.session_state.keywords_map, force_ai)
                                kw_counts, group_counts = analyzer.analyze(text, st.session_state.keywords_map)
                                text_length = len(text)
                        except Exception as e:
                            logger.error(f"AI Keyword Search failed: {e}")
                            st.warning(f"⚠️ ALL AI failed: {str(e)[:50]}... Falling back to Local OCR.")
                            text, tokens_used = extractor.extract_from_file(
                                file_path, 
                                st.session_state.keywords_map, 
                                False,
                                progress_callback=update_page_progress
                            )
                            kw_counts, group_counts = analyzer.analyze(text, st.session_state.keywords_map)
                            text_length = len(text)
                    else:
                        # Standard or Force AI mode
                        # Use progress callback for BOTH modes (Local OCR & OCR AI)
                        text, tokens_used = extractor.extract_from_file(
                            file_path, 
                            st.session_state.keywords_map, 
                            force_ai, 
                            progress_callback=update_page_progress
                        )
                    
                        kw_counts, group_counts = analyzer.analyze(text, st.session_state.keywords_map)
                        text_length = len(text)
                
                    # Update token counter - ALWAYS log for debugging
                    st.session_state.total_tokens += tokens_used
                    log_message(f"Tokens used: {tokens_used} | Keywords found: {sum(kw_counts.values())}")
                
                    # Aggregate counts
                    for k, v in kw_counts.items():
                        all_kws[k] = all_kws.get(k, 0) + v
                    for g, c in group_counts.items():
                        all_groups[g] = all_groups.get(g, 0) + c
                
                    res = {
                        "filename": uploaded_file.name,
                        "text_length": text_length,
                        "total_keywords": sum(kw_counts.values()),
                        "group_counts": group_counts,
                        "keyword_counts": kw_counts
                    }
                    results.append(res)
                    log_message(f"Found {res['total_keywords']} keywords in {current_file_name}")
                
                    progress_bar.progress((i + 1) / total_files)
            
                # Store results
                st.session_state.processed_files.extend(results)
                st.session_state.all_keyword_counts = all_kws
                st.session_state.all_group_counts = all_groups
            
                # Export
                export_path = os.path.join(OUTPUT_DIR, f"analysis_report_{int(time.time())}.xlsx")
                export_to_excel(results, export_path)
            
                status_box.success("✅ Processing Complete!")
                log_message(f"Batch complete. Report saved.")
            
                # Update state and rerun to re-enable button
                st.session_state.is_processing = False
                st.session_state.run_completed = True
                st.session_state.last_report_path = export_path
                st.session_state.last_run_time = time.time() - start_time
            
                # Determine mode name for summary
                if force_ai:
                    st.session_state.last_run_mode = "OCR AI"
                elif ai_keyword_search:
                    st.session_state.last_run_mode = "ALL AI"
                else:
                    st.session_state.last_run_mode = "Local OCR"
                
                st.rerun()

            elif st.session_state.run_completed:
                st.success("✅ Processing Complete!")
                st.balloons()
            
                # Calculate metrics
                total_kw = sum(r['total_keywords'] for r in st.session_state.processed_files) if st.session_state.processed_files else 0
                total_tokens = st.session_state.total_tokens
                elapsed_time = st.session_state.get('last_run_time', 0)
                mode = st.session_state.get('last_run_mode', 'Unknown')
            
                # Estimate cost (Assumption: ~$0.10 per 1M tokens for Flash models)
                # Input tokens are cheap, output tokens are slightly more. This is a rough estimate.
                estimated_cost = (total_tokens / 1_000_000) * 0.10
            
                # Display Summary Table
                st.markdown(f"""
                | Metric | Value |
                |---|---|
                | **Mode** | {mode} |
                | **Total Keywords** | {total_kw} |
                | **Total Tokens** | {total_tokens:,} |
                | **Estimated Cost** | ${estimated_cost:.6f} |
                | **Total Time** | {elapsed_time:.1f}s |
                """)
            
                if 'last_report_path' in st.session_state:
                    st.success(f"Report saved to: `{st.session_state.last_report_path}`")

            else:
                st.info("Upload documents and click 'Start Processing' to begin.")

        with tab_results:
            if st.session_state.processed_files:
                total_kw = sum(r['total_keywords'] for r in st.session_state.processed_files)
                avg_kw = total_kw / len(st.session_state.processed_files) if st.session_state.processed_files else 0
            
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Files", len(st.session_state.processed_files))
                m2.metric("Total Keywords", total_kw)
                m3.metric("Avg Keywords/File", f"{avg_kw:.1f}")
            
                # File summary table
                st.markdown("#### 📋 File Summary")
                df = pd.DataFrame([
                    {"File": r['filename'], "Keywords": r['total_keywords'], "Length": r['text_length']} 
                    for r in st.session_state.processed_files
                ])
                st.dataframe(df, use_container_width=True)
            
                # Detailed keyword frequency
                all_kws = st.session_state.all_keyword_counts
                all_groups = st.session_state.all_group_counts
            
                if all_kws:
                    st.markdown("---")
                    st.markdown("#### 📊 Chi tiết Tần suất Keywords")
                    
                    # Create tabs for Keywords and Groups
                    kw_detail_tab1, kw_detail_tab2 = st.tabs(["🔑 Keywords", "📁 Groups"])
                    
                    with kw_detail_tab1:
                        # Sort keywords by frequency
                        sorted_kws = sorted(all_kws.items(), key=lambda x: x[1], reverse=True)
                        
                        # Create DataFrame with keyword details
                        kw_df_data = []
                        for keyword, count in sorted_kws:
                            # Get group for this keyword
                            group_id = st.session_state.keywords_map.get(keyword, 0)
                            kw_df_data.append({
                                "Keyword": keyword,
                                "Count": count,
                                "Group": f"Group {group_id}" if group_id > 0 else "Ungrouped"
                            })
                        
                        kw_df = pd.DataFrame(kw_df_data)
                        st.dataframe(kw_df, use_container_width=True, height=400)
                    
                    with kw_detail_tab2:
                        # Group statistics
                        if all_groups:
                            sorted_groups = sorted(all_groups.items(), key=lambda x: x[1], reverse=True)
                            
                            group_df_data = []
                            for group_id, count in sorted_groups:
                                # Count unique keywords in this group
                                group_keywords = [k for k, g in st.session_state.keywords_map.items() if g == group_id]
                                found_keywords = [k for k in all_kws.keys() if st.session_state.keywords_map.get(k, 0) == group_id]
                                
                                group_df_data.append({
                                    "Group": f"Group {group_id}",
                                    "Total Count": count,
                                    "Unique Keywords Found": len(found_keywords),
                                    "Total Keywords in Group": len(group_keywords)
                                })
                            
                            group_df = pd.DataFrame(group_df_data)
                            st.dataframe(group_df, use_container_width=True)
                            
                            # Show group details
                            st.markdown("##### 📈 Group Details")
                            for group_id, count in sorted_groups:
                                with st.expander(f"Group {group_id} - {count} occurrences"):
                                    group_keywords = [(k, all_kws[k]) for k in all_kws.keys() 
                                                     if st.session_state.keywords_map.get(k, 0) == group_id]
                                    group_keywords.sort(key=lambda x: x[1], reverse=True)
                                    
                                    for kw, kw_count in group_keywords:
                                        st.markdown(f"- **{kw}**: {kw_count} lần")
                        else:
                            st.info("No group data available.")
                
                    # Word Cloud
                    st.markdown("---")
                    st.markdown("#### ☁️ Word Cloud")
                    if WORDCLOUD_AVAILABLE:
                        try:
                            wc = WordCloud(width=800, height=400, background_color='white', 
                                           font_path=None, max_words=100).generate_from_frequencies(all_kws)
                            fig, ax = plt.subplots(figsize=(10, 5))
                            ax.imshow(wc, interpolation='bilinear')
                            ax.axis('off')
                            st.pyplot(fig)
                        except Exception as e:
                            st.error(f"Word Cloud error: {e}")
                else:
                    st.warning("No keywords found.")
            else:
                st.caption("No results yet.")

        with tab_insights:
            st.markdown("### 🤖 AI-Generated Insights")
        
            # Debug info
            st.caption(f"📊 Data available: {len(st.session_state.all_keyword_counts)} keywords, {len(st.session_state.processed_files)} files")
        
            if st.button("🔮 Generate AI Insights", type="secondary"):
                ai_service = GeminiService(api_key=user_api_key)

                if not ai_service.model:
                    if not user_api_key:
                        st.error("❌ Gemini API key not configured. Please configure your API key in Settings.")
                    else:
                        st.error("❌ Gemini API initialization failed. Please check your API key.")
                else:
                    with st.spinner("Đang tạo nhận xét..."):
                        # Get data from session state
                        kw_counts = st.session_state.all_keyword_counts
                        grp_counts = st.session_state.all_group_counts
                        files = [r['filename'] for r in st.session_state.processed_files]
                    
                        log_message(f"Generating insights with {len(kw_counts)} keywords...")
                    
                        insights, tokens = ai_service.generate_insights(kw_counts, grp_counts, files)
                    
                        st.session_state.total_tokens += tokens
                        st.session_state.ai_insights = insights
                        log_message(f"Insights generated ({tokens} tokens)")
                    
                        # Force rerun to show results
                        st.rerun()
        
            # Always display insights if available
            if st.session_state.ai_insights:
                st.markdown(st.session_state.ai_insights)
            else:
                st.info("👆 Click 'Generate AI Insights' để AI phân tích kết quả của bạn.")

        with tab_logs:
            for msg in reversed(st.session_state.logs[-50:]):  # Last 50 logs
                st.text(msg)

    # Footer
    st.markdown("---")
    st.caption(f"© 2025 Text-Mining Research Tool v{APP_VERSION} | Built with Streamlit")
