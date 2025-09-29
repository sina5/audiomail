# Configuration

AudioMail can be extensively configured through the `config.ini` file. This guide explains all available settings and how to optimize them for your use case.

## Configuration File Location

AudioMail looks for `config.ini` in:
1. Current working directory
2. AudioMail installation directory
3. User home directory (`~/.audiomail/config.ini`)

If no config file is found, AudioMail creates a default one in the current directory.

## Configuration Sections

### [audio] - Audio Recording Settings

Controls how AudioMail captures and processes audio input.

```ini
[audio]
# Sample rate for audio recording (Hz)
sample_rate = 44100

# Number of audio channels (1 = mono, 2 = stereo)
channels = 1

# Directory to save audio recordings
recordings_dir = recordings

# Whether to save audio recordings (true/false)
save_recordings = false

# Audio device ID (use 'auto' for default, or specific device ID)
device_id = auto

# Audio input buffer size
buffer_size = 1024
```

#### Audio Settings Explained

**Sample Rate**: Higher values capture more detail but create larger files
- `22050`: Basic quality, smallest files
- `44100`: CD quality, recommended for most users  
- `48000`: Professional quality, larger files

**Channels**: 
- `1` (mono): Recommended for voice, smaller files
- `2` (stereo): Only needed for music or multi-speaker recordings

**Device Selection**:
```bash
# List available audio devices
python -c "import sounddevice; print(sounddevice.query_devices())"
```

### [whisper] - Speech Recognition Settings

Configures the Whisper model for speech-to-text conversion.

```ini
[whisper]
# Whisper model size: tiny, base, small, medium, large
model_size = tiny

# Processing device: auto, cpu, cuda, mps
device = auto

# Language for transcription (leave empty for auto-detection)
language = 

# Enable faster transcription with potential quality trade-off
fast_mode = false
```

#### Model Size Comparison

| Model | Size | VRAM | Speed | Quality |
|-------|------|------|-------|---------|
| `tiny` | 39 MB | ~1 GB | Fastest | Basic |
| `base` | 74 MB | ~1 GB | Fast | Good |
| `small` | 244 MB | ~2 GB | Medium | Better |
| `medium` | 769 MB | ~5 GB | Slow | Great |
| `large` | 1550 MB | ~10 GB | Slowest | Best |

!!! tip "Model Selection"
    - **For testing**: Use `tiny` for quick setup
    - **For daily use**: Use `base` or `small`
    - **For best quality**: Use `large` if you have sufficient VRAM

#### Device Selection

- `auto`: Automatically chooses the best available device
- `cpu`: Force CPU processing (slower but works everywhere)
- `cuda`: Use NVIDIA GPU (requires CUDA installation)
- `mps`: Use Apple Silicon GPU (Mac only)

### [llm] - Language Model Settings

Configures the large language model for email generation.

```ini
[llm]
# Hugging Face model name
model_name = microsoft/DialoGPT-medium

# Device for model execution
device = auto

# Trust remote code (required for some models)
trust_remote_code = true

# Data type: auto, float16, float32, bfloat16
dtype = auto

# Maximum context length
max_context_length = 2048
```

#### Recommended Models

**For Speed** (Low VRAM):
```ini
model_name = microsoft/DialoGPT-small
dtype = float16
```

**For Balance** (Medium VRAM):
```ini
model_name = microsoft/DialoGPT-medium
dtype = float16
```

**For Quality** (High VRAM):
```ini
model_name = microsoft/DialoGPT-large
dtype = float16
```

**For Latest Features**:
```ini
model_name = microsoft/DialoGPT-medium
trust_remote_code = true
dtype = auto
```

### [generation] - Email Generation Settings

Fine-tune how emails are generated.

```ini
[generation]
# Maximum tokens in generated email
max_new_tokens = 512

# Controls randomness (0.0 = deterministic, 1.0 = very random)
temperature = 0.7

# Nucleus sampling threshold
top_p = 0.95

# Whether to use sampling (true) or greedy decoding (false)
do_sample = true

# Number of beams for beam search (1 = disabled)
num_beams = 1

# Repetition penalty to avoid repetitive text
repetition_penalty = 1.1
```

#### Generation Parameters Explained

**Temperature** controls creativity:
- `0.1-0.3`: Very conservative, formal emails
- `0.5-0.7`: Balanced, professional tone
- `0.8-1.0`: Creative, varied language

