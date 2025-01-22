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

def add_note(deck_name, front, back):
    """Add a note (card) to a specific deck."""
    note = {
        "deckName": deck_name,
        "modelName": "Basic",  # Use "Basic" model for simple front/back cards
        "fields": {
            "Front": front,
            "Back": back
        },
        "tags": [],
        "options": {
            "allowDuplicate": False
        }
    }
    invoke("addNote", {"note": note})

class AnkiCard(BaseModel):
    front: str
    back: str

    class Config:
        schema_extra = {
            "example": {
                "front": "What is matrix multiplication?",
                "back": "Matrix multiplication is an operation that combines two matrices to create a new matrix."
            }
        }

class AnkiDeck(BaseModel):
    deck: Literal["Probability", "Linear Algebra", "C++"]
    cards: List[AnkiCard]

    class Config:
        schema_extra = {
            "example": {
                "deck": "Linear Algebra",
                "cards": [
                    {
                        "front": "What is matrix multiplication?",
                        "back": "Matrix multiplication is an operation that combines two matrices to create a new matrix."
                    }
                ]
            }
        }

def generate_anki_cards(text_passage):
    """Generate Anki cards from a text passage using OpenAI's API."""
    response = client.beta.chat.completions.parse(
        model="gpt-4o",  # or your specific model version
        messages=[
            {"role": "system", "content": "Extract up to 3 Anki cards from the provided text."},
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