import json
import pandas as pd
import os
from app.config import DEFAULT_KEYWORDS_FILE, OUTPUT_DIR

def load_keywords(file_path=None):
    """
    Load keywords from JSON, CSV, or Excel.
    Returns: {keyword: group_id}, max_group_id
    """
    if not file_path:
        file_path = DEFAULT_KEYWORDS_FILE

    if not os.path.exists(file_path):
        return {}, 0

    ext = os.path.splitext(file_path)[1].lower()
    keywords_map = {}
    max_group = 0

    try:
        if ext == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Handle JSON if needed
                pass 
        elif ext in ['.csv', '.xlsx', '.xls', '.txt', '.md']:
            if ext == '.csv':
                # Try different delimiters
                try:
                    df = pd.read_csv(file_path, encoding='utf-8')
                except:
                    df = pd.read_csv(file_path, encoding='utf-8', sep=';')
            elif ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            elif ext in ['.txt', '.md']:
                # Parse text/markdown files
                # Expected format: Group ID | Keywords (comma separated)
                # OR just list of keywords (Group 0)
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                data = []
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('#'): continue
                    
                    parts = line.split('|')
                    if len(parts) >= 2:
                        data.append({'Group': parts[0].strip(), 'Keywords': parts[1].strip()})
                    else:
                        data.append({'Group': 0, 'Keywords': line})
                df = pd.DataFrame(data)

            # Process DataFrame
            # Assume col 0 is Group, col 1 is Keyword (as per fin_v3.txt logic)
            # Or if columns are named 'Group' and 'Keywords'
            
            group_col_idx = 0
            kw_col_idx = 1
            
            # Check if headers match
            if 'Group' in df.columns:
                group_col_idx = df.columns.get_loc('Group')
            if 'Keywords' in df.columns:
                kw_col_idx = df.columns.get_loc('Keywords')
            elif 'Keyword' in df.columns:
                kw_col_idx = df.columns.get_loc('Keyword')

            for _, row in df.iterrows():
                try:
                    # Handle Group
                    raw_group = row.iloc[group_col_idx]
                    if pd.isna(raw_group):
                        group = 0
                    else:
                        # Extract number from string if needed
                        import re
                        match = re.search(r'\d+', str(raw_group))
                        group = int(match.group()) if match else 0

                    # Handle Keywords
                    raw_kw = row.iloc[kw_col_idx]
                    if pd.isna(raw_kw): continue
                    
                    keywords_str = str(raw_kw)
                    if keywords_str.lower() in ['nan', 'none', '']: continue
                    
                    # Split by comma
                    keywords_list = [k.strip() for k in keywords_str.split(',') if k.strip()]
                    
                    for kw in keywords_list:
                        keywords_map[kw] = group
                        max_group = max(max_group, group)
                except Exception as e:
                    print(f"Skipping row: {e}")
                    continue
    except Exception as e:
        print(f"Error loading keywords: {e}")

    return keywords_map, max_group

def save_keywords(keywords_map, file_path=DEFAULT_KEYWORDS_FILE):
    pass

def export_to_excel(results, output_path):
    """
    Export analysis results to Excel with 3 sheets:
    1. Keyword: Detailed keyword counts
    2. Group: Group totals per file
    3. Standardized: Group totals normalized (0-100)
    """
    if not results:
        return

    keyword_rows = []
    group_rows = []
    standardized_rows = []

    all_groups = set()
    for res in results:
        all_groups.update(res.get("group_counts", {}).keys())
    sorted_groups = sorted(list(all_groups))

    for res in results:
        filename = res["filename"]
        
        # 1. Keyword Sheet
        if res["keyword_counts"]:
            for kw, count in res["keyword_counts"].items():
                keyword_rows.append({
                    "File Name": filename,
                    "Keyword": kw,
                    "Count": count,
                    "Group": "Unknown" 
                })
        else:
             keyword_rows.append({
                "File Name": filename,
                "Keyword": "No keywords found",
                "Count": 0,
                "Group": "-"
            })

        # 2. Group Sheet
        group_row = {
            "File Name": filename,
            "Total Keywords": res["total_keywords"],
            "Text Length": res["text_length"]
        }
        for g in sorted_groups:
            group_row[f"Group_{g}"] = res["group_counts"].get(g, 0)
        group_rows.append(group_row)

        # 3. Standardized Sheet
        # Normalize group counts (0-100 relative to max in that file)
        std_row = {
            "File Name": filename
        }
        
        # Calculate max count for this file to normalize against
        # If max is 0, all scores are 0
        current_file_counts = res["group_counts"]
        max_val = max(current_file_counts.values()) if current_file_counts else 0
        
        for g in sorted_groups:
            val = current_file_counts.get(g, 0)
            if max_val > 0:
                # Standard academic normalization: (value / max) * 100
                std_score = round((val / max_val) * 100, 2)
            else:
                std_score = 0
            std_row[f"Group_{g}"] = std_score
            
        standardized_rows.append(std_row)

    df_keyword = pd.DataFrame(keyword_rows)
    df_group = pd.DataFrame(group_rows)
    df_std = pd.DataFrame(standardized_rows)

    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df_keyword.to_excel(writer, sheet_name='Keyword', index=False)
            df_group.to_excel(writer, sheet_name='Group', index=False)
            df_std.to_excel(writer, sheet_name='Standardized', index=False)
        print(f"Exported to {output_path}")
    except Exception as e:
        print(f"Export failed: {e}")
