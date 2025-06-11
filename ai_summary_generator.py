#!/usr/bin/env python3
"""
AI-Powered SuperWhisper Summary Generator
Creates beautiful, shareable insights from your analytics using AI
"""

import pandas as pd
import os
import pickle
from datetime import datetime, timedelta
import config

def load_config():
    """Load configuration, handling missing attributes gracefully"""
    try:
        # Check if config has required attributes
        if not hasattr(config, 'ANTHROPIC_API_KEY'):
            config.ANTHROPIC_API_KEY = None
        if not hasattr(config, 'OPENAI_API_KEY'):
            config.OPENAI_API_KEY = None
            
        print("✅ Configuration loaded successfully")
        return config
        
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        print("💡 Please ensure config.py exists and is properly configured")
        return None

def load_analytics_data():
    """Load analytics data from CSV files"""
    try:
        # Load the detailed text analysis results
        text_analysis_file = "data/recordings_text_analysis.csv"
        if not os.path.exists(text_analysis_file):
            print(f"❌ Analytics file not found: {text_analysis_file}")
            print("💡 Run 'python superwhisper_text_analysis.py' first to generate analytics data")
            return None
        
        # Read the detailed recording data
        df = pd.read_csv(text_analysis_file)
        if df.empty:
            print("❌ Analytics file is empty")
            return None
        
        print(f"✅ Loaded {len(df)} recordings for analysis")
        
        # Calculate aggregate statistics
        total_recordings = len(df)
        total_minutes = df['duration_minutes'].sum()
        total_characters = df['result_length'].sum()
        total_words = df['estimated_words'].sum()
        total_time_saved_professional = df['time_saved_vs_professional_min'].sum()
        total_time_saved_casual = df['time_saved_vs_casual_min'].sum()
        
        # Speaking speed
        speaking_wpm = total_words / total_minutes if total_minutes > 0 else 0
        
        # Date range
        df['datetime'] = pd.to_datetime(df['datetime'])
        first_date = df['datetime'].min().strftime('%B %d, %Y')
        last_date = df['datetime'].max().strftime('%B %d, %Y')
        
        # Active days
        unique_dates = df['datetime'].dt.date.nunique()
        
        # Daily averages
        avg_daily_recordings = total_recordings / unique_dates if unique_dates > 0 else 0
        avg_daily_minutes = total_minutes / unique_dates if unique_dates > 0 else 0
        
        # Peak day analysis
        daily_stats = df.groupby(df['datetime'].dt.date).agg({
            'duration_minutes': 'sum',
            'result_length': 'count'  # count recordings per day
        }).rename(columns={'result_length': 'recordings_count'})
        
        peak_day_date = daily_stats['duration_minutes'].idxmax()
        peak_minutes = daily_stats['duration_minutes'].max()
        peak_recordings = daily_stats.loc[peak_day_date, 'recordings_count']
        peak_day = peak_day_date.strftime('%B %d, %Y')
        
        # Usage patterns
        busiest_hour = df.groupby(df['datetime'].dt.hour)['duration_minutes'].sum().idxmax()
        busiest_day = df.groupby(df['datetime'].dt.day_name())['duration_minutes'].sum().idxmax()
        
        # Recent activity (last 30 days)
        cutoff_date = df['datetime'].max() - timedelta(days=30)
        recent_df = df[df['datetime'] >= cutoff_date]
        recent_words = recent_df['estimated_words'].sum()
        recent_time_saved_hours = recent_df['time_saved_vs_professional_min'].sum() / 60
        
        # Efficiency calculations
        total_speaking_hours = total_minutes / 60
        total_typing_time_professional = total_words / 60  # minutes at 60 WPM
        speed_multiplier_professional = speaking_wpm / 60 if speaking_wpm > 0 else 0
        efficiency_vs_professional = (total_time_saved_professional / (total_typing_time_professional + total_minutes)) * 100 if (total_typing_time_professional + total_minutes) > 0 else 0
        
        return {
            'total_recordings': total_recordings,
            'active_days': unique_dates,
            'total_hours': f"{total_minutes / 60:.1f}",
            'total_words': int(total_words),
            'total_characters': int(total_characters),
            'speaking_wpm': f"{speaking_wpm:.1f}",
            'analysis_period': f"{first_date} to {last_date}",
            'avg_daily_recordings': f"{avg_daily_recordings:.1f}",
            'avg_daily_minutes': f"{avg_daily_minutes:.1f}",
            'peak_day': peak_day,
            'peak_minutes': f"{peak_minutes:.1f}",
            'peak_recordings': int(peak_recordings),
            'time_saved_casual_hours': f"{total_time_saved_casual / 60:.1f}",
            'time_saved_professional_hours': f"{total_time_saved_professional / 60:.1f}",
            'speed_multiplier_professional': f"{speed_multiplier_professional:.1f}",
            'efficiency_vs_professional': f"{efficiency_vs_professional:.1f}",
            'busiest_hour': int(busiest_hour),
            'busiest_day': busiest_day,
            'recent_words': int(recent_words),
            'recent_time_saved_hours': recent_time_saved_hours
        }
        
    except Exception as e:
        print(f"❌ Error loading analytics data: {e}")
        import traceback
        traceback.print_exc()
        return None

