# SuperWhisper Recording Analysis 🎙️📊

A comprehensive Python toolkit for analyzing SuperWhisper voice recording data, providing detailed insights into your recording habits, productivity gains, and time savings from speaking vs typing.

## 🚀 Features

- **Comprehensive Recording Analysis**: Daily, weekly, and monthly statistics
- **Text Content Analysis**: Character counts, word estimates, and content insights
- **Time Savings Calculator**: Compare speaking vs typing efficiency across different typing speeds
- **Productivity Metrics**: Track your speaking speed, efficiency gains, and daily productivity impact
- **Beautiful Visualizations**: 8+ detailed charts showing your recording patterns and trends
- **AI-Powered Summaries**: Generate shareable insights using OpenAI or Anthropic APIs
- **iCloud Optimization**: Smart caching system to handle iCloud sync delays
- **Fast Processing**: Parallel processing with progress bars for large datasets

## 📈 What You'll Discover

- How many hours you've recorded and how much text you've generated
- Time saved vs different typing speeds (casual, professional, fast)
- Your speaking patterns by hour of day and day of week
- Recording duration trends and productivity insights
- Cumulative time savings and efficiency metrics
- Your most productive days and content insights
- AI-generated shareable summaries perfect for social media and presentations

## 🗣️ Example: Recent Activity Insights

Here's a sample of the user-friendly insights you'll get about your voice recording habits:

> **In the last 30 days**, I've been talking instead of typing - and it's completely changed my daily routine! Imagine having a casual 40-minute conversation every day; that's about how much I speak to my device. I average about 4,200 words daily, which is roughly the length of a lengthy blog post or a short story.
>
> Here's what amazes me: **I'm saving nearly 20 hours per month** just by speaking instead of typing. That's like getting back an entire weekend! I find myself reaching for voice input about 69 times throughout the day - pretty much whenever I need to write anything longer than a quick text.
>
> The coolest part? I'm speaking at a comfortable pace (about 113 words per minute), which is nearly twice as fast as if I were typing. It's like the difference between walking and riding a bike - same destination, but you get there so much quicker! I tend to be most chatty on Wednesday afternoons, usually around 1 PM when my creative energy is flowing.
>
> If you're curious about trying voice-to-text, I'd absolutely recommend it. It's as simple as talking to a friend, and you might be surprised how natural it feels after just a few days. Think about all the things you could do with an extra 20 hours a month - that's a lot of Netflix shows, walks in the park, or quality time with family!

*This is the kind of personal, relatable summary the AI generator creates from your own SuperWhisper data - perfect for sharing with friends or inspiring others to try voice-to-text technology!*

### 📊 Underlying Data Structure

Here's the actual data that gets sent to the AI to generate the above summary:

```
RECENT ACTIVITY DATA (Last 30 Days):
- Daily talking habit: 4,200 words per day on average
- Time spent talking: 40.0 minutes per day
- Time saved vs typing: 1,200 minutes total (40.0 min/day)
- How often I use voice: 68.8 times per day
- Recent productivity: Generated 126,092 words in 30 days

OVERALL CONTEXT:
- Total experience: February 09, 2025 to June 11, 2025
- Speaking speed: 112.6 words per minute
- vs Professional typing: 1.9x faster
- Peak day was: March 03, 2025 (89.5 minutes)
- Most active time: Wednesdays at 1:00
```

*The AI transforms these raw metrics into engaging, relatable stories that anyone can understand and share.*

## 🛠️ Installation

1. **Clone the repository**:
```bash
git clone https://github.com/~/superwhisper-analysis.git
cd superwhisper-analysis
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Optional: Install AI dependencies** (for summary generation):
```bash
# For OpenAI GPT-4 summaries
pip install openai

