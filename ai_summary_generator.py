#!/usr/bin/env python3
"""
AI-Powered SuperWhisper Summary Generator
Creates beautiful, shareable insights from your analytics using AI
"""

import json
import os
import pickle
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path
import config

def load_analysis_data():
    """Load all analysis data from cache and CSV files"""
    print("📊 Loading analysis data...")
    
    # Load raw recordings data
    try:
        with open(config.RECORDINGS_CACHE_FILE, 'rb') as f:
            recordings = pickle.load(f)
        print(f"✅ Loaded {len(recordings)} recordings from cache")
    except FileNotFoundError:
        print("❌ No cache found. Please run superwhisper_analysis_fast.py first.")
        return None
    
    # Create dataframe
    df = pd.DataFrame(recordings)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['date'] = df['datetime'].dt.date
    
    # Calculate key metrics
    total_recordings = len(df)
    total_hours = df['duration_minutes'].sum() / 60
    total_words = df['result_length'].sum() / 5  # Rough estimate
    total_chars = df['result_length'].sum()
    
    # Speaking speed
    speaking_wpm = total_words / (total_hours * 60) if total_hours > 0 else 0
    
    # Time savings calculations
    total_speaking_minutes = df['duration_minutes'].sum()
    typing_time_casual_minutes = total_words / config.TYPING_SPEEDS['casual']  # minutes
    typing_time_professional_minutes = total_words / config.TYPING_SPEEDS['professional']  # minutes
    typing_time_fast_minutes = total_words / config.TYPING_SPEEDS['fast']  # minutes
    
    time_saved_casual = (typing_time_casual_minutes - total_speaking_minutes) / 60  # hours
    time_saved_professional = (typing_time_professional_minutes - total_speaking_minutes) / 60  # hours
    time_saved_fast = (typing_time_fast_minutes - total_speaking_minutes) / 60  # hours
    
    # Daily stats
    daily_stats = df.groupby('date').agg({
        'duration_minutes': 'sum',
        'folder': 'count'
    }).rename(columns={'folder': 'num_recordings'})
    
    # Find peak day
    peak_day = daily_stats['duration_minutes'].idxmax()
    peak_minutes = daily_stats['duration_minutes'].max()
    peak_recordings = daily_stats.loc[peak_day, 'num_recordings']
    
    # Recent activity (last 30 days)
    recent_cutoff = df['datetime'].max() - timedelta(days=30)
    recent_df = df[df['datetime'] >= recent_cutoff]
    recent_words = recent_df['result_length'].sum() / 5
    recent_typing_time = recent_words / config.TYPING_SPEEDS['professional']  # minutes
    recent_time_saved = (recent_typing_time - recent_df['duration_minutes'].sum()) / 60  # hours
    
    # Compile summary data
    summary_data = {
        'total_recordings': total_recordings,
        'total_hours': round(total_hours, 1),
        'total_words': int(total_words),
        'total_characters': total_chars,
        'speaking_wpm': round(speaking_wpm, 1),
        'analysis_period': f"{df['datetime'].min().strftime('%B %Y')} to {df['datetime'].max().strftime('%B %Y')}",
        'active_days': len(daily_stats),
        'avg_daily_recordings': round(total_recordings / len(daily_stats), 1),
        'avg_daily_minutes': round(df['duration_minutes'].sum() / len(daily_stats), 1),
        'peak_day': peak_day.strftime('%B %d, %Y'),
        'peak_minutes': round(peak_minutes, 1),
        'peak_recordings': int(peak_recordings),
        'time_saved_casual_hours': round(time_saved_casual, 1),
        'time_saved_professional_hours': round(time_saved_professional, 1),
        'time_saved_fast_hours': round(time_saved_fast, 1),
        'efficiency_vs_casual': round((time_saved_casual / (typing_time_casual_minutes/60)) * 100, 1),
        'efficiency_vs_professional': round((time_saved_professional / (typing_time_professional_minutes/60)) * 100, 1),
        'recent_words': int(recent_words),
        'recent_time_saved_hours': round(recent_time_saved, 1),
        'speed_multiplier_casual': round(speaking_wpm / config.TYPING_SPEEDS['casual'], 1),
        'speed_multiplier_professional': round(speaking_wpm / config.TYPING_SPEEDS['professional'], 1),
        'busiest_hour': df.groupby(df['datetime'].dt.hour)['duration_minutes'].sum().idxmax(),
        'busiest_day': df.groupby(df['datetime'].dt.day_name())['duration_minutes'].sum().idxmax()
    }
    
    return summary_data

def setup_ai_client():
    """Setup AI client (OpenAI or Anthropic) based on user preference"""
    print("\n🤖 AI Summary Generator Setup")
    print("=" * 50)
    print("Choose your AI provider:")
    print("1. OpenAI (GPT-4)")
    print("2. Anthropic (Claude)")
    print("3. Skip AI generation")
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == "3":
        return None, None
    
    if choice == "1":
        try:
            import openai
            api_key = input("Enter your OpenAI API key: ").strip()
            if not api_key:
                print("❌ No API key provided")
                return None, None
            
            client = openai.OpenAI(api_key=api_key)
            return client, "openai"
        except ImportError:
            print("❌ OpenAI package not installed. Run: pip install openai")
            return None, None
    
    elif choice == "2":
        try:
            import anthropic
            api_key = input("Enter your Anthropic API key: ").strip()
            if not api_key:
                print("❌ No API key provided")
                return None, None
            
            client = anthropic.Anthropic(api_key=api_key)
            return client, "anthropic"
        except ImportError:
            print("❌ Anthropic package not installed. Run: pip install anthropic")
            return None, None
    
    else:
        print("❌ Invalid choice")
        return None, None

