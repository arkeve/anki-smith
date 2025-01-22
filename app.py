from flask import Flask, render_template, request, jsonify
from anki_service import generate_anki_cards, create_deck, add_note

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    text_passage = request.json.get('text')
    try:
        structured_output = generate_anki_cards(text_passage)
        cards = [{"front": card.front, "back": card.back} for card in structured_output.cards]
        return jsonify({
            "success": True,
            "deck": structured_output.deck,
            "cards": cards
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/save-cards', methods=['POST'])
def save_cards():
    data = request.json
    deck_name = data.get('deck')
    cards = data.get('cards', [])
    
    try:
        create_deck(deck_name)
        for card in cards:
            add_note(deck_name, card['front'], card['back'])
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(debug=True) 