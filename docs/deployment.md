# Documentation Deployment

This guide explains how to deploy the AudioMail documentation to GitHub Pages.

## Automatic Deployment with GitHub Actions

1. Create `.github/workflows/docs.yml`:

```yaml
name: Deploy Documentation
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: '3.x'
    - run: pip install -r docs-requirements.txt
    - run: mkdocs gh-deploy --force
```

## Manual Deployment

1. **Install documentation dependencies:**
   ```bash
   pip install -r docs-requirements.txt
   ```

2. **Deploy to GitHub Pages:**
   ```bash
   mkdocs gh-deploy
   ```

This will build the documentation and push it to the `gh-pages` branch.

## Local Development

1. **Serve documentation locally:**
   ```bash
   mkdocs serve
   ```

2. **Build for production:**
   ```bash
   mkdocs build
   ```

The documentation will be available at `https://sina5.github.io/audiomail/`