def generate_ai_summary(data, client, provider):
    """Generate AI-powered summary of the analytics"""
    
    prompt = f"""
Create a compelling, shareable summary of this SuperWhisper voice recording analysis. The data shows impressive productivity gains from using voice-to-text technology.

ANALYTICS DATA:
- Total recordings: {data['total_recordings']:,} over {data['active_days']} days
- Total speaking time: {data['total_hours']} hours
- Words generated: {data['total_words']:,} words
- Characters: {data['total_characters']:,}
- Speaking speed: {data['speaking_wpm']} WPM
- Analysis period: {data['analysis_period']}
- Daily averages: {data['avg_daily_recordings']} recordings, {data['avg_daily_minutes']} minutes
- Peak day: {data['peak_day']} ({data['peak_minutes']} minutes, {data['peak_recordings']} recordings)
- Time saved vs casual typing: {data['time_saved_casual_hours']} hours
- Time saved vs professional typing: {data['time_saved_professional_hours']} hours  
- Speed multiplier vs professional typing: {data['speed_multiplier_professional']}x faster
- Efficiency gain vs professional typing: {data['efficiency_vs_professional']}%
- Recent 30 days: {data['recent_words']:,} words, {data['recent_time_saved_hours']} hours saved
- Usage patterns: Busiest at {data['busiest_hour']}:00 on {data['busiest_day']}s

Create a summary that:
1. Starts with a compelling hook about productivity gains
2. Highlights the most impressive numbers (time saved, speed multiplier, efficiency)
3. Includes specific metrics that demonstrate ROI
4. Is perfect for sharing on LinkedIn or in presentations
5. Uses emojis strategically for visual appeal
6. Ends with a call-to-action about voice productivity

Format as markdown with clear sections. Make it engaging and shareable!
"""

    print("🤖 Generating AI summary...")
    
    try:
        if provider == "openai":
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a data storytelling expert who creates compelling summaries of productivity analytics."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            return response.choices[0].message.content
            
        elif provider == "anthropic":
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
            
    except Exception as e:
        print(f"❌ Error generating AI summary: {e}")
        return None

def create_fallback_summary(data):
    """Create a fallback summary without AI"""
    return f"""# 🎙️ SuperWhisper Analytics Summary

## 📊 Productivity Overview

I analyzed **{data['analysis_period']}** of voice recording data and discovered some incredible productivity gains!

### 🚀 Key Numbers
- **{data['total_recordings']:,} recordings** across {data['active_days']} active days
- **{data['total_hours']} hours** of total speaking time  
- **{data['total_words']:,} words** generated (equivalent to ~{data['total_words']//250} pages!)
- **{data['speaking_wpm']} WPM** average speaking speed

### ⚡ Time Savings
By speaking instead of typing, I saved:
- **{data['time_saved_professional_hours']} hours** vs professional typing (60 WPM)
- **{data['time_saved_casual_hours']} hours** vs casual typing (35 WPM)
- That's **{data['speed_multiplier_professional']}x faster** than professional typing!

### 📈 Daily Impact
- **{data['avg_daily_recordings']} recordings** per day on average
- **{data['avg_daily_minutes']} minutes** of daily speaking
- **{data['efficiency_vs_professional']}% efficiency gain** vs typing
- Peak day: **{data['peak_day']}** ({data['peak_minutes']} minutes!)

### 🎯 Recent Performance (Last 30 Days)
- **{data['recent_words']:,} words** generated through voice
- **{data['recent_time_saved_hours']} hours** saved vs typing
- Most active on **{data['busiest_day']}s** at **{data['busiest_hour']}:00**

## 💡 Bottom Line

Voice-to-text isn't just convenient—it's a **{data['speed_multiplier_professional']}x productivity multiplier** that saves me **{data['time_saved_professional_hours']} hours** compared to traditional typing.

*Generated from SuperWhisper analytics on {datetime.now().strftime('%B %d, %Y')}*
"""

def save_summary(summary, filename="superwhisper_summary.md"):
    """Save the summary to a markdown file"""
    config.ensure_data_dir()
    filepath = f"data/{filename}"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"✅ Summary saved to: {filepath}")
    return filepath

def main():
    """Main summary generation function"""
    print("🎙️ SuperWhisper AI Summary Generator")
    print("=" * 50)
    
    # Load data
    data = load_analysis_data()
    if not data:
        return
    
    # Setup AI client
    client, provider = setup_ai_client()
    
    # Generate summary
    if client and provider:
        summary = generate_ai_summary(data, client, provider)
        if summary:
            print("✅ AI summary generated successfully!")
        else:
            print("⚠️ AI generation failed, using fallback...")
            summary = create_fallback_summary(data)
    else:
        print("📝 Using fallback summary (no AI)...")
        summary = create_fallback_summary(data)
    
    # Save summary
    filepath = save_summary(summary)
    
    # Show preview
    print(f"\n📋 SUMMARY PREVIEW:")
    print("=" * 50)
    print(summary[:500] + "..." if len(summary) > 500 else summary)
    print("=" * 50)
    
    print(f"\n🎉 Complete! Your shareable summary is ready at: {filepath}")
    print("Perfect for LinkedIn posts, blog articles, or presentations!")

if __name__ == "__main__":
    main() 