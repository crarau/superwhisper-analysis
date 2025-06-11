#!/usr/bin/env python3
"""
SuperWhisper Recording Analysis - Optimized Version
Handles iCloud sync issues and processes files much faster
"""

import json
import os
import shutil
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import numpy as np
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import time
from tqdm import tqdm
import pickle

# Import configuration
import config

def create_local_cache(recordings_path, cache_dir="./cache_meta_files"):
    """Copy all meta.json files to a local cache directory for faster access"""
    print(f"Creating local cache at {cache_dir}...")
    
    # Create cache directory
    os.makedirs(cache_dir, exist_ok=True)
    
    # Find all meta.json files
    meta_files = []
    
    print("Scanning for recording folders...")
    folders = [f for f in os.listdir(recordings_path) 
               if os.path.isdir(os.path.join(recordings_path, f)) and not f.startswith('.')]
    
    print(f"Found {len(folders)} recording folders")
    
    # Copy meta.json files with progress bar
    cached_files = []
    with tqdm(total=len(folders), desc="Caching meta.json files") as pbar:
        for folder_name in folders:
            folder_path = os.path.join(recordings_path, folder_name)
            meta_file = os.path.join(folder_path, 'meta.json')
            
            if os.path.exists(meta_file):
                # Copy to cache with folder name as filename
                cache_file = os.path.join(cache_dir, f"{folder_name}.json")
                
                try:
                    # Only copy if not already cached or source is newer
                    if not os.path.exists(cache_file) or \
                       os.path.getmtime(meta_file) > os.path.getmtime(cache_file):
                        shutil.copy2(meta_file, cache_file)
                    
                    cached_files.append((folder_name, cache_file))
                except Exception as e:
                    print(f"Error caching {meta_file}: {e}")
            
            pbar.update(1)
    
    print(f"Cached {len(cached_files)} meta.json files")
    return cached_files

def process_single_file(args):
    """Process a single meta.json file - designed for parallel processing"""
    folder_name, file_path = args
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract relevant data
        recording = {
            'folder': folder_name,
            'datetime': datetime.fromisoformat(data['datetime'].replace('Z', '+00:00')),
            'duration_ms': data['duration'],
            'duration_minutes': data['duration'] / 1000 / 60,
            'model_name': data.get('modelName', 'Unknown'),
            'app_version': data.get('appVersion', 'Unknown'),
            'processing_time': data.get('processingTime', 0),
            'result_length': len(data.get('result', ''))
        }
        return recording
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def load_recording_data_parallel(cached_files, max_workers=None):
    """Load recording data using parallel processing"""
    print(f"Processing {len(cached_files)} files in parallel...")
    
    recordings = []
    
    # Use ThreadPoolExecutor for I/O bound tasks
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_file = {executor.submit(process_single_file, file_args): file_args 
                         for file_args in cached_files}
        
        # Process completed tasks with progress bar
        with tqdm(total=len(cached_files), desc="Processing recordings") as pbar:
            for future in as_completed(future_to_file):
                result = future.result()
                if result:
                    recordings.append(result)
                pbar.update(1)
    
    print(f"Successfully processed {len(recordings)} recordings")
    return recordings

def save_cache_data(recordings, cache_file="recordings_cache.pkl"):
    """Save processed recordings to a pickle file for faster future loading"""
    with open(cache_file, 'wb') as f:
        pickle.dump(recordings, f)
    print(f"Saved processed data to {cache_file}")

def load_cache_data(cache_file="recordings_cache.pkl"):
    """Load processed recordings from cache file"""
    try:
        with open(cache_file, 'rb') as f:
            recordings = pickle.load(f)
        print(f"Loaded {len(recordings)} recordings from cache")
        return recordings
    except FileNotFoundError:
        return None

