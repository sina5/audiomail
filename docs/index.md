# AudioMail 🎙️✉️

AudioMail is an AI-powered tool that converts your voice instructions into professionally drafted emails. It uses local, high-performance models for transcription and generation, ensuring privacy and speed.

## Key Features

- **🎤 Voice-to-Email**: Record your thoughts, and AudioMail will draft a polished email
- **🔄 Iterative Refinement**: Provide voice feedback to improve the email draft until it's perfect
- **🔒 Local & Private**: All processing is done on your machine, keeping your data secure
- **⚡ Hardware Accelerated**: Automatically uses Metal (on Apple Silicon), CUDA (on NVIDIA), or CPU for optimal performance
- **🖥️ Dual Interfaces**: Choose between a CLI for quick tasks or a Streamlit-based web UI for a more interactive experience
- **⚙️ Configurable**: Easily customize settings like model sizes, audio parameters, and generation settings

## Quick Start

1. **[Install AudioMail](installation.md)** - Set up the environment and dependencies
2. **[Run the Web UI](ui.md)** - Use the intuitive Streamlit interface  
3. **[Try the CLI](cli.md)** - Quick terminal-based workflow
4. **[Configure Settings](configuration.md)** - Customize models and parameters

## How It Works

AudioMail processes your voice input through several steps:

1. **Audio Recording** - Captures your voice using your system microphone
2. **Speech-to-Text** - Uses Whisper models for accurate transcription
3. **Email Generation** - Leverages large language models to create professional emails
4. **Refinement** - Allows iterative improvements through voice feedback

!!! info "Privacy First"
    AudioMail runs entirely on your local machine. No data is sent to external servers, ensuring your conversations and emails remain private.

## Requirements

- Python 3.10+
- A working microphone
- For GPU acceleration:
  - **NVIDIA**: CUDA toolkit installed
  - **Apple Silicon**: No special setup needed

## Project Structure

```
audiomail/
├── audiomail_cli.py      # Command-line interface
├── audiomail_ui.py       # Streamlit web interface
├── config.ini            # Configuration file
├── audiomail/            # Core package
│   ├── nodes.py          # Core logic for recording, transcription, and generation
│   ├── state.py          # Application state management
│   └── utils.py          # Utility functions
├── docs/                 # Documentation (this site)
└── requirements.txt      # Python dependencies
```

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](https://github.com/sina5/audiomail/blob/main/LICENSE) file for more details.