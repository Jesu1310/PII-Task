import spacy
from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")  # Load the spaCy English model

def detect_pii(text):
    doc = nlp(text)

    pii_patterns = {
        'name': r'\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b',
        #'aadhaar': r'\b(\d{12})\b',
        'passport': r'\b([A-Z]{3}\d{9})\b',
        #'mobile': r'\b(\d{10})\b',
    }

    pii_detected = []

    current_entity_type = None
    current_entity_value = ""

    for entity in doc.ents:
        entity_type = entity.label_
        entity_value = entity.text

        if entity_type in ["PERSON", "ORG"]:
            # Consecutive entities of the same type are considered part of the same value
            if current_entity_type == entity_type:
                current_entity_value += " " + entity_value
            else:
                # Start a new value
                #if current_entity_type is not None:
                    #pii_detected.append({"pii_type": "name", "pii_value": current_entity_value.strip()})
                current_entity_type = entity_type
                current_entity_value = entity_value
        elif len(entity_value) == 10:
            pii_detected.append({"pii_type": "mobile", "pii_value": entity_value})
        elif len(entity_value) == 12:
            pii_detected.append({"pii_type": "aadhaar", "pii_value": entity_value})

    for pii_type, pattern in pii_patterns.items():
            matches = re.findall(pattern, text)
            for match in matches:
                if pii_type == 'name':
                    pii_detected.append({'pii_type': pii_type.capitalize(), 'pii_value': f'{match[0]} {match[1]}'})
                else:
                    pii_detected.append({'pii_type': pii_type.capitalize(), 'pii_value': match})

    # Add the last entity value if any
    #if current_entity_type is not None:
     #   pii_detected.append({"pii_type": "name", "pii_value": current_entity_value.strip()})

    return pii_detected


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def back_home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_text():
    try:
        data = request.get_json()
        if 'body' not in data:
            raise ValueError("Missing 'body' in the request")

        text = data['body']
        pii_detected = detect_pii(text)

        response = {'pii_detected': pii_detected, 'error': None}
        return jsonify(response)

    except Exception as e:
        response = {'pii_detected': [], 'error': str(e)}
        return jsonify(response)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8800, debug=True)
