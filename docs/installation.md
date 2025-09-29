# Installation

This guide will help you set up AudioMail on your system.

## Requirements

Before installing AudioMail, make sure you have:

- **Python 3.10+**
- **A working microphone**
- **uv** for fast dependency management (recommended)

For **GPU acceleration** (optional but recommended):

=== "NVIDIA GPUs"
    - CUDA toolkit installed
    - Compatible NVIDIA GPU with CUDA support

=== "Apple Silicon"
    - No special setup needed
    - Metal acceleration works out of the box

=== "CPU Only"
    - Works on any system
    - Slower processing but still functional

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/sina5/audiomail.git
cd audiomail
```

### 2. Create Virtual Environment

You can use either `uv` (recommended) or standard Python `venv`:

=== "Using uv (Recommended)"
    ```bash
    # Install uv if not already installed
    pip install uv
    
    # Create and activate virtual environment
    uv venv
    source .venv/bin/activate  # On macOS/Linux
    # .venv\Scripts\activate    # On Windows
    ```

=== "Using venv"
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On macOS/Linux
    # .venv\Scripts\activate    # On Windows
    ```

### 3. Install Dependencies

=== "Using uv"
    ```bash
    uv pip install -r requirements.txt
    ```

=== "Using pip"
    ```bash
    pip install -r requirements.txt
    ```

!!! tip "Installation Time"
    The first installation may take several minutes as it downloads PyTorch and other large dependencies. GPU versions of PyTorch are particularly large.

## Verify Installation

After installation, verify that AudioMail is working:

### Test CLI
```bash
python audiomail_cli.py --help
```

### Test Web UI
```bash
streamlit run audiomail_ui.py
```

This should open your web browser to `http://localhost:8501` with the AudioMail interface.

## GPU Setup

### NVIDIA CUDA Setup

1. **Install CUDA Toolkit**: Download from [NVIDIA's official site](https://developer.nvidia.com/cuda-downloads)
2. **Verify CUDA installation**:
   ```bash
   nvidia-smi
   nvcc --version
   ```
3. **Test GPU support**:
   ```python
   import torch
   print(torch.cuda.is_available())  # Should return True
   ```

### Apple Silicon Setup

Metal acceleration works automatically on Apple Silicon Macs. No additional setup required.

## Troubleshooting Installation

### Common Issues

!!! warning "Permission Errors"
    If you get permission errors during installation:
    ```bash
    pip install --user -r requirements.txt
    ```

!!! warning "PyTorch Installation Issues"
    If PyTorch installation fails, visit [pytorch.org](https://pytorch.org/get-started/locally/) for platform-specific installation instructions.

!!! warning "Microphone Access"
    Make sure your system has microphone permissions enabled for the terminal or application you're running AudioMail from.

### Dependency Conflicts

If you encounter dependency conflicts:

1. **Create a fresh virtual environment**:
   ```bash
   rm -rf .venv
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies one by one**:
   ```bash
   pip install torch
   pip install transformers
   pip install -r requirements.txt
   ```

### Memory Requirements

**Minimum RAM**: 4GB  
**Recommended RAM**: 8GB or more  
**GPU VRAM**: 2GB for small models, 4GB+ for larger models

If you have limited memory, edit `config.ini` to use smaller models:
```ini
[whisper]
model_size = tiny

[llm]
model_name = microsoft/DialoGPT-small
```

## Next Steps

Once installation is complete, continue to:

- [Usage Guide](usage.md) - Learn the basics
- [Web UI Guide](ui.md) - Use the visual interface
- [CLI Guide](cli.md) - Use the command line
- [Configuration](configuration.md) - Customize settings