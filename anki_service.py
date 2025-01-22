from openai import OpenAI
import os
import requests
from typing import Literal, List
from pydantic import BaseModel
from dotenv import load_dotenv

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
        "modelName": "Basic",  # Use "Basic" model for simple front/back cards
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

class AnkiCard(BaseModel):
    front: str
    back: str
    tags: List[str]

class AnkiDeck(BaseModel):
    deck: str
    cards: List[AnkiCard]

def get_all_tags():
    """Get all existing tags from Anki."""
    response = invoke("getTags")
    return response.get("result", [])

def generate_anki_cards(text_passage):
    """Generate Anki cards from a text passage using OpenAI's API."""
    # Get available tags and decks to inform the model
    available_tags = get_all_tags()
    available_decks = get_all_decks()
    system_message = f"""Extract up to 3 Anki cards from the provided text.
Available decks: {', '.join(available_decks)}
Available tags: {', '.join(available_tags)}
Please use appropriate tags from the available list for each card and select an appropriate deck from the available decks."""

    response = client.beta.chat.completions.parse(
        model="gpt-4o",  # or your specific model version
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": text_passage}
        ],
        response_format=AnkiDeck,
    )
    return response.choices[0].message.parsed

# Example usage
if __name__ == "__main__":
    text_passage = "linear algebra matrix multiplication"
    structured_output = generate_anki_cards(text_passage)
    
    deck_name = structured_output.deck
    create_deck(deck_name)
    
    for card in structured_output.cards:
        add_note(deck_name, card.front, card.back)
    
    print("Cards added successfully!")