# Anki Card Generator

A web application that generates Anki cards from text passages using OpenAI's API and integrates with Anki through AnkiConnect.

## Prerequisites

1. Install Rust (required for pydantic):
   - Windows: Download and run [rustup-init](https://win.rustup.rs/)
   - macOS/Linux: Run `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
   - After installation, restart your terminal

2. Install Python 3.8 or higher

## Setup

1. Install the required Python packages:
```bash
pip install -r requirements.txt
```

2. Install the AnkiConnect add-on in Anki:
   - Open Anki
   - Go to Tools > Add-ons > Get Add-ons
   - Enter code: `2055492159`
   - Restart Anki

3. Configure the environment:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key to the `.env` file
   - (Optional) Modify the AnkiConnect URL if needed

4. Start the application:
```bash
python app.py
```

5. Open your browser to `http://localhost:5000`

## Configuration

The application can be configured using environment variables:

- `OPENAI_API_KEY` (Required): Your OpenAI API key
- `ANKICONNECT_URL` (Optional): The URL of your AnkiConnect instance (defaults to `http://localhost:8765`)

## Troubleshooting

If you encounter installation errors:

1. Make sure Rust is properly installed:
```bash
rustc --version
```

2. If you still have issues with pydantic installation, try:
```bash
pip install --upgrade pip
pip install setuptools-rust
pip install -r requirements.txt
``` 