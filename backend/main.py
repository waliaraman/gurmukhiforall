from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sockets import Sockets
import os
import time
import json
import uuid

app = Flask(__name__)
CORS(app)
sockets = Sockets(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Placeholder Functions ---
def transcribe_audio_placeholder(audio_filepath, source="Unknown"):
    print(f"ASR Placeholder ({source}): Simulating transcription for {audio_filepath}...")
    time.sleep(0.5)
    gurmukhi_text = f"ਇਕ ਓਅੰਕਾਰ ਸਤਿ ਨਾਮੁ ({source} Stream)"
    print(f"ASR Placeholder: Simulated transcription: {gurmukhi_text}")
    return gurmukhi_text

def generate_embedding_placeholder(text, source="Unknown"): # Updated signature
    print(f"Embedding Placeholder ({source}): Simulating for text: '{text[:30]}...'")
    time.sleep(0.2) # Reduced delay
    dummy_embedding = [0.1, 0.2, 0.3, 0.4, 0.5, (source=="WebSocket")] # Varied output
    print(f"Embedding Placeholder ({source}): Generated dummy: {dummy_embedding}")
    return dummy_embedding

def search_similar_verse_placeholder(embedding, source="Unknown"): # Updated signature
    print(f"Search Placeholder ({source}): Simulating search with embedding: {embedding}")
    time.sleep(0.5) # Reduced delay

    verse_text = f"ਸਲੋਕੁ ਮਃ ੩ ॥ ({source} Placeholder Verse)" # Modified content
    meaning_text = f"Shalok, Third Mehl ({source} Placeholder Meaning)" # Modified content
    page_num = f"Ang 644 ({source} Placeholder Page)" # Modified content

    found_verse = {
        "verse_gurmukhi": verse_text,
        "meaning_english": meaning_text,
        "source_page": page_num
    }
    print(f"Search Placeholder ({source}): Found dummy verse: {found_verse['verse_gurmukhi']}")
    return found_verse

# --- HTTP Routes ---
@app.route('/')
def home():
    return "Backend is running (HTTP)!"

@app.route('/api/audio', methods=['POST'])
def process_audio_http():
    if 'audio_file' not in request.files:
        return jsonify({"message": "No audio file part"}), 400
    file = request.files['audio_file']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400
    if file:
        filename = f"recording_{int(time.time())}.webm"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(filepath)
            print(f"File saved to {filepath}")

            transcribed_text = transcribe_audio_placeholder(filepath, source="HTTP POST") # Pass source
            embedding = generate_embedding_placeholder(transcribed_text, source="HTTP POST") # Pass source
            found_verse_data = search_similar_verse_placeholder(embedding, source="HTTP POST") # Pass source

            return jsonify({
                "message": "Audio received, saved, and processed (placeholders).",
                "filename": filename,
                "transcribed_text": transcribed_text,
                "generated_embedding": embedding,
                "found_verse": found_verse_data
            }), 200
        except Exception as e:
            print(f"Error processing file: {e}")
            return jsonify({"message": "Error processing file", "error": str(e)}), 500
    return jsonify({"message": "Unknown error"}), 500

# --- WebSocket Route ---
@sockets.route('/api/audio_stream')
def audio_stream_socket(ws):
    print("WebSocket connection established for streaming ASR.")
    audio_buffer = []
    CHUNKS_TO_ACCUMULATE = 3

    while not ws.closed:
        message = ws.receive()
        if message is None:
            print("WebSocket (audio_stream_socket): Client sent None or closed.")
            break

        if isinstance(message, bytes):
            audio_buffer.append(message)

            if len(audio_buffer) >= CHUNKS_TO_ACCUMULATE:
                temp_filename = f"temp_stream_audio_{uuid.uuid4()}.webm"
                temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)

                try:
                    with open(temp_filepath, 'wb') as f:
                        for chunk in audio_buffer:
                            f.write(chunk)

                    # 1. ASR Placeholder
                    transcribed_text = transcribe_audio_placeholder(temp_filepath, source="WebSocket")
                    ws.send(json.dumps({
                        "type": "transcription_update",
                        "text": transcribed_text
                    }))

                    # 2. Embedding Placeholder
                    embedding = generate_embedding_placeholder(transcribed_text, source="WebSocket")
                    # Optionally send embedding for debugging on client if needed:
                    # ws.send(json.dumps({"type": "embedding_update", "embedding": embedding, "source": "WebSocket"}))

                    # 3. Search Placeholder
                    found_verse_data = search_similar_verse_placeholder(embedding, source="WebSocket")
                    ws.send(json.dumps({
                        "type": "verse_update",
                        "data": found_verse_data,
                        "source": "WebSocket"
                    }))
                    # print(f"WebSocket: Sent verse data: {found_verse_data['verse_gurmukhi']}")

                except Exception as e:
                    print(f"WebSocket (audio_stream_socket): Error during ASR/Embedding/Search processing: {e}")
                    try:
                        ws.send(json.dumps({"type": "error", "message": "Error processing audio stream"}))
                    except Exception as ws_send_e:
                        print(f"WebSocket (audio_stream_socket): Failed to send error to client: {ws_send_e}")
                finally:
                    if os.path.exists(temp_filepath):
                        os.remove(temp_filepath)
                    audio_buffer = []
        elif isinstance(message, str):
            print(f"WebSocket (audio_stream_socket): Received text message: {message}")
            try:
                msg_json = json.loads(message)
                if msg_json.get("action") == "stop":
                    print("WebSocket (audio_stream_socket): Received stop signal from client.")
            except json.JSONDecodeError:
                print(f"WebSocket (audio_stream_socket): Text message is not valid JSON: {message}")
        else:
            print(f"WebSocket (audio_stream_socket): Received unexpected message type ({type(message)}), ignoring.")

    print("WebSocket (audio_stream_socket): Connection closed.")

# --- Main Execution ---
if __name__ == '__main__':
    print("Starting Flask development server for HTTP routes on port 5001.")
    print("NOTE: WebSockets defined at /api/audio_stream WILL NOT WORK with this dev server.")
    print("Use 'gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 main:app -b 0.0.0.0:5001' for WebSocket support.")
    app.run(debug=True, port=5001, host='0.0.0.0')
