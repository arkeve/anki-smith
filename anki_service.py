from openai import OpenAI
import os
import requests
from typing import Literal, List
from pydantic import BaseModel
from dotenv import load_dotenv
from enum import Enum

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables with defaults
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANKICONNECT_URL = os.getenv('ANKICONNECT_URL', 'http://localhost:8765')

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

client = OpenAI(api_key=OPENAI_API_KEY)

def invoke(action, params=None):
    """Send a request to the AnkiConnect API."""
    params = params if params else {}
    response = requests.post(ANKICONNECT_URL, json={
        "action": action,
        "version": 6,
        "params": params
    })
    response.raise_for_status()
    return response.json()

def create_deck(deck_name):
    """Create a new deck."""
    invoke("createDeck", {"deck": deck_name})

def add_note(deck_name, front, back, tags=None):
    """Add a note (card) to a specific deck."""
    note = {
        "deckName": deck_name,
        "modelName": "KaTeX and Markdown Basic (Color)",
        "fields": {
            "Front": front,
            "Back": back
        },
        "tags": tags or [],
        "options": {
            "allowDuplicate": False
        }
    }
    invoke("addNote", {"note": note})

def get_all_decks():
    """Get all existing decks from Anki."""
    response = invoke("deckNames")
    return response.get("result", [])

def get_all_tags():
    """Get all existing tags from Anki."""
    response = invoke("getTags")
    return response.get("result", [])

# Dynamically create Enum classes
TagEnum = Enum('TagEnum', {tag.replace(" ", "_"): tag for tag in get_all_tags()})
DeckEnum = Enum('DeckEnum', {deck.replace(" ", "_"): deck for deck in get_all_decks()})

class AnkiCard(BaseModel):
    front: str
    back: str
    tags: List[TagEnum]
    class Config:
        use_enum_values = True

class AnkiDeck(BaseModel):
    deck: DeckEnum
    cards: List[AnkiCard]
    class Config:
        use_enum_values = True

def generate_anki_cards(text_passage, card_count=1):
    """Generate Anki cards from a text passage using OpenAI's API."""
    response = client.beta.chat.completions.parse(
        model="gpt-4o",  # or your specific model version
        messages=[
            {"role": "system", "content": f"""Extract up to {card_count} Anki cards from the provided text.

Format your responses using:
1. KaTeX for mathematical expressions:
   - Use $...$ for inline math (e.g. $x^2$)
   - Use $$...$$ for display math (e.g. $$\\begin{{matrix}} a & b \\\\ c & d \\end{{matrix}}$$)
2. Matrix examples:
   - Inline matrix: $\\begin{{pmatrix}} 1 & 2 \\\\ 3 & 4 \\end{{pmatrix}}$
   - Display matrix: $$\\begin{{pmatrix}} 1 & 2 \\\\ 3 & 4 \\end{{pmatrix}}$$
   - Matrix multiplication: If $A = \\begin{{pmatrix}} 1 & 2 \\\\ 3 & 4 \\end{{pmatrix}}$ and $B = \\begin{{pmatrix}} 5 & 6 \\\\ 7 & 8 \\end{{pmatrix}}$,
     then $$C = A \\times B = \\begin{{pmatrix}} 19 & 22 \\\\ 43 & 50 \\end{{pmatrix}}$$
3. Markdown for:
   - Code blocks with language specification (e.g. ```python)
   - Lists, tables, and other formatting
4. Guidelines:
   - Always wrap math expressions in $ or $$ delimiters
   - Always wrap matrices in $ or $$ delimiters
   - Format code snippets in appropriate language blocks
   - Use proper markdown for lists and tables
   - Ensure proper escaping of special characters"""},
            {"role": "user", "content": text_passage}
        ],
        response_format=AnkiDeck,
    )
    return response.choices[0].message.parsed

# Example usage
if __name__ == "__main__":
    text_passage = "linear algebra matrix multiplication"
    structured_output = generate_anki_cards(text_passage)
    
    deck_name = structured_output.deck.value  # Get the actual deck name from the enum
    create_deck(deck_name)
    
    for card in structured_output.cards:
        add_note(deck_name, card.front, card.back, [tag.value for tag in card.tags])  # Convert enum tags to strings
    
    print("Cards added successfully!")