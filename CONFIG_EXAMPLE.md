# Configuration Example

When sharing this repository, you'll need to update `config.py` with your actual paths.

## Before (GitHub version):
```python
RECORDINGS_PATH = "~/Documents/superwhisper/recordings"
```

## After (your local version):
```python
RECORDINGS_PATH = "/Users/johndoe/Documents/superwhisper/recordings"
```

OR simply keep the tilde format (recommended):
```python
RECORDINGS_PATH = "~/Documents/superwhisper/recordings"
```

Replace `~` with your actual username and adjust the path to match where SuperWhisper stores your recordings.

## Finding Your SuperWhisper Path

1. Open SuperWhisper app
2. Go to Settings/Preferences
3. Look for "Recording Location" or "Storage Location"
4. Copy that path into `config.py`

## Auto-Detection

You can also run:
```bash
python config.py
```

This will attempt to auto-detect your SuperWhisper recordings path. 