# OR for Anthropic Claude summaries  
pip install anthropic
```

## 📁 Setup

1. **Configure your SuperWhisper recordings path** in `config.py`:
```python
RECORDINGS_PATH = "~/Documents/superwhisper/recordings"
```

2. **Make sure your SuperWhisper recordings are accessible** (if using iCloud, ensure they're downloaded locally or the script will handle the sync automatically)

## 🎯 Usage

### Quick Start - Full Analysis
```bash
python superwhisper_analysis_fast.py
```

### Text Analysis & Time Savings
```bash
python superwhisper_text_analysis.py
```

### AI-Powered Summary Generation
```bash
python ai_summary_generator.py
```
Creates beautiful, shareable summaries perfect for LinkedIn, blogs, or presentations using OpenAI or Anthropic APIs.

**Features:**
- Choose between OpenAI (GPT-4) or Anthropic (Claude) 
- Works without AI (fallback summary)
- Generates markdown formatted summaries
- Perfect for social media posts and presentations

### First Run (Large Dataset)
The first run will:
- Cache all `meta.json` files locally for faster future processing
- Process files in parallel to handle large datasets efficiently
- Create a `.pkl` cache file for instant future analysis

**Expected time**: ~10 minutes for 7,000+ recordings
**Future runs**: ~5 seconds (uses cache)

## 📊 Output Files

The analysis generates several files:

### Visualizations (Main Directory)
- `superwhisper_analysis_fast.png` - 8 comprehensive charts showing recording patterns
- `superwhisper_text_analysis.png` - Text analysis and time savings visualizations

### Data Files (data/ Directory)
- `data/recordings_detailed_fast.csv` - Complete dataset with all metrics
- `data/daily_stats_fast.csv` - Daily aggregated statistics
- `data/weekly_stats_fast.csv` - Weekly aggregated statistics  
- `data/monthly_stats_fast.csv` - Monthly aggregated statistics
- `data/recordings_text_analysis.csv` - Enhanced data with text analysis and time savings
- `data/superwhisper_summary.md` - AI-generated shareable summary (markdown format)

### Cache Files
- `recordings_cache.pkl` - Processed data cache for fast future runs
- `cache_meta_files/` - Local cache of meta.json files

## 📋 Sample Output

```
📊 OVERALL STATISTICS
Total Recordings:         7,688
Total Recording Time:     46.9 hours
Average Duration:         0.4 minutes
Date Range:               2025-02-09 to 2025-06-11

⏱️ TIME SAVINGS ANALYSIS
Recording Time:           46.9 hours

TIME SAVED vs DIFFERENT TYPING SPEEDS:
vs Casual Typing (35 WPM):     106.0 hours (6362 min)
vs Professional (60 WPM):      44.2 hours (2652 min)
vs Fast Typing (80 WPM):       23.5 hours (1408 min)

📝 TEXT CONTENT STATISTICS
Total Characters:         1,600,590
Total Estimated Words:    317,069
Average Speaking Speed:   126.7 WPM
```

## 🔧 Configuration

Edit `config.py` to customize:
- Recording path location
- Analysis parameters
- Output preferences
- Typing speed benchmarks

## 📱 SuperWhisper App

This tool analyzes data from the [SuperWhisper](https://superwhisper.com/) macOS app - an AI-powered voice-to-text application that creates local recordings with detailed metadata.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details

## ⚠️ Privacy Note

This tool processes data locally and does not send any information to external servers. All analysis is performed on your machine using the metadata from your SuperWhisper recordings.

## 🐛 Troubleshooting

### iCloud Sync Issues
If you encounter slow processing due to iCloud sync:
- The script automatically handles this by creating a local cache
- First run may take longer as files download from iCloud
- Subsequent runs will be much faster using the local cache

### Large Datasets
For datasets with thousands of recordings:
- Use `superwhisper_analysis_fast.py` for optimized processing
- Enable parallel processing (default: 8 workers)
- Monitor progress with built-in progress bars

### Memory Issues
If you encounter memory issues with very large datasets:
- The script processes data in chunks
- Cache files help reduce memory usage
- Consider running analysis on smaller date ranges if needed

## 📞 Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

**Made with ❤️ for SuperWhisper users who want to understand their voice recording patterns and productivity gains.** 