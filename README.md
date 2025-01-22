# Anki Card Generator

A tool designed to streamline the creation of Anki flashcards using the power of Large Language Models. This web application allows you to effortlessly generate high-quality flashcards from text passages and seamlessly upload them to your Anki account. By leveraging OpenAI's structured outputs, it intelligently suggests appropriate decks and tags based on your existing Anki configuration. Before finalizing, you can review and edit the generated cards to ensure they perfectly match your learning needs.

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