def create_analysis_dataframe(recordings):
    """Convert recordings to pandas DataFrame and add derived columns"""
    df = pd.DataFrame(recordings)
    
    if df.empty:
        return df
    
    # Add derived columns
    df['date'] = df['datetime'].dt.date
    df['hour'] = df['datetime'].dt.hour
    df['day_of_week'] = df['datetime'].dt.day_name()
    df['week'] = df['datetime'].dt.isocalendar().week
    df['month'] = df['datetime'].dt.month
    df['year_month'] = df['datetime'].dt.strftime('%Y-%m')
    df['year_week'] = df['datetime'].dt.strftime('%Y-W%U')
    
    # Sort by datetime
    df = df.sort_values('datetime')
    
    return df

def generate_daily_stats(df):
    """Generate daily statistics"""
    daily_stats = df.groupby('date').agg({
        'duration_minutes': ['sum', 'count', 'mean'],
        'folder': 'count'
    }).round(2)
    
    daily_stats.columns = ['total_minutes', 'num_recordings', 'avg_duration', 'recordings_count']
    daily_stats['total_hours'] = (daily_stats['total_minutes'] / 60).round(2)
    
    return daily_stats

def generate_weekly_stats(df):
    """Generate weekly statistics"""
    weekly_stats = df.groupby('year_week').agg({
        'duration_minutes': ['sum', 'count', 'mean'],
        'datetime': 'first'
    }).round(2)
    
    weekly_stats.columns = ['total_minutes', 'num_recordings', 'avg_duration', 'week_start']
    weekly_stats['total_hours'] = (weekly_stats['total_minutes'] / 60).round(2)
    
    return weekly_stats

def generate_monthly_stats(df):
    """Generate monthly statistics"""
    monthly_stats = df.groupby('year_month').agg({
        'duration_minutes': ['sum', 'count', 'mean'],
        'datetime': 'first'
    }).round(2)
    
    monthly_stats.columns = ['total_minutes', 'num_recordings', 'avg_duration', 'month_start']
    monthly_stats['total_hours'] = (monthly_stats['total_minutes'] / 60).round(2)
    
    return monthly_stats

