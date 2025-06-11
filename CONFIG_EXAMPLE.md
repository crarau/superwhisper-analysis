# SuperWhisper Analysis Configuration Example

This file shows you how to configure the SuperWhisper Analysis tool for your environment.

## Basic Setup

1. **Copy config.py and customize your paths**:
```python
# Update this path to match your SuperWhisper recordings location
RECORDINGS_PATH = "~/Documents/superwhisper/recordings"
```

## AI Summary Generation Setup (Optional)

For AI-powered summary generation, set up your API keys via environment variables for security:

### Anthropic Claude (Recommended)
```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export ANTHROPIC_API_KEY="your_anthropic_api_key_here"
```

### OpenAI GPT-4 (Alternative)
```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export OPENAI_API_KEY="your_openai_api_key_here"
```

### Setting Environment Variables

**macOS/Linux:**
```bash
# Temporary (current session only)
export ANTHROPIC_API_KEY="your_key_here"

# Permanent (add to ~/.zshrc or ~/.bashrc)
echo 'export ANTHROPIC_API_KEY="your_key_here"' >> ~/.zshrc
source ~/.zshrc
```

**Windows:**
```cmd
# Temporary
set ANTHROPIC_API_KEY=your_key_here

# Permanent (via System Properties > Environment Variables)
```

## Common SuperWhisper Paths

Try these common locations if your recordings aren't found:
- `~/Documents/superwhisper/recordings`
- `~/Library/Application Support/SuperWhisper/recordings`  
- `~/SuperWhisper/recordings`

## Security Best Practices

- ✅ Use environment variables for API keys (as shown above)
- ❌ Never commit API keys directly to git repositories
- 🔒 Keep your API keys private and secure

## Testing Your Configuration

Run this command to test if your configuration is working:

```bash
python config.py
```

This will attempt to auto-detect your SuperWhisper recordings path. 