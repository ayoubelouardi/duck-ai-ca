# Duck AI CLI

A Python CLI tool for interacting with DuckDuckGo AI (reverse engineered API).

## Structure

```
duck-ai-cli/
├── src/
│   └── duckai/
│       ├── __init__.py
│       ├── client.py      # Core API client
│       ├── models.py      # Data models
│       └── utils.py       # Helper utilities
├── cli/
│   ├── __init__.py
│   └── main.py            # CLI entry point
├── tests/
│   └── __init__.py
├── requirements.txt       # Minimal dependencies
└── setup.py              # Package setup
```

## Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Install in editable mode
pip install -e .
```

## Usage

```bash
# Chat with AI
duckai chat "Your message here"

# Interactive mode
duckai interactive
```
