# Troubleshooting

This guide helps you diagnose and resolve common issues with AudioMail.

## Quick Diagnosis

### System Check

Run this quick diagnostic to identify potential issues:

```bash
# Check Python version
python --version

# Check AudioMail imports
python -c "import audiomail; print('AudioMail imports successfully')"

# Check dependencies
python -c "import torch, transformers, sounddevice; print('All dependencies available')"

# Check audio devices
python -c "import sounddevice; print(sounddevice.query_devices())"
```

### Configuration Validation

```bash
# Validate your config
python audiomail_cli.py --validate-config

# Check GPU availability
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, MPS: {torch.backends.mps.is_available()}')"
```

## Common Issues

### Installation Problems

#### Issue: `ModuleNotFoundError`

```
ModuleNotFoundError: No module named 'audiomail'
```

**Solutions:**

1. **Verify virtual environment activation:**
   ```bash
   which python
   # Should show path to your .venv/bin/python
   ```

2. **Reinstall dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Check Python path:**
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

#### Issue: PyTorch Installation Fails

```
ERROR: Could not find a version that satisfies the requirement torch
```

**Solutions:**

1. **Install PyTorch manually:**
   ```bash
   # CPU version
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
   
   # CUDA version (replace cu118 with your CUDA version)
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

2. **Check Python version compatibility:**
   ```bash
   python --version  # Should be 3.10+
   ```

### Audio Recording Issues

#### Issue: No Microphone Detected

```
Error: No audio input devices found
```

**Solutions:**

1. **Check audio devices:**
   ```bash
   python -c "import sounddevice; print(sounddevice.query_devices())"
   ```

2. **Grant microphone permissions:**
   - **macOS**: System Preferences → Security & Privacy → Microphone
   - **Linux**: Check PulseAudio/ALSA configuration
   - **Windows**: Settings → Privacy → Microphone

3. **Test microphone:**
   ```bash
   # Record a test file
   python -c "
   import sounddevice as sd
   import scipy.io.wavfile as wav
   print('Recording for 3 seconds...')
   audio = sd.rec(3 * 44100, samplerate=44100, channels=1)
   sd.wait()
   wav.write('test.wav', 44100, audio)
   print('Test recording saved as test.wav')
   "
   ```

#### Issue: Silent or Noisy Recordings

```
Warning: Audio input appears to be silent
```

**Solutions:**

1. **Check microphone volume:**
   - Verify microphone is not muted
   - Increase input gain in system settings
   - Test with other applications

2. **Adjust audio settings in `config.ini`:**
   ```ini
   [audio]
   sample_rate = 44100
   channels = 1
   device_id = auto  # Try specific device ID
   ```

3. **Test different audio devices:**
   ```bash
   # List devices with IDs
   python -c "
   import sounddevice as sd
   devices = sd.query_devices()
   for i, device in enumerate(devices):
       if device['max_input_channels'] > 0:
           print(f'{i}: {device[\"name\"]}')
   "
   ```

### Model Loading Issues

#### Issue: CUDA Out of Memory

```
RuntimeError: CUDA out of memory
```

**Solutions:**

1. **Use smaller models in `config.ini`:**
   ```ini
   [whisper]
   model_size = tiny
   
   [llm]
   model_name = microsoft/DialoGPT-small
   ```

2. **Force CPU usage:**
   ```ini
   [whisper]
   device = cpu
   
   [llm]
   device = cpu
   ```

3. **Check GPU memory:**
   ```bash
   nvidia-smi  # Shows GPU memory usage
   ```

#### Issue: Model Download Fails

```
OSError: We couldn't connect to 'https://huggingface.co' to load this model
```

**Solutions:**

1. **Check internet connection:**
   ```bash
   curl -I https://huggingface.co
   ```

2. **Use offline mode with cached models:**
   ```bash
   export TRANSFORMERS_OFFLINE=1
   ```

3. **Download models manually:**
   ```bash
   python -c "
   from transformers import AutoModel
   AutoModel.from_pretrained('microsoft/DialoGPT-medium')
   "
   ```

### Performance Issues

#### Issue: Slow Transcription

**Solutions:**

1. **Use GPU acceleration:**
   ```ini
   [whisper]
   device = cuda  # or mps for Mac
   ```

2. **Use faster models:**
   ```ini
   [whisper]
   model_size = tiny
   fast_mode = true
   ```

3. **Optimize audio settings:**
   ```ini
   [audio]
   sample_rate = 22050  # Lower sample rate
   ```

#### Issue: Slow Email Generation

**Solutions:**

1. **Reduce token limit:**
   ```ini
   [generation]
   max_new_tokens = 128
   ```

2. **Use smaller language models:**
   ```ini
   [llm]
   model_name = microsoft/DialoGPT-small
   ```

3. **Disable sampling:**
   ```ini
   [generation]
   do_sample = false
   num_beams = 1
   ```

### Web UI Issues

#### Issue: Streamlit Won't Start

```
ModuleNotFoundError: No module named 'streamlit'
```

**Solutions:**

1. **Install Streamlit:**
   ```bash
   pip install streamlit
   ```

2. **Check port availability:**
   ```bash
   lsof -i :8501
   streamlit run audiomail_ui.py --server.port 8502
   ```

#### Issue: Recording Button Not Working

**Solutions:**

1. **Check browser permissions:**
   - Allow microphone access in browser
   - Try different browser (Chrome recommended)

2. **Refresh the page:**
   ```bash
   # Restart Streamlit
   Ctrl+C
   streamlit run audiomail_ui.py
   ```

### Email Quality Issues

#### Issue: Poor Transcription Quality

**Symptoms:**
- Incorrect words in transcription
- Missing parts of speech
- Garbled text

**Solutions:**

1. **Improve recording quality:**
   - Use a quiet environment
   - Speak clearly and at normal pace
   - Position microphone closer to mouth
   - Use a better microphone

2. **Use larger Whisper models:**
   ```ini
   [whisper]
   model_size = base  # or small, medium, large
   ```

3. **Specify language:**
   ```ini
   [whisper]
   language = en  # or your preferred language
   ```

#### Issue: Poor Email Quality

**Symptoms:**
- Awkward phrasing
- Missing key information
- Wrong tone

**Solutions:**

1. **Improve voice instructions:**
   - Be more specific about recipient and purpose
   - Include all necessary details
   - Speak in complete thoughts

2. **Use better language models:**
   ```ini
   [llm]
   model_name = microsoft/DialoGPT-large
   ```

3. **Adjust generation parameters:**
   ```ini
   [generation]
   temperature = 0.6  # More conservative
   max_new_tokens = 512  # Allow longer emails
   ```

## Advanced Troubleshooting

### Debug Mode

Enable detailed logging:

```bash
# Run with verbose output
python audiomail_cli.py --verbose

