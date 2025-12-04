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
from app.i18n.translator import Translator
from ui.components.api_key_input import render_api_key_input
from ui.components.cloud_storage import render_cloud_storage_settings, render_file_source_selector
from ui.components.theme_selector import render_compact_theme_selector
from ui.components.language_selector import render_compact_language_selector

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

    # Initialize settings manager
    settings_manager = SettingsManager(firebase_manager.get_firestore_client())

    # Initialize language
    user_language = settings_manager.get_language_preference(user_id) if user_id else 'en'
    if 'language' not in st.session_state:
        st.session_state['language'] = user_language

    # Initialize translator
    translator = Translator(st.session_state.get('language', 'en'))

    # Initialize theme manager and apply theme
    theme_manager = ThemeManager(settings_manager, user_id)
    theme_manager.apply_theme()

    # Get user's API key
    user_api_key = settings_manager.get_api_key(user_id) if user_id else None

    # Create 2 columns
    left_col, right_col = st.columns([1, 2], gap="large")

    with left_col:
        st.markdown(f"### ⚙️ {translator.t('settings.configuration_input')}")

        # --- Settings Section ---
        with st.expander(f"⚙️ {translator.t('settings.title')}", expanded=not user_api_key):
            # API Key Configuration
            has_api_key = render_api_key_input(
                settings_manager,
                user_id,
                language=st.session_state.get('language', 'en')
            )

            # Warning if no API key
            if not has_api_key:
                st.warning(f"⚠️ {translator.t('settings.api_key_warning')}")

            st.markdown("---")

            # Language Configuration
            render_compact_language_selector(
                settings_manager,
                user_id,
                translator
            )

            st.markdown("---")

            # Theme Configuration
            render_compact_theme_selector(
                theme_manager,
                language=st.session_state.get('language', 'en')
            )

            st.markdown("---")

            # Cloud Storage Configuration
            render_cloud_storage_settings(
                settings_manager,
                user_id,
                language=st.session_state.get('language', 'en')
            )

        # --- Keyword Section ---
        with st.expander(f"🔑 {translator.t('keywords.title')}", expanded=True):
            st.info(f"{translator.t('keywords.loaded')}: **{len(st.session_state.keywords_map)}** {translator.t('keywords.keywords_count')}")

            kw_tab1, kw_tab2 = st.tabs([f"📤 {translator.t('keywords.upload_tab')}", f"✍️ {translator.t('keywords.manual_tab')}"])
        
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

        # --- File Upload Section ---
        st.markdown("### 📁 Document Input")
        uploaded_files = st.file_uploader("Upload Documents", 
                                        type=['pdf', 'docx', 'txt', 'png', 'jpg', 'html'], 
                                        accept_multiple_files=True)

        # --- AI Options ---
        st.markdown("### 🤖 Extraction Mode")
    
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
                
                    # Save file
                    file_path = os.path.join(INPUT_DIR, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                    tokens_used = 0
                    current_page_info = {"page": 0, "total": 0}
                
                    # Define progress callback for AI extraction
                    def update_page_progress(current_page, total_pages, tokens_so_far, keywords_so_far=0, keyword_counts=None):
                        current_page_info["page"] = current_page
                        current_page_info["total"] = total_pages
                        elapsed = time.time() - start_time
                    
                        status_box.markdown(f"""
                        **Processing:** `{current_file_name}`
                    
                        | Metric | Value |
                        |---|---|
                        | **Progress** | {i+1}/{total_files} |
                        | **Mode** | {tech_used} |
                        | **Page** | {current_page}/{total_pages} |
                        | **Keywords** | {keywords_so_far} |
                        | **Tokens** | {tokens_so_far:,} |
                        | **Time** | {elapsed:.1f}s |
                        """)
                    
                        # Update Bubble Chart
                        if keyword_counts:
                            chart = create_bubble_chart(keyword_counts)
                            if chart:
                                chart_box.altair_chart(chart, use_container_width=True)
                
                    if ai_keyword_search and ai_service.model:
                        # AI Keyword Search Mode (ALL AI)
                        # Convert PDF to image and search directly
                        import fitz
                        try:
                            if file_path.lower().endswith('.pdf'):
                                doc = fitz.open(file_path)
                                total_pages = len(doc)
                                kw_counts = {}
                                total_keywords_found = 0
                            
                                for page_num in range(total_pages):  # Process ALL pages
                                    # Update progress
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
                                    
                                    # Update progress again with new counts
                                    update_page_progress(page_num + 1, total_pages, tokens_used, total_keywords_found, kw_counts)
                                doc.close()
                            
                                # Calculate group counts
                                group_counts = {}
                                for kw, count in kw_counts.items():
                                    g = st.session_state.keywords_map.get(kw, 0)
                                    group_counts[g] = group_counts.get(g, 0) + count
                            
                                text_length = 0  # Not applicable for direct search
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
            
                df = pd.DataFrame([
                    {"File": r['filename'], "Keywords": r['total_keywords'], "Length": r['text_length']} 
                    for r in st.session_state.processed_files
                ])
                st.dataframe(df, use_container_width=True)
            
                # Word Cloud (removed Keyword Distribution bar chart)
                all_kws = st.session_state.all_keyword_counts
            
                if all_kws:
                
                    if WORDCLOUD_AVAILABLE:
                        st.markdown("#### ☁️ Word Cloud")
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
