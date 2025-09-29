# Command Line Interface

The AudioMail CLI provides a fast, keyboard-driven workflow perfect for power users, automation, and integration with other tools.

## Starting the CLI

Launch AudioMail from your terminal:

```bash
python audiomail_cli.py
```

The CLI will initialize and show:
- Configuration loading status
- Model initialization progress
- Ready prompt for recording

## CLI Workflow

### Basic Commands

The CLI uses single-key commands for efficiency:

| Key | Action |
|-----|--------|
| `s` | **S**top recording |
| `y` | **Y**es, refine the email |
| `n` | **N**o, finish with current email |
| `Enter` | Start recording |
| `Ctrl+C` | Exit application |

### Step-by-Step Process

#### 1. Start Recording

```
AudioMail CLI - Voice to Email Agent
===================================

Press Enter to start recording your email instructions...
```

Press **Enter** to begin recording.

#### 2. Record Instructions

```
🎤 Recording... (press 's' to stop)
```

Speak your email instructions clearly. The CLI shows:
- 🎤 Recording indicator
- Real-time audio level meter (optional)
- Instructions to stop

#### 3. Stop Recording

Press **`s`** to stop recording:

```
⏹️ Recording stopped. Processing...
```

#### 4. View Transcription

```
📝 Transcription:
"Send an email to the development team about the code review meeting. 
Tell them it's scheduled for Thursday at 3 PM in the conference room. 
Ask them to prepare their recent commits for discussion."
```

#### 5. View Generated Email

```
📧 Generated Email:
─────────────────────────────────────

Subject: Code Review Meeting - Thursday 3 PM

Hi Development Team,

I hope this email finds you well. I wanted to inform you about our upcoming code review meeting scheduled for Thursday at 3 PM in the conference room.

Please prepare your recent commits for discussion during the meeting. This will help us have a productive session and ensure we cover all the important changes.

Looking forward to seeing you there.

Best regards,
[Your name]

─────────────────────────────────────
```

#### 6. Refinement Option

```
Would you like to refine this email? (y/n): 
```

- Type **`y`** to provide voice feedback for improvements
- Type **`n`** to finish with the current email

#### 7. Voice Refinement (if selected)

```
🎤 Recording feedback... (press 's' to stop)
Speak your refinement instructions:
```

Provide specific feedback, then press **`s`** to stop.

#### 8. Final Email

```
📧 Final Email:
─────────────────────────────────────

Subject: Code Review Meeting - Thursday 3 PM (Conference Room B)

Hi Development Team,

I wanted to inform you about our upcoming code review meeting scheduled for Thursday at 3 PM in Conference Room B.

Please prepare your recent commits for discussion:
• Bug fixes from the last sprint
• New feature implementations  
• Any performance improvements

This will help us have a focused and productive session.

Best regards,
[Your name]

─────────────────────────────────────

Email generation complete! 
Copy the email above to your email client.
```

## Advanced CLI Features

### Command Line Arguments

```bash
# Show help
python audiomail_cli.py --help

# Use custom config file
python audiomail_cli.py --config custom_config.ini

# Verbose output for debugging
python audiomail_cli.py --verbose

# Save audio recordings
python audiomail_cli.py --save-audio

# Specify output format
python audiomail_cli.py --output json
```

### Output Formats

#### Plain Text (Default)
```bash
python audiomail_cli.py
```
Human-readable format with formatting.

#### JSON Output
```bash
python audiomail_cli.py --output json
```
Structured data for integration:
```json
{
  "transcription": "Send email to team...",
  "email": {
    "subject": "Code Review Meeting",
    "body": "Hi Development Team...",
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "refinements": 1
}
```

#### Markdown Output
```bash
python audiomail_cli.py --output markdown
```
Markdown-formatted email for documentation.

### Batch Processing

Process multiple recordings:

```bash
# Process all WAV files in a directory
python audiomail_cli.py --batch recordings/*.wav

# Process with custom output directory
python audiomail_cli.py --batch *.wav --output-dir ./emails/
```

### Integration with Other Tools

#### Pipe to Email Client
```bash
python audiomail_cli.py --output plain | mail -s "$(grep Subject: | cut -d: -f2)" recipient@example.com
```

#### Save to File
```bash
python audiomail_cli.py --output markdown > draft_email.md
```

