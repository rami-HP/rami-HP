# Rami HP Project

This repository includes a small script that calls the OpenAI API. It is configured to run on GitHub Actions using Python 3.11.

Requirements
- Python 3.11
- Install dependencies: pip install -r requirements.txt

Set OPENAI_API_KEY (GitHub Actions)
- Via the web UI:
  Settings → Secrets and variables → Actions → New repository secret
  Name: OPENAI_API_KEY
  Value: <your OpenAI API key from openai.com>

- Or via GitHub CLI:
  gh secret set OPENAI_API_KEY --body "sk-..." --repo rami-HP/rami-HP

Usage (local)
- Linux / macOS:
  export OPENAI_API_KEY="sk-..."
  python custom/key_id/model_id.py

Notes
- The GitHub Actions workflow (.github/workflows/ci.yml) runs Python 3.11 and executes custom/key_id/model_id.py using the OPENAI_API_KEY secret.
- Do NOT commit your API key into the repository.