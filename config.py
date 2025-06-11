#!/usr/bin/env python3
"""
Configuration file for SuperWhisper Analysis
Customize these settings for your environment
"""

import os
from pathlib import Path

# ==============================================================================
# PATH CONFIGURATION
# ==============================================================================

# Default SuperWhisper recordings path (update this to match your setup)
# Common locations:
# macOS: "~/Documents/superwhisper/recordings"
# Alternative: "~/Library/Application Support/SuperWhisper/recordings"
RECORDINGS_PATH = "~/Documents/superwhisper/recordings"

# Cache and output directories (relative to project root)
CACHE_DIR = "./cache_meta_files"
OUTPUT_DIR = "./output"

# Cache file names
RECORDINGS_CACHE_FILE = "recordings_cache.pkl"

# ==============================================================================
# ANALYSIS PARAMETERS
# ==============================================================================

# Parallel processing settings
MAX_WORKERS = 8  # Number of parallel processes (adjust based on your CPU)

# Text analysis parameters
AVERAGE_WORD_LENGTH = 5  # Characters per word (including spaces)

# Typing speed benchmarks (Words Per Minute)
TYPING_SPEEDS = {
    'casual': 35,       # Casual/hunt-and-peck typing
    'professional': 60, # Professional/touch typing
    'fast': 80         # Fast/expert typing
}

# ==============================================================================
# VISUALIZATION SETTINGS
# ==============================================================================

# Chart settings
FIGURE_SIZE = (20, 24)  # Width, height in inches
DPI = 300              # Resolution for saved images
STYLE = 'default'      # Matplotlib style

# Color palette
COLORS = {
    'primary': 'steelblue',
    'secondary': 'lightcoral',
    'accent': 'green',
    'warning': 'orange',
    'info': 'purple',
    'success': 'teal'
}

# ==============================================================================
# OUTPUT FILE NAMES
# ==============================================================================

OUTPUT_FILES = {
    # Visualizations (keep in main directory - these are the beautiful charts!)
    'main_analysis_chart': 'superwhisper_analysis_fast.png',
    'text_analysis_chart': 'superwhisper_text_analysis.png',
    
    # CSV data files (organized in data subdirectory)
    'detailed_data': 'data/recordings_detailed_fast.csv',
    'daily_stats': 'data/daily_stats_fast.csv',
    'weekly_stats': 'data/weekly_stats_fast.csv',
    'monthly_stats': 'data/monthly_stats_fast.csv',
    'text_analysis_data': 'data/recordings_text_analysis.csv'
}

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def get_recordings_path():
    """Get the configured recordings path, expanding user home if needed"""
    return Path(os.path.expanduser(RECORDINGS_PATH))

def ensure_output_dir():
    """Create output directory if it doesn't exist"""
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    return OUTPUT_DIR

def ensure_data_dir():
    """Create data directory for CSV files if it doesn't exist"""
    Path("data").mkdir(exist_ok=True)
    return "data"

def get_cache_dir():
    """Get cache directory path"""
    Path(CACHE_DIR).mkdir(exist_ok=True)
    return CACHE_DIR

def validate_config():
    """Validate configuration settings"""
    recordings_path = get_recordings_path()
    
    if not recordings_path.exists():
        print(f"⚠️  WARNING: Recordings path does not exist: {recordings_path}")
        print("Please update RECORDINGS_PATH in config.py to match your SuperWhisper recordings location")
        return False
    
    if not recordings_path.is_dir():
        print(f"⚠️  WARNING: Recordings path is not a directory: {recordings_path}")
        return False
    
    print(f"✅ Configuration validated. Recordings path: {recordings_path}")
    return True

# ==============================================================================
# ENVIRONMENT DETECTION
# ==============================================================================

def detect_superwhisper_path():
    """Attempt to auto-detect SuperWhisper recordings path"""
    possible_paths = [
        "~/Documents/superwhisper/recordings",
        "~/Library/Application Support/SuperWhisper/recordings",
        "~/SuperWhisper/recordings"
    ]
    
    for path in possible_paths:
        expanded_path = Path(path.replace('~', os.path.expanduser('~')))
        if expanded_path.exists() and expanded_path.is_dir():
            return str(expanded_path)
    
    return None

if __name__ == "__main__":
    print("SuperWhisper Analysis Configuration")
    print("=" * 50)
    print(f"Recordings Path: {get_recordings_path()}")
    print(f"Cache Directory: {get_cache_dir()}")
    print(f"Output Directory: {ensure_output_dir()}")
    print(f"Max Workers: {MAX_WORKERS}")
    print()
    
    # Try to detect SuperWhisper path if current config doesn't work
    if not validate_config():
        detected_path = detect_superwhisper_path()
        if detected_path:
            print(f"💡 Auto-detected possible path: {detected_path}")
            print("Consider updating RECORDINGS_PATH in config.py")
        else:
            print("❌ Could not auto-detect SuperWhisper recordings path")
            print("Please manually set RECORDINGS_PATH in config.py") 