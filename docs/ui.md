# Web UI Guide

The AudioMail Web UI provides an intuitive, visual way to create emails from voice instructions. It's built with Streamlit and offers real-time feedback throughout the process.

## Starting the Web UI

Launch the web interface from your terminal:

```bash
streamlit run audiomail_ui.py
```

This will:
1. Start the Streamlit server
2. Automatically open your web browser
3. Navigate to `http://localhost:8501`

!!! tip "Custom Port"
    To use a different port:
    ```bash
    streamlit run audiomail_ui.py --server.port 8502
    ```

## Interface Overview

The Web UI is organized into clear sections:

### 1. Recording Section
- **Start Recording** button - Begin capturing audio
- **Stop Recording** button - End audio capture  
- **Audio playback** - Review what you recorded
- **Recording status** - Shows current state

### 2. Processing Section
- **Transcription display** - Shows what AudioMail heard
- **Email draft** - Generated email content
- **Processing status** - Shows current operation

### 3. Refinement Section
- **Record Feedback** button - Provide voice improvements
- **Stop Feedback** button - End feedback recording
- **Refinement history** - Track changes made

### 4. Control Section
- **Clear and Start Over** - Reset the entire session
- **Export Email** - Save or copy the final email

## Step-by-Step Workflow

### Step 1: Record Your Instructions

1. Click the **"Start Recording"** button
2. Speak your email instructions clearly
3. Click **"Stop Recording"** when finished

!!! example "Good Recording Practice"
    "I need to send an email to the marketing team about the upcoming product launch. Tell them the launch is scheduled for next month and we need to finalize the campaign materials by Friday. Ask them to review the attached mockups and provide feedback."

The interface will show:
- 🔴 Recording indicator while active
- ⏹️ Stop button to end recording
- 📊 Audio waveform visualization

### Step 2: Review Transcription

After recording, AudioMail will:
1. Process your audio file
2. Display the transcription
3. Show any confidence scores

If the transcription is incorrect:
- Click **"Clear and Start Over"**
- Try recording again with clearer speech
- Check your microphone settings

### Step 3: Review Generated Email

AudioMail creates a professional email draft:

```
Subject: Product Launch - Campaign Materials Due Friday

Hi Marketing Team,

I hope this email finds you well. I wanted to update you on our upcoming product launch, which is scheduled for next month.

We need to finalize all campaign materials by Friday to stay on schedule. Could you please review the attached mockups and provide your feedback?

Your input will be valuable in ensuring we have everything ready for the launch.

Best regards,
[Your name]
```

### Step 4: Refine (Optional)

If the email needs improvements:

1. Click **"Start Feedback Recording"**
2. Provide specific instructions for changes
3. Click **"Stop Feedback Recording"**

!!! example "Refinement Examples"
    - "Make the tone more urgent since Friday is a hard deadline"
    - "Add a bullet list of what materials we need feedback on"
    - "Include my phone number for quick questions"
    - "Change the subject to be more specific about the campaign type"

### Step 5: Export Your Email

When satisfied with the result:
1. Copy the email text
2. Paste into your email client
3. Add recipients and send

## Advanced Features

### Audio Playback

- **Play button** - Listen to your recorded instructions
- **Waveform display** - Visual representation of audio
- **Duration indicator** - Shows recording length

### Session Management

- **Session state** - Maintains context between recordings
- **History tracking** - See previous versions of your email
- **Auto-save** - Protects against accidental loss

### Real-time Status

The interface shows:
- 📝 "Transcribing..." during speech-to-text
- 🤖 "Generating email..." during AI processing  
- ✅ "Ready" when complete
- ❌ Error messages with helpful details

## Customization Options

### Theme and Appearance

Streamlit automatically adapts to your browser's dark/light mode preference.

### Layout Options

- **Wide mode**: Use browser's full width
- **Sidebar**: Collapse/expand for more space
- **Full screen**: Hide browser UI for focus

## Keyboard Shortcuts

While the focus is on the Streamlit app:

| Shortcut | Action |
|----------|--------|
| `r` | Start/stop recording |
| `c` | Clear session |
| `Esc` | Stop current operation |

## Troubleshooting Web UI

### Common Issues

!!! warning "Microphone Access"
    If recording doesn't work:
    1. Check browser permissions for microphone access
    2. Ensure microphone is not muted
    3. Try refreshing the page

!!! warning "Page Won't Load"
    If the UI doesn't start:
    ```bash
    # Check if port is already in use
    lsof -i :8501
    
    # Use different port
    streamlit run audiomail_ui.py --server.port 8502
    ```

!!! warning "Processing Stuck"
    If processing hangs:
    1. Check terminal for error messages
    2. Restart the Streamlit server
    3. Verify all dependencies are installed

### Performance Tips

- **Close unused tabs** to free memory
- **Use smaller models** in config.ini for faster processing
- **Record shorter clips** for quicker transcription
- **Check CPU/GPU usage** during processing

### Browser Compatibility

**Recommended browsers**:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Required features**:
- WebRTC for microphone access
- Modern JavaScript support
- WebAssembly support

## Integration Tips

### Email Clients

The generated emails work best with:
- **Gmail** - Copy and paste directly
- **Outlook** - Preserves formatting well
- **Apple Mail** - Good markdown support
- **Thunderbird** - Handles plain text well

### Workflow Integration

- **Use with calendar apps** for meeting follow-ups
- **Integrate with CRM** by copying to contact notes
- **Save templates** for repeated use cases
- **Export to documents** for record keeping

## Next Steps

- [Try the CLI interface](cli.md) for faster workflows
- [Configure settings](configuration.md) to optimize performance
- [Troubleshooting guide](troubleshooting.md) for common issues