def setup_ai_client(config):
    """Setup AI client based on configuration"""
    try:
        # Try Anthropic first if API key is available
        if hasattr(config, 'ANTHROPIC_API_KEY') and config.ANTHROPIC_API_KEY:
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
                print("✅ Using Anthropic Claude for AI generation")
                return client, "anthropic"
            except ImportError:
                print("⚠️ Anthropic library not installed. Install with: pip install anthropic")
            except Exception as e:
                print(f"⚠️ Anthropic setup failed: {e}")
        
        # Try OpenAI as fallback
        if hasattr(config, 'OPENAI_API_KEY') and config.OPENAI_API_KEY:
            try:
                import openai
                client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
                print("✅ Using OpenAI GPT-4 for AI generation")
                return client, "openai"
            except ImportError:
                print("⚠️ OpenAI library not installed. Install with: pip install openai")
            except Exception as e:
                print(f"⚠️ OpenAI setup failed: {e}")
        
        print("❌ No AI provider available. Please configure API keys in config.py")
        return None, None
        
    except Exception as e:
        print(f"❌ Error setting up AI client: {e}")
        return None, None

def generate_recent_activity_prompt(data):
    """Generate a user-friendly prompt focused on recent habits"""
    # Handle mixed data types safely
    recent_words = data.get('recent_words', 0)
    recent_time_saved_hours = data.get('recent_time_saved_hours', 0)
    avg_daily_recordings = data.get('avg_daily_recordings', '0')
    speaking_wpm = data.get('speaking_wpm', '0')
    speed_multiplier_professional = data.get('speed_multiplier_professional', '0')
    peak_day = data.get('peak_day', 'N/A')
    peak_minutes = data.get('peak_minutes', '0')
    busiest_day = data.get('busiest_day', 'N/A')
    busiest_hour = data.get('busiest_hour', '0')
    analysis_period = data.get('analysis_period', 'N/A')
    
    # Calculate daily averages safely
    try:
        daily_words = int(recent_words) / 30 if recent_words else 0
        daily_talk_minutes = float(recent_time_saved_hours) * 60 / 30 if recent_time_saved_hours else 0
        total_saved_minutes = float(recent_time_saved_hours) * 60 if recent_time_saved_hours else 0
        daily_saved_minutes = total_saved_minutes / 30 if total_saved_minutes else 0
    except (ValueError, TypeError):
        daily_words = 0
        daily_talk_minutes = 0
        total_saved_minutes = 0
        daily_saved_minutes = 0
    
    return f"""
Create a compelling, easy-to-understand summary focused on recent voice recording habits. This should be relatable for anyone, not just tech people.

RECENT ACTIVITY DATA (Last 30 Days):
- Daily talking habit: {daily_words:.0f} words per day on average
- Time spent talking: {daily_talk_minutes:.1f} minutes per day
- Time saved vs typing: {total_saved_minutes:.0f} minutes total ({daily_saved_minutes:.1f} min/day)
- How often I use voice: {avg_daily_recordings} times per day
- Recent productivity: Generated {recent_words:,} words in 30 days

OVERALL CONTEXT:
- Total experience: {analysis_period}
- Speaking speed: {speaking_wpm} words per minute
- vs Professional typing: {speed_multiplier_professional}x faster
- Peak day was: {peak_day} ({peak_minutes} minutes)
- Most active time: {busiest_day}s at {busiest_hour}:00

Create a summary that:
1. Starts with "In the last 30 days..." to focus on recent habits
2. Uses simple, relatable language (avoid tech jargon)
3. Compares to everyday activities people understand
4. Emphasizes the convenience and time savings
5. Shows daily habits that anyone can relate to
6. Uses conversational tone, like telling a friend
7. Ends with encouragement for others to try voice-to-text

Make it feel personal and inspiring, not technical. Focus on the human impact!
"""

def generate_ai_summary(data, client, provider, focus="comprehensive"):
    """Generate AI-powered summary of the analytics"""
    
    if focus == "recent":
        prompt = generate_recent_activity_prompt(data)
    else:
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

def main():
    print("🎙️ SuperWhisper AI Summary Generator")
    print("=====================================")
    
    # Load configuration
    config = load_config()
    if not config:
        return
    
    # Setup AI client
    client, provider = setup_ai_client(config)
    if not client:
        return
    
    # Load analytics data
    print("\n📊 Loading analytics data...")
    data = load_analytics_data()
    if not data:
        return
    
    # Menu for summary type
    print("\n🤖 Choose summary type:")
    print("1. 📈 Comprehensive Analysis (Great for sharing)")
    print("2. 🗣️  Recent Activity (Last 30 days - User-friendly)")
    print("3. 📋 Both Summaries")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    summaries_to_generate = []
    if choice == "1":
        summaries_to_generate = [("comprehensive", "📈 Comprehensive Analysis")]
    elif choice == "2":
        summaries_to_generate = [("recent", "🗣️ Recent Activity Summary")]
    elif choice == "3":
        summaries_to_generate = [
            ("comprehensive", "📈 Comprehensive Analysis"),
            ("recent", "🗣️ Recent Activity Summary")
        ]
    else:
        print("❌ Invalid choice. Defaulting to comprehensive analysis.")
        summaries_to_generate = [("comprehensive", "📈 Comprehensive Analysis")]
    
    # Generate summaries
    for focus, title in summaries_to_generate:
        print(f"\n{title}")
        print("=" * 50)
        
        summary = generate_ai_summary(data, client, provider, focus)
        if summary:
            print(f"✅ Generated {title.lower()}!")
            print("\n" + "="*60)
            print(summary)
            print("="*60)
            
            # Save to file
            filename = f"ai_summary_{focus}.md"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"# {title}\n\n")
                    f.write(f"*Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*\n\n")
                    f.write(summary)
                print(f"📝 Summary saved to: {filename}")
            except Exception as e:
                print(f"❌ Error saving summary: {e}")
        else:
            print(f"❌ Failed to generate {title.lower()}")
    
    print(f"\n✨ Summary generation complete using {provider.upper()}!")
    print("💡 Tip: Share these summaries to inspire others to try voice-to-text!")

if __name__ == "__main__":
    main() 