# Check log files
tail -f audiomail.log
```

### Memory Profiling

Monitor memory usage:

```bash
# Install memory profiler
pip install memory-profiler

# Profile memory usage
python -m memory_profiler audiomail_cli.py
```

### Performance Profiling

Identify bottlenecks:

```bash
# Install profiling tools
pip install cProfile

# Profile performance
python -m cProfile -o profile.prof audiomail_cli.py

# View profile results
python -c "
import pstats
p = pstats.Stats('profile.prof')
p.sort_stats('cumulative').print_stats(10)
"
```

### Network Issues

Debug connection problems:

```bash
# Test Hugging Face connectivity
curl -I https://huggingface.co/api/models/microsoft/DialoGPT-medium

# Check proxy settings
echo $HTTP_PROXY
echo $HTTPS_PROXY

# Test with different mirror
export HUGGINGFACE_HUB_URL="https://hf-mirror.com"
```

## System-Specific Issues

### macOS Issues

#### Issue: Microphone Permission Denied

**Solution:**
1. Go to System Preferences → Security & Privacy → Microphone
2. Add Terminal or your terminal app to allowed applications
3. Restart the terminal

#### Issue: Metal/MPS Not Working

**Solution:**
```bash
# Check MPS availability
python -c "import torch; print(torch.backends.mps.is_available())"

# Force MPS in config
[whisper]
device = mps
```

### Linux Issues

#### Issue: ALSA/PulseAudio Errors

**Solution:**
```bash
# Install audio development packages
sudo apt-get install libasound2-dev portaudio19-dev

# Test audio system
arecord -l  # List recording devices
pactl list sources  # List PulseAudio sources
```

#### Issue: CUDA Driver Version Mismatch

**Solution:**
```bash
# Check CUDA version
nvidia-smi
nvcc --version

# Install compatible PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Windows Issues

#### Issue: Audio Device Access

**Solution:**
1. Check Windows microphone privacy settings
2. Run as administrator if needed
3. Install Visual C++ Redistributable

#### Issue: Path Length Limits

**Solution:**
```powershell
# Enable long paths in Windows
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

## Getting Help

### Log Information Collection

When reporting issues, include:

1. **System information:**
   ```bash
   python --version
   pip list
   uname -a  # Linux/Mac
   ```

2. **AudioMail configuration:**
   ```bash
   cat config.ini
   ```

3. **Error logs:**
   ```bash
   tail -50 audiomail.log
   ```

### Community Resources

- **GitHub Issues**: [Report bugs and feature requests](https://github.com/sina5/audiomail/issues)
- **Discussions**: [Community support and questions](https://github.com/sina5/audiomail/discussions)

### Professional Support

For enterprise deployments or complex issues:
- Custom configuration assistance
- Performance optimization
- Integration support

## Prevention Tips

### Regular Maintenance

1. **Keep dependencies updated:**
   ```bash
   pip list --outdated
   pip install --upgrade -r requirements.txt
   ```

2. **Clean up cache periodically:**
   ```bash
   rm -rf ~/.cache/audiomail/
   rm -rf ~/.cache/huggingface/
   ```

3. **Monitor disk space:**
   ```bash
   du -sh ~/.cache/
   ```

### Best Practices

- **Test after updates**: Verify functionality after dependency updates
- **Backup configurations**: Save working `config.ini` files
- **Monitor resources**: Keep an eye on CPU, memory, and disk usage
- **Regular testing**: Periodically test all features to catch issues early