#### Integration with Scripts
```bash
#!/bin/bash
EMAIL=$(python audiomail_cli.py --output json)
SUBJECT=$(echo $EMAIL | jq -r '.email.subject')
BODY=$(echo $EMAIL | jq -r '.email.body')
# Process further...
```

## Configuration for CLI

### Command-Line Config Override

```bash
# Use smaller model for faster processing
python audiomail_cli.py --whisper-model tiny --llm-model microsoft/DialoGPT-small

# Force CPU usage
python audiomail_cli.py --device cpu

# Adjust generation parameters
python audiomail_cli.py --temperature 0.5 --max-tokens 256
```

### Environment Variables

Set environment variables for consistent behavior:

```bash
export AUDIOMAIL_CONFIG="/path/to/config.ini"
export AUDIOMAIL_DEVICE="cuda"
export AUDIOMAIL_WHISPER_MODEL="base"
export AUDIOMAIL_SAVE_RECORDINGS="true"

python audiomail_cli.py
```

## Automation Examples

### Daily Standup Emails

```bash
#!/bin/bash
# daily_standup.sh

echo "Recording daily standup email..."
python audiomail_cli.py --output json > standup_$(date +%Y%m%d).json

# Extract and send
SUBJECT=$(jq -r '.email.subject' standup_$(date +%Y%m%d).json)
BODY=$(jq -r '.email.body' standup_$(date +%Y%m%d).json)

mail -s "$SUBJECT" team@company.com <<< "$BODY"
```

### Meeting Follow-ups

```bash
#!/bin/bash
# meeting_followup.sh

if [ "$1" = "record" ]; then
    python audiomail_cli.py --save-audio --output json > followup.json
    echo "Follow-up recorded and saved to followup.json"
elif [ "$1" = "send" ]; then
    # Process and send the follow-up
    RECIPIENTS=$(jq -r '.recipients[]' followup.json)
    SUBJECT=$(jq -r '.email.subject' followup.json)
    BODY=$(jq -r '.email.body' followup.json)
    
    for recipient in $RECIPIENTS; do
        mail -s "$SUBJECT" "$recipient" <<< "$BODY"
    done
fi
```

## Troubleshooting CLI

### Common Issues

!!! warning "Audio Device Not Found"
    ```bash
    # List available audio devices
    python -c "import sounddevice; print(sounddevice.query_devices())"
    
    # Specify device in config.ini
    [audio]
    device_id = 1
    ```

!!! warning "Keyboard Interrupt Handling"
    If Ctrl+C doesn't work properly:
    ```bash
    # Kill process by name
    pkill -f audiomail_cli.py
    
    # Or find and kill by PID
    ps aux | grep audiomail_cli.py
    kill <PID>
    ```

!!! warning "Model Loading Errors"
    ```bash
    # Run with verbose output to see detailed errors
    python audiomail_cli.py --verbose
    
    # Check available memory
    free -h
    
    # Use smaller models
    python audiomail_cli.py --whisper-model tiny
    ```

### Performance Optimization

#### For Speed
```bash
# Fastest settings
python audiomail_cli.py \
  --whisper-model tiny \
  --device cpu \
  --max-tokens 128 \
  --temperature 0.1
```

#### For Quality
```bash
# Best quality settings
python audiomail_cli.py \
  --whisper-model large \
  --device cuda \
  --max-tokens 512 \
  --temperature 0.7
```

#### For Low Memory
```bash
# Memory-efficient settings
python audiomail_cli.py \
  --whisper-model base \
  --device cpu \
  --max-tokens 256
```

## Keyboard Shortcuts and Tips

### Efficient Recording
- **Quick start**: Press Enter immediately when ready
- **Clean stops**: Wait for a pause before pressing 's'
- **Background noise**: Record in quiet environments

### Fast Refinement
- **Be specific**: "Make it more formal" vs "change the tone"
- **Multiple changes**: Record all changes in one refinement session
- **Context**: Reference specific parts: "in the second paragraph..."

### Workflow Tips
- **Prepare notes**: Outline key points before recording
- **Practice**: Try a few emails to learn the optimal speaking style
- **Templates**: Develop verbal templates for common email types

## Next Steps

- [Configure AudioMail](configuration.md) for optimal CLI performance
- [Web UI Guide](ui.md) for visual alternative
- [Troubleshooting](troubleshooting.md) for detailed problem solving