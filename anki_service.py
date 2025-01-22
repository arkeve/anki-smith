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

def generate_anki_cards(text_passage, card_count=3):
    """Generate Anki cards from a text passage using OpenAI's API."""
    response = client.beta.chat.completions.parse(
        model="gpt-4o",  # or your specific model version
        messages=[
            {"role": "system", "content": f"Extract up to {card_count} Anki cards from the provided text."},
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