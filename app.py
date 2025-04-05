from flask import Flask, request, jsonify, render_template
import requests
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')

# Replace with your Ollama host endpoint
OLLAMA_ENDPOINT = "http://192.168.1.13:11434/api/chat"
OLLAMA_PS_ENDPOINT = "http://192.168.1.13:11434/api/tags"

@app.route('/')
def home():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    selected_model = request.json.get('model')

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Prepare the payload for the Ollama API
    payload = {
        "model": selected_model,
        "messages": [{"role": "user", "content": user_message}],
        "stream": False  # Ensure we receive the full response at once
    }

    try:
        logging.debug(f"Sending to Ollama: {payload}")
        response = requests.post(OLLAMA_ENDPOINT, json=payload, timeout=1200)
        response.raise_for_status()
        ollama_response = response.json()
        logging.debug(f"Received from Ollama: {ollama_response}")

        # Extract the assistant's message content
        assistant_message = ollama_response.get('message', {}).get('content', '').strip()
        if not assistant_message:
            raise ValueError("Received empty response from Ollama.")

    except requests.exceptions.RequestException as e:
        logging.error(f"RequestException: {e}")
        return jsonify({"error": "Ollama is currently unavailable. Please try again later."}), 500
    except ValueError as e:
        logging.error(f"ValueError: {e}")
        return jsonify({"error": str(e)}), 500

    return jsonify({"response": assistant_message})

@app.route('/models', methods=['GET'])
def get_models():
    try:
        response = requests.get(OLLAMA_PS_ENDPOINT, timeout=5)
        response.raise_for_status()
        models = response.json().get('models', [])
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch models from Ollama: {e}")
        return jsonify({"error": "Failed to fetch models from Ollama."}), 500

    return jsonify({"models": models})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3030, debug=True)
