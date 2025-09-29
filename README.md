# AudioMail 🎙️✉️

AudioMail is an AI-powered tool that converts your voice instructions into professionally drafted emails. It uses local, high-performance models for transcription and generation, ensuring privacy and speed. The tool is accessible through both a command-line interface (CLI) and a user-friendly web UI.

## Features

- **Voice-to-Email**: Record your thoughts, and AudioMail will draft a polished email.
- **Iterative Refinement**: Provide voice feedback to improve the email draft until it's perfect.
- **Local & Private**: All processing is done on your machine, keeping your data secure.
- **Hardware Accelerated**: Automatically uses Metal (on Apple Silicon), CUDA (on NVIDIA), or CPU for optimal performance.
- **Dual Interfaces**: Choose between a CLI for quick tasks or a Streamlit-based web UI for a more interactive experience.
- **Configurable**: Easily customize settings like model sizes, audio parameters, and generation settings via a `config.ini` file.

## Requirements

- Python 3.10+
- A working microphone
- `uv` for fast dependency management (recommended)
- For GPU acceleration:
  - **NVIDIA**: CUDA toolkit installed
  - **Apple Silicon**: No special setup needed

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/sina5/audiomail.git
    cd audiomail
    ```

2.  **Create and activate a virtual environment:**
    Using `uv`:
    ```bash
    uv venv
    source .venv/bin/activate  # On macOS/Linux
    # .venv\Scripts\activate  # On Windows
    ```
    Or using `venv`:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    Using `uv`:
    ```bash
    uv pip install -r requirements.txt
    ```
    Or using `pip`:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

You can run AudioMail using either the web UI or the CLI.

### Web UI (Recommended)

The web UI provides an intuitive, visual way to interact with AudioMail.

**To start the web UI:**
```bash
streamlit run audiomail_ui.py
```

**Features:**
- Simple "Start" and "Stop" recording buttons.
- Displays the audio recording, transcription, and email draft.
- Allows for voice-based feedback and refinement.
- "Clear and Start Over" button to reset the session.

### Command-Line Interface (CLI)

The CLI is perfect for quick, terminal-based workflows.

**To run the CLI:**
```bash
python audiomail_cli.py
```

**Workflow:**
1.  Follow the prompt to start recording.
2.  Speak your email instructions clearly.
3.  Press `s` to stop recording.
4.  The system will transcribe your audio and generate a draft.
5.  You will be asked if you want to refine the email. Answer `yes` to provide voice feedback or `no` to finish.

## Configuration

AudioMail can be configured by editing the `config.ini` file. This file allows you to control various aspects of the application.

-   **[audio]**: Settings for `sample_rate` and `channels`.
-   **[whisper]**: `model_size` (e.g., `tiny`, `base`, `small`) and `device` (`auto`, `cpu`, `cuda`).
-   **[llm]**: `model_name` (from Hugging Face), `device`, and `torch_dtype`.
-   **[generation]**: Parameters like `max_new_tokens`, `temperature`, and `top_p`.
-   **[paths]**: Directory for saving recordings (`recordings_dir`).

The system will automatically create a default `config.ini` if one doesn't exist.

## Project Structure

```
.
├── audiomail_cli.py      # Command-line interface
├── audiomail_ui.py       # Streamlit web interface
├── config.ini            # Configuration file
├── nodes.py              # Core logic for recording, transcription, and generation
├── README.md             # This file
├── requirements.txt      # Python dependencies
└── recordings/           # Directory for saved audio files
```

## Troubleshooting

-   **No input devices found**: Make sure your microphone is connected and has the correct permissions.
-   **Recording is silent**: Check your microphone volume and ensure it's not muted.
-   **Errors during model loading**: You may not have enough RAM or VRAM for the selected models. Try using smaller models (e.g., `tiny` for Whisper) in `config.ini`.
-   **`uv` command not found**: Ensure `uv` is installed (`pip install uv`). If you prefer not to use it, standard `venv` and `pip` work just as well.

## Documentation

Comprehensive documentation is available using MkDocs with a beautiful dark theme:

### Building Documentation

1. **Install documentation dependencies:**
   ```bash
   pip install -r docs-requirements.txt
   ```

2. **Build and serve documentation locally:**
   ```bash
   mkdocs serve
   ```
   
   This will start a local server at `http://localhost:8000` with live reload.

3. **Build static documentation:**
   ```bash
   mkdocs build
   ```
   
   The documentation will be generated in the `site/` directory.

The documentation includes:
- **Installation Guide** - Step-by-step setup instructions
- **Usage Guide** - How to use both CLI and Web UI
- **Configuration** - Detailed configuration options
- **Troubleshooting** - Solutions to common issues

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for more details.