**Top-p** (nucleus sampling):
- `0.9`: More focused, consistent style
- `0.95`: Balanced variety and consistency
- `0.99`: Maximum variety in word choice

**Max Tokens**: Typical email lengths:
- `128`: Short, direct emails
- `256`: Standard business emails
- `512`: Detailed, comprehensive emails
- `1024`: Long, formal communications

### [paths] - File and Directory Settings

```ini
[paths]
# Directory for audio recordings
recordings_dir = recordings

# Directory for temporary files
temp_dir = temp

# Directory for model cache
cache_dir = ~/.cache/audiomail

# Log file location
log_file = audiomail.log
```

## Environment-Specific Configurations

### Development Configuration

For development and testing:

```ini
[audio]
sample_rate = 22050
save_recordings = true

[whisper]
model_size = tiny
device = cpu

[llm]
model_name = microsoft/DialoGPT-small
device = cpu

[generation]
max_new_tokens = 128
temperature = 0.5
```

### Production Configuration

For daily use with good hardware:

```ini
[audio]
sample_rate = 44100
save_recordings = false

[whisper]
model_size = base
device = auto

[llm]
model_name = microsoft/DialoGPT-medium
device = auto
dtype = float16

[generation]
max_new_tokens = 512
temperature = 0.7
```

### High-Performance Configuration

For powerful systems with GPU:

```ini
[audio]
sample_rate = 48000
save_recordings = true

[whisper]
model_size = large
device = cuda

[llm]
model_name = microsoft/DialoGPT-large
device = cuda
dtype = float16

[generation]
max_new_tokens = 1024
temperature = 0.7
top_p = 0.95
```

### Low-Resource Configuration

For systems with limited memory:

```ini
[audio]
sample_rate = 22050
channels = 1

[whisper]
model_size = tiny
device = cpu

[llm]
model_name = microsoft/DialoGPT-small
device = cpu
dtype = float32

[generation]
max_new_tokens = 256
temperature = 0.6
```

## Configuration Validation

AudioMail validates your configuration on startup. Common issues:

!!! warning "Invalid Model Names"
    ```
    Error: Model 'invalid/model' not found
    ```
    Check the model name on Hugging Face Hub.

!!! warning "Device Not Available"
    ```
    Warning: CUDA not available, falling back to CPU
    ```
    Install CUDA toolkit or use `device = cpu`.

!!! warning "Insufficient Memory"
    ```
    Error: CUDA out of memory
    ```
    Use smaller models or reduce batch size.

## Advanced Configuration

### Custom Model Paths

Use local models instead of downloading:

```ini
[llm]
model_name = /path/to/local/model
trust_remote_code = true
```

### Multiple Configurations

Use different configs for different scenarios:

```bash
# Work emails
python audiomail_cli.py --config config_work.ini

# Personal emails  
python audiomail_cli.py --config config_personal.ini

# Quick drafts
python audiomail_cli.py --config config_fast.ini
```

### Environment Variables

Override config with environment variables:

```bash
export AUDIOMAIL_WHISPER_MODEL="base"
export AUDIOMAIL_LLM_DEVICE="cuda"
export AUDIOMAIL_TEMPERATURE="0.8"

python audiomail_cli.py
```

## Performance Tuning

### For Speed

```ini
[whisper]
model_size = tiny
fast_mode = true

[llm]
model_name = microsoft/DialoGPT-small

[generation]
max_new_tokens = 128
num_beams = 1
do_sample = false
```

### For Quality

```ini
[whisper]
model_size = large
language = en

[llm]
model_name = microsoft/DialoGPT-large

[generation]
max_new_tokens = 512
temperature = 0.7
num_beams = 4
```

### For Memory Efficiency

```ini
[whisper]
device = cpu
model_size = base

[llm]
device = cpu
dtype = float32

[generation]
max_new_tokens = 256
```

## Troubleshooting Configuration

### Check Current Configuration

```bash
python -c "from audiomail import load_config; print(load_config())"
```

### Validate Configuration

```bash
python audiomail_cli.py --validate-config
```

### Reset to Defaults

```bash
mv config.ini config.ini.backup
python audiomail_cli.py  # Creates new default config
```

## Next Steps

- [Troubleshooting Guide](troubleshooting.md) for configuration issues
- [CLI Guide](cli.md) for command-line usage
- [Web UI Guide](ui.md) for visual interface