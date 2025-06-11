# Quick Setup Guide

## 1. Configure Your Path
Edit `config.py` and update the `RECORDINGS_PATH` variable:
```python
RECORDINGS_PATH = "/Users/yourusername/Documents/superwhisper/recordings"
```

## 2. Test Configuration
```bash
python config.py
```

## 3. Run Analysis
```bash
python superwhisper_analysis_fast.py
python superwhisper_text_analysis.py
```

## 4. Troubleshooting
- First run may take ~10 minutes for large datasets
- Future runs will be ~5 seconds (uses cache)
- Check path if you get "recordings path does not exist" error 