def create_visualizations(df, daily_stats, weekly_stats, monthly_stats):
    """Create comprehensive visualizations"""
    # Set up the plotting style
    plt.style.use(config.STYLE)
    fig = plt.figure(figsize=config.FIGURE_SIZE)
    
    # 1. Daily Recording Duration
    plt.subplot(4, 2, 1)
    daily_stats['total_minutes'].plot(kind='line', marker='o', color=config.COLORS['primary'])
    plt.title('Daily Recording Duration (Minutes)', fontsize=14, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Minutes')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # 2. Daily Number of Recordings
    plt.subplot(4, 2, 2)
    daily_stats['num_recordings'].plot(kind='bar', color=config.COLORS['secondary'], alpha=0.7)
    plt.title('Daily Number of Recordings', fontsize=14, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Number of Recordings')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # 3. Weekly Trends
    plt.subplot(4, 2, 3)
    weekly_stats['total_hours'].plot(kind='line', marker='s', color=config.COLORS['accent'], linewidth=2)
    plt.title('Weekly Recording Hours', fontsize=14, fontweight='bold')
    plt.xlabel('Week')
    plt.ylabel('Hours')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # 4. Monthly Trends
    plt.subplot(4, 2, 4)
    monthly_stats['total_hours'].plot(kind='bar', color=config.COLORS['warning'], alpha=0.8)
    plt.title('Monthly Recording Hours', fontsize=14, fontweight='bold')
    plt.xlabel('Month')
    plt.ylabel('Hours')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # 5. Recording Distribution by Hour of Day
    plt.subplot(4, 2, 5)
    hourly_dist = df.groupby('hour')['duration_minutes'].sum()
    hourly_dist.plot(kind='bar', color='purple', alpha=0.7)
    plt.title('Recording Distribution by Hour of Day', fontsize=14, fontweight='bold')
    plt.xlabel('Hour of Day')
    plt.ylabel('Total Minutes')
    plt.grid(True, alpha=0.3)
    
    # 6. Recording Distribution by Day of Week
    plt.subplot(4, 2, 6)
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_dist = df.groupby('day_of_week')['duration_minutes'].sum().reindex(day_order)
    daily_dist.plot(kind='bar', color='teal', alpha=0.7)
    plt.title('Recording Distribution by Day of Week', fontsize=14, fontweight='bold')
    plt.xlabel('Day of Week')
    plt.ylabel('Total Minutes')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # 7. Duration Distribution Histogram
    plt.subplot(4, 2, 7)
    plt.hist(df['duration_minutes'], bins=30, color='gold', alpha=0.7, edgecolor='black')
    plt.title('Recording Duration Distribution', fontsize=14, fontweight='bold')
    plt.xlabel('Duration (Minutes)')
    plt.ylabel('Frequency')
    plt.grid(True, alpha=0.3)
    
    # 8. Cumulative Recording Time
    plt.subplot(4, 2, 8)
    df_sorted = df.sort_values('datetime')
    cumulative_minutes = df_sorted['duration_minutes'].cumsum()
    plt.plot(df_sorted['datetime'], cumulative_minutes, color='red', linewidth=2)
    plt.title('Cumulative Recording Time', fontsize=14, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Minutes')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(config.OUTPUT_FILES['main_analysis_chart'], dpi=config.DPI, bbox_inches='tight')
    print(f"Visualization saved as '{config.OUTPUT_FILES['main_analysis_chart']}'")

def print_summary_statistics(df, daily_stats, weekly_stats, monthly_stats):
    """Print comprehensive summary statistics"""
    print("=" * 80)
    print("SUPERWHISPER RECORDING ANALYSIS SUMMARY (FAST VERSION)")
    print("=" * 80)
    
    # Overall Statistics
    total_recordings = len(df)
    total_minutes = df['duration_minutes'].sum()
    total_hours = total_minutes / 60
    avg_duration = df['duration_minutes'].mean()
    
    print(f"\n📊 OVERALL STATISTICS")
    print(f"{'Total Recordings:':<25} {total_recordings:,}")
    print(f"{'Total Recording Time:':<25} {total_minutes:,.1f} minutes ({total_hours:.1f} hours)")
    print(f"{'Average Duration:':<25} {avg_duration:.1f} minutes")
    print(f"{'Date Range:':<25} {df['datetime'].min().date()} to {df['datetime'].max().date()}")
    
    # Daily Statistics
    print(f"\n📅 DAILY STATISTICS")
    print(f"{'Active Days:':<25} {len(daily_stats)}")
    print(f"{'Avg Recordings/Day:':<25} {daily_stats['num_recordings'].mean():.1f}")
    print(f"{'Avg Minutes/Day:':<25} {daily_stats['total_minutes'].mean():.1f}")
    print(f"{'Max Minutes/Day:':<25} {daily_stats['total_minutes'].max():.1f}")
    print(f"{'Most Active Day:':<25} {daily_stats['total_minutes'].idxmax()} ({daily_stats['total_minutes'].max():.1f} min)")
    
    # Weekly Statistics
    print(f"\n📆 WEEKLY STATISTICS")
    print(f"{'Active Weeks:':<25} {len(weekly_stats)}")
    print(f"{'Avg Hours/Week:':<25} {weekly_stats['total_hours'].mean():.1f}")
    print(f"{'Max Hours/Week:':<25} {weekly_stats['total_hours'].max():.1f}")
    
    # Monthly Statistics
    print(f"\n🗓️ MONTHLY STATISTICS")
    print(f"{'Active Months:':<25} {len(monthly_stats)}")
    print(f"{'Avg Hours/Month:':<25} {monthly_stats['total_hours'].mean():.1f}")
    print(f"{'Max Hours/Month:':<25} {monthly_stats['total_hours'].max():.1f}")
    
    # Top Recording Days
    print(f"\n🏆 TOP 10 RECORDING DAYS")
    top_days = daily_stats.nlargest(10, 'total_minutes')
    for i, (date, row) in enumerate(top_days.iterrows(), 1):
        print(f"{i:2d}. {date}: {row['total_minutes']:.1f} min ({row['num_recordings']} recordings)")
    
    # Recording Patterns
    print(f"\n⏰ RECORDING PATTERNS")
    busiest_hour = df.groupby('hour')['duration_minutes'].sum().idxmax()
    busiest_day = df.groupby('day_of_week')['duration_minutes'].sum().idxmax()
    print(f"{'Busiest Hour:':<25} {busiest_hour}:00")
    print(f"{'Busiest Day:':<25} {busiest_day}")
    
    # Recent Activity (Last 30 days)
    recent_cutoff = df['datetime'].max() - timedelta(days=30)
    recent_df = df[df['datetime'] >= recent_cutoff]
    
    if not recent_df.empty:
        print(f"\n📈 RECENT ACTIVITY (Last 30 Days)")
        print(f"{'Recordings:':<25} {len(recent_df)}")
        print(f"{'Total Minutes:':<25} {recent_df['duration_minutes'].sum():.1f}")
        print(f"{'Daily Average:':<25} {recent_df['duration_minutes'].sum() / min(30, len(recent_df.groupby('date'))):.1f} min/day")

def main():
    """Main analysis function - optimized version"""
    # Validate configuration
    if not config.validate_config():
        return
    
    recordings_path = str(config.get_recordings_path())
    cache_file = config.RECORDINGS_CACHE_FILE
    
    start_time = time.time()
    
    print("🚀 SuperWhisper Recording Analysis - FAST VERSION")
    print("=" * 60)
    
    # Try to load from cache first
    recordings = load_cache_data(cache_file)
    
    if recordings is None:
        print("No cache found. Processing files...")
        
        # Step 1: Create local cache of meta.json files
        cached_files = create_local_cache(recordings_path, config.get_cache_dir())
        
        if not cached_files:
            print("No recording data found!")
            return
        
        # Step 2: Process files in parallel
        recordings = load_recording_data_parallel(cached_files, max_workers=config.MAX_WORKERS)
        
        # Step 3: Save to cache for next time
        save_cache_data(recordings, cache_file)
    
    if not recordings:
        print("No valid recordings found!")
        return
    
    print(f"\n✅ Data loaded successfully!")
    print(f"📊 Processing {len(recordings)} recordings...")
    
    # Create DataFrame and generate statistics
    df = create_analysis_dataframe(recordings)
    daily_stats = generate_daily_stats(df)
    weekly_stats = generate_weekly_stats(df) 
    monthly_stats = generate_monthly_stats(df)
    
    # Print comprehensive summary
    print_summary_statistics(df, daily_stats, weekly_stats, monthly_stats)
    
    # Create visualizations
    print("\n📈 Generating visualizations...")
    create_visualizations(df, daily_stats, weekly_stats, monthly_stats)
    
    # Save detailed data to CSV
    print("\n💾 Saving detailed data...")
    config.ensure_data_dir()  # Create data directory for CSV files
    df.to_csv(config.OUTPUT_FILES['detailed_data'], index=False)
    daily_stats.to_csv(config.OUTPUT_FILES['daily_stats'])
    weekly_stats.to_csv(config.OUTPUT_FILES['weekly_stats'])
    monthly_stats.to_csv(config.OUTPUT_FILES['monthly_stats'])
    
    # Performance summary
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"\n⚡ PERFORMANCE SUMMARY")
    print(f"{'Total Processing Time:':<25} {processing_time:.1f} seconds")
    print(f"{'Recordings/Second:':<25} {len(recordings)/processing_time:.1f}")
    
    print("\n✅ Analysis complete!")
    print("Files saved:")
    print(f"- {config.OUTPUT_FILES['main_analysis_chart']} (visualizations)")
    print(f"- {config.OUTPUT_FILES['detailed_data']} (raw data)")
    print(f"- {config.OUTPUT_FILES['daily_stats']} (daily statistics)")
    print(f"- {config.OUTPUT_FILES['weekly_stats']} (weekly statistics)")
    print(f"- {config.OUTPUT_FILES['monthly_stats']} (monthly statistics)")
    print(f"- {cache_file} (processed data cache)")

if __name__ == "__main__":
    main() 