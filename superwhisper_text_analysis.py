#!/usr/bin/env python3
"""
SuperWhisper Text Analysis - Enhanced Version
Analyzes text content, word counts, and time savings from speaking vs typing
"""

import json
import os
import pickle
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time

# Import configuration
import config

def load_cache_data(cache_file=None):
    """Load processed recordings from cache file"""
    if cache_file is None:
        cache_file = config.RECORDINGS_CACHE_FILE
    
    try:
        with open(cache_file, 'rb') as f:
            recordings = pickle.load(f)
        print(f"Loaded {len(recordings)} recordings from cache")
        return recordings
    except FileNotFoundError:
        print("Cache file not found! Please run superwhisper_analysis_fast.py first.")
        return None

def enhance_data_with_text_analysis(recordings):
    """Add text analysis fields to the recordings data"""
    print("Enhancing data with text analysis...")
    
    for recording in recordings:
        chars = recording['result_length']
        
        # Estimate word count (average word length from config)
        estimated_words = max(1, chars // config.AVERAGE_WORD_LENGTH) if chars > 0 else 0
        
        # Calculate typing time estimates using configured speeds
        typing_time_casual = estimated_words / config.TYPING_SPEEDS['casual'] * 60  # seconds
        typing_time_professional = estimated_words / config.TYPING_SPEEDS['professional'] * 60  # seconds
        typing_time_fast = estimated_words / config.TYPING_SPEEDS['fast'] * 60  # seconds
        
        # Recording duration in seconds
        recording_duration_seconds = recording['duration_ms'] / 1000
        
        # Time savings calculations
        time_saved_vs_casual = max(0, typing_time_casual - recording_duration_seconds)
        time_saved_vs_professional = max(0, typing_time_professional - recording_duration_seconds)
        time_saved_vs_fast = max(0, typing_time_fast - recording_duration_seconds)
        
        # Words per minute while speaking
        speaking_wpm = (estimated_words / (recording_duration_seconds / 60)) if recording_duration_seconds > 0 else 0
        
        # Add new fields
        recording.update({
            'characters': chars,
            'estimated_words': estimated_words,
            'typing_time_casual_sec': typing_time_casual,
            'typing_time_professional_sec': typing_time_professional,  
            'typing_time_fast_sec': typing_time_fast,
            'time_saved_vs_casual_sec': time_saved_vs_casual,
            'time_saved_vs_professional_sec': time_saved_vs_professional,
            'time_saved_vs_fast_sec': time_saved_vs_fast,
            'speaking_wpm': speaking_wpm,
            'efficiency_vs_casual': (time_saved_vs_casual / typing_time_casual * 100) if typing_time_casual > 0 else 0,
            'efficiency_vs_professional': (time_saved_vs_professional / typing_time_professional * 100) if typing_time_professional > 0 else 0,
            'efficiency_vs_fast': (time_saved_vs_fast / typing_time_fast * 100) if typing_time_fast > 0 else 0
        })
    
    return recordings

def create_text_analysis_dataframe(recordings):
    """Convert enhanced recordings to pandas DataFrame"""
    df = pd.DataFrame(recordings)
    
    if df.empty:
        return df
    
    # Add derived columns for time analysis
    df['date'] = df['datetime'].dt.date
    df['hour'] = df['datetime'].dt.hour
    df['day_of_week'] = df['datetime'].dt.day_name()
    df['year_month'] = df['datetime'].dt.strftime('%Y-%m')
    df['year_week'] = df['datetime'].dt.strftime('%Y-W%U')
    
    # Convert time savings to minutes for readability
    df['time_saved_vs_casual_min'] = df['time_saved_vs_casual_sec'] / 60
    df['time_saved_vs_professional_min'] = df['time_saved_vs_professional_sec'] / 60
    df['time_saved_vs_fast_min'] = df['time_saved_vs_fast_sec'] / 60
    
    # Sort by datetime
    df = df.sort_values('datetime')
    
    return df

def print_text_analysis_summary(df):
    """Print comprehensive text analysis summary"""
    print("=" * 80)
    print("SUPERWHISPER TEXT ANALYSIS & TIME SAVINGS SUMMARY")
    print("=" * 80)
    
    # Filter out empty recordings for more accurate analysis
    df_with_text = df[df['characters'] > 0]
    
    # Overall Text Statistics
    total_chars = df['characters'].sum()
    total_words = df['estimated_words'].sum()
    total_recording_time_hours = df['duration_minutes'].sum() / 60
    avg_speaking_wpm = df_with_text['speaking_wpm'].mean()
    
    print(f"\n📝 TEXT CONTENT STATISTICS")
    print(f"{'Total Characters:':<30} {total_chars:,}")
    print(f"{'Total Estimated Words:':<30} {total_words:,}")
    print(f"{'Average Speaking Speed:':<30} {avg_speaking_wpm:.1f} WPM")
    print(f"{'Characters per Recording:':<30} {total_chars/len(df):.1f}")
    print(f"{'Words per Recording:':<30} {total_words/len(df):.1f}")
    
    # Time Savings Analysis
    total_time_saved_casual = df['time_saved_vs_casual_min'].sum()
    total_time_saved_professional = df['time_saved_vs_professional_min'].sum()
    total_time_saved_fast = df['time_saved_vs_fast_min'].sum()
    
    print(f"\n⏱️ TIME SAVINGS ANALYSIS")
    print(f"{'Recording Time:':<30} {total_recording_time_hours:.1f} hours")
    print(f"")
    print(f"TIME SAVED vs DIFFERENT TYPING SPEEDS:")
    print(f"{'vs Casual Typing (' + str(config.TYPING_SPEEDS['casual']) + ' WPM):':<30} {total_time_saved_casual/60:.1f} hours ({total_time_saved_casual:.0f} min)")
    print(f"{'vs Professional (' + str(config.TYPING_SPEEDS['professional']) + ' WPM):':<30} {total_time_saved_professional/60:.1f} hours ({total_time_saved_professional:.0f} min)")
    print(f"{'vs Fast Typing (' + str(config.TYPING_SPEEDS['fast']) + ' WPM):':<30} {total_time_saved_fast/60:.1f} hours ({total_time_saved_fast:.0f} min)")
    
    # Efficiency Analysis
    avg_efficiency_casual = df_with_text['efficiency_vs_casual'].mean()
    avg_efficiency_professional = df_with_text['efficiency_vs_professional'].mean()
    avg_efficiency_fast = df_with_text['efficiency_vs_fast'].mean()
    
    print(f"\n🚀 EFFICIENCY ANALYSIS")
    print(f"{'Average Efficiency vs Casual:':<30} {avg_efficiency_casual:.1f}% time saved")
    print(f"{'Average Efficiency vs Professional:':<30} {avg_efficiency_professional:.1f}% time saved")
    print(f"{'Average Efficiency vs Fast:':<30} {avg_efficiency_fast:.1f}% time saved")
    
    # Daily productivity impact
    days_active = len(df.groupby('date'))
    daily_time_saved_casual = total_time_saved_casual / days_active
    daily_time_saved_professional = total_time_saved_professional / days_active
    
    print(f"\n📊 DAILY PRODUCTIVITY IMPACT")
    print(f"{'Active Days:':<30} {days_active}")
    print(f"{'Daily Time Saved (vs casual):':<30} {daily_time_saved_casual:.1f} minutes")
    print(f"{'Daily Time Saved (vs professional):':<30} {daily_time_saved_professional:.1f} minutes")
    
    # Text content insights
    print(f"\n📈 CONTENT INSIGHTS")
    longest_recording = df_with_text.loc[df_with_text['characters'].idxmax()]
    most_words_recording = df_with_text.loc[df_with_text['estimated_words'].idxmax()]
    
    print(f"{'Longest Recording:':<30} {longest_recording['characters']:,} chars on {longest_recording['datetime'].date()}")
    print(f"{'Most Words in Recording:':<30} {most_words_recording['estimated_words']:,} words on {most_words_recording['datetime'].date()}")
    
    # Recent productivity
    recent_cutoff = df['datetime'].max() - timedelta(days=30)
    recent_df = df[df['datetime'] >= recent_cutoff]
    recent_time_saved = recent_df['time_saved_vs_professional_min'].sum()
    
    print(f"\n📅 RECENT PRODUCTIVITY (Last 30 Days)")
    print(f"{'Time Saved:':<30} {recent_time_saved/60:.1f} hours ({recent_time_saved:.0f} minutes)")
    print(f"{'Characters Generated:':<30} {recent_df['characters'].sum():,}")
    print(f"{'Words Generated:':<30} {recent_df['estimated_words'].sum():,}")

def create_text_visualizations(df):
    """Create visualizations focused on text analysis and time savings"""
    plt.style.use(config.STYLE)
    fig = plt.figure(figsize=config.FIGURE_SIZE)
    
    # Filter out recordings with no text for cleaner visualizations
    df_with_text = df[df['characters'] > 0]
    
    # 1. Daily Characters Generated
    plt.subplot(4, 2, 1)
    daily_chars = df.groupby('date')['characters'].sum()
    daily_chars.plot(kind='line', marker='o', color='steelblue')
    plt.title('Daily Characters Generated', fontsize=14, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Characters')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # 2. Daily Words Generated
    plt.subplot(4, 2, 2)
    daily_words = df.groupby('date')['estimated_words'].sum()
    daily_words.plot(kind='line', marker='s', color='green')
    plt.title('Daily Words Generated', fontsize=14, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Words')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # 3. Daily Time Saved (vs Professional Typing)
    plt.subplot(4, 2, 3)
    daily_time_saved = df.groupby('date')['time_saved_vs_professional_min'].sum()
    daily_time_saved.plot(kind='bar', color='orange', alpha=0.7)
    plt.title('Daily Time Saved vs Professional Typing (60 WPM)', fontsize=14, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Minutes Saved')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # 4. Speaking Speed Distribution
    plt.subplot(4, 2, 4)
    plt.hist(df_with_text['speaking_wpm'], bins=30, color='purple', alpha=0.7, edgecolor='black')
    plt.title('Speaking Speed Distribution (Words Per Minute)', fontsize=14, fontweight='bold')
    plt.xlabel('Speaking Speed (WPM)')
    plt.ylabel('Frequency')
    plt.axvline(df_with_text['speaking_wpm'].mean(), color='red', linestyle='--', 
                label=f'Average: {df_with_text["speaking_wpm"].mean():.1f} WPM')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 5. Character Count Distribution
    plt.subplot(4, 2, 5)
    plt.hist(df_with_text['characters'], bins=30, color='teal', alpha=0.7, edgecolor='black')
    plt.title('Character Count Distribution per Recording', fontsize=14, fontweight='bold')
    plt.xlabel('Characters per Recording')
    plt.ylabel('Frequency')
    plt.grid(True, alpha=0.3)
    
    # 6. Cumulative Time Saved
    plt.subplot(4, 2, 6)
    df_sorted = df.sort_values('datetime')
    cumulative_time_saved = df_sorted['time_saved_vs_professional_min'].cumsum()
    plt.plot(df_sorted['datetime'], cumulative_time_saved, color='red', linewidth=2)
    plt.title('Cumulative Time Saved vs Professional Typing', fontsize=14, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Minutes Saved')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # 7. Efficiency by Hour of Day
    plt.subplot(4, 2, 7)
    hourly_efficiency = df_with_text.groupby('hour')['efficiency_vs_professional'].mean()
    hourly_efficiency.plot(kind='bar', color='gold', alpha=0.7)
    plt.title('Average Efficiency by Hour of Day', fontsize=14, fontweight='bold')
    plt.xlabel('Hour of Day')
    plt.ylabel('Efficiency (% Time Saved)')
    plt.grid(True, alpha=0.3)
    
    # 8. Words vs Recording Duration Scatter
    plt.subplot(4, 2, 8)
    plt.scatter(df_with_text['duration_minutes'], df_with_text['estimated_words'], 
                alpha=0.6, color='coral')
    plt.title('Words Generated vs Recording Duration', fontsize=14, fontweight='bold')
    plt.xlabel('Recording Duration (Minutes)')
    plt.ylabel('Estimated Words')
    plt.grid(True, alpha=0.3)
    
    # Add trend line
    z = np.polyfit(df_with_text['duration_minutes'], df_with_text['estimated_words'], 1)
    p = np.poly1d(z)
    plt.plot(df_with_text['duration_minutes'], p(df_with_text['duration_minutes']), 
             "r--", alpha=0.8, linewidth=2)
    
    plt.tight_layout()
    plt.savefig(config.OUTPUT_FILES['text_analysis_chart'], dpi=config.DPI, bbox_inches='tight')
    print(f"Text analysis visualization saved as '{config.OUTPUT_FILES['text_analysis_chart']}'")

def main():
    """Main text analysis function"""
    start_time = time.time()
    
    print("🚀 SuperWhisper Text Analysis & Time Savings Calculator")
    print("=" * 70)
    
    # Load cached data
    recordings = load_cache_data()
    if recordings is None:
        return
    
    # Enhance with text analysis
    enhanced_recordings = enhance_data_with_text_analysis(recordings)
    
    # Create enhanced DataFrame
    df = create_text_analysis_dataframe(enhanced_recordings)
    
    # Print comprehensive text analysis
    print_text_analysis_summary(df)
    
    # Create text-focused visualizations
    print("\n📊 Generating text analysis visualizations...")
    create_text_visualizations(df)
    
    # Save enhanced data
    print("\n💾 Saving enhanced data...")
    config.ensure_data_dir()  # Create data directory for CSV files
    df.to_csv(config.OUTPUT_FILES['text_analysis_data'], index=False)
    
    # Performance summary
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"\n⚡ ANALYSIS COMPLETE!")
    print(f"Processing time: {processing_time:.1f} seconds")
    print("\nFiles saved:")
    print(f"- {config.OUTPUT_FILES['text_analysis_chart']} (text analysis visualizations)")
    print(f"- {config.OUTPUT_FILES['text_analysis_data']} (enhanced data with text analysis)")

if __name__ == "__main__":
    main() 