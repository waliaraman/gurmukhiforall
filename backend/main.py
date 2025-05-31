from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import time
import json
import uuid

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, async_mode='gevent', cors_allowed_origins="*")

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Updated Placeholder Functions ---
def transcribe_audio_placeholder(audio_filepath, source="Unknown"):
    print(f"ASR Placeholder ({source}): Simulating transcription for {audio_filepath}...")
    time.sleep(0.5)
    gurmukhi_text = f"ਇਕ ਓਅੰਕਾਰ ਸਤਿ ਨਾਮੁ ({source} Stream via Socket.IO)" # Updated
    print(f"ASR Placeholder: Simulated transcription: {gurmukhi_text}")
    return gurmukhi_text

def generate_embedding_placeholder(text, source="Unknown"):
    print(f"Embedding Placeholder ({source}): Simulating for text: '{text[:30]}...'")
    time.sleep(0.2)
    dummy_embedding = [0.1, 0.2, 0.3, 0.4, 0.5, (source=="SocketIO")] # Updated source check
    print(f"Embedding Placeholder ({source}): Generated dummy: {dummy_embedding}")
    return dummy_embedding

def search_similar_verse_placeholder(embedding, source="Unknown"):
    print(f"Search Placeholder ({source}): Simulating search with embedding: {embedding}")
    time.sleep(0.5)
    verse_text = f"ਸਲੋਕੁ ਮਃ ੩ ॥ ({source} Placeholder Verse via Socket.IO)" # Updated
    meaning_text = f"Shalok, Third Mehl ({source} Placeholder Meaning via Socket.IO)" # Updated
    page_num = f"Ang 644 ({source} Placeholder Page via Socket.IO)" # Updated
    found_verse = {
        "verse_gurmukhi": verse_text,
        "meaning_english": meaning_text,
        "source_page": page_num
    }
    print(f"Search Placeholder ({source}): Found dummy verse: {found_verse['verse_gurmukhi']}")
    return found_verse

# --- HTTP Routes (remain unchanged) ---
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
            # Ensure HTTP POST still uses its specific source tag if needed for differentiation
            transcribed_text = transcribe_audio_placeholder(filepath, source="HTTP POST")
            embedding = generate_embedding_placeholder(transcribed_text, source="HTTP POST")
            found_verse_data = search_similar_verse_placeholder(embedding, source="HTTP POST")
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

# --- Socket.IO Event Handlers ---
STREAM_NAMESPACE = '/api/audio_stream'

@socketio.on('connect', namespace=STREAM_NAMESPACE)
def handle_connect():
    print(f"Client connected to Socket.IO namespace: {STREAM_NAMESPACE}, sid: {request.sid}")
    # emit('connection_ack', {'message': 'Connected successfully!'}) # Optional ack

@socketio.on('disconnect', namespace=STREAM_NAMESPACE)
def handle_disconnect():
    sid = request.sid # Get sid before it's potentially unavailable
    print(f"Client disconnected from Socket.IO namespace: {STREAM_NAMESPACE}, sid: {sid}")
    # Clean up buffer for the disconnected client
    if sid in client_audio_buffers:
        del client_audio_buffers[sid]
        print(f"Socket.IO (disconnect from {sid}): Cleared audio buffer for disconnected client.")

client_audio_buffers = {}

@socketio.on('audio_chunk', namespace=STREAM_NAMESPACE)
def handle_audio_chunk(chunk_data): # chunk_data is expected to be bytes
    sid = request.sid
    # print(f"Socket.IO (audio_chunk from {sid}): Received audio chunk. Size: {len(chunk_data)} bytes.") # Verbose

    if not isinstance(chunk_data, bytes):
        print(f"Socket.IO (audio_chunk from {sid}): Received non-bytes data, ignoring. Type: {type(chunk_data)}")
        return

    if sid not in client_audio_buffers:
        client_audio_buffers[sid] = []

    client_audio_buffers[sid].append(chunk_data)

    CHUNKS_TO_ACCUMULATE = 3

    if len(client_audio_buffers[sid]) >= CHUNKS_TO_ACCUMULATE:
        # print(f"Socket.IO (audio_chunk from {sid}): Buffer full. Processing for ASR.") # Verbose

        current_buffer_list = client_audio_buffers[sid]
        client_audio_buffers[sid] = [] # Reset buffer for this client immediately

        temp_filename = f"temp_socketio_audio_{sid}_{uuid.uuid4()}.webm"
        temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)

        try:
            with open(temp_filepath, 'wb') as f:
                for chunk_item in current_buffer_list: # Iterate over the copied list
                    f.write(chunk_item)

            transcribed_text = transcribe_audio_placeholder(temp_filepath, source="SocketIO")
            emit('transcription_update', {
                "type": "transcription_update",
                "text": transcribed_text
            })
            # print(f"Socket.IO (audio_chunk from {sid}): Sent transcription: {transcribed_text}") # Verbose

            embedding = generate_embedding_placeholder(transcribed_text, source="SocketIO")
            found_verse_data = search_similar_verse_placeholder(embedding, source="SocketIO")
            emit('verse_update', {
                "type": "verse_update",
                "data": found_verse_data,
                "source": "SocketIO"
            })
            # print(f"Socket.IO (audio_chunk from {sid}): Sent verse data for: {found_verse_data['verse_gurmukhi']}") # Verbose

        except Exception as e:
            print(f"Socket.IO (audio_chunk from {sid}): Error during processing: {e}")
            emit('processing_error', {"type": "error", "message": "Error processing audio stream"})
        finally:
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
    # else:
    #     print(f"Socket.IO (audio_chunk from {sid}): Chunk added. Buffer: {len(client_audio_buffers[sid])}") # Verbose


@socketio.on('client_stopped_recording', namespace=STREAM_NAMESPACE)
def handle_client_stopped(data): # Data can be None or a JSON object
    sid = request.sid
    print(f"Socket.IO (client_stopped_recording from {sid}): Client indicated recording stopped. Data: {data}")

    # Process any remaining data in the buffer for this client
    # This part could be refactored into a common function if complex,
    # but for now, let's try a simplified version of the buffer processing.
    if sid in client_audio_buffers and client_audio_buffers[sid]:
        print(f"Socket.IO (client_stopped_recording from {sid}): Processing remaining {len(client_audio_buffers[sid])} chunks.")

        current_buffer_list = client_audio_buffers[sid]
        client_audio_buffers[sid] = [] # Clear buffer

        temp_filename = f"temp_socketio_final_audio_{sid}_{uuid.uuid4()}.webm"
        temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)

        try:
            with open(temp_filepath, 'wb') as f:
                for chunk_item in current_buffer_list:
                    f.write(chunk_item)

            transcribed_text = transcribe_audio_placeholder(temp_filepath, source="SocketIO_Final")
            emit('transcription_update', {
                "type": "transcription_update", # Or a different type like "final_transcription"
                "text": transcribed_text,
                "is_final": True # Indicate this might be a final segment
            })
            print(f"Socket.IO (client_stopped_recording from {sid}): Sent final transcription: {transcribed_text}")

            embedding = generate_embedding_placeholder(transcribed_text, source="SocketIO_Final")
            found_verse_data = search_similar_verse_placeholder(embedding, source="SocketIO_Final")
            emit('verse_update', {
                "type": "verse_update", # Or "final_verse_update"
                "data": found_verse_data,
                "source": "SocketIO_Final",
                "is_final": True
            })
            print(f"Socket.IO (client_stopped_recording from {sid}): Sent final verse data for: {found_verse_data['verse_gurmukhi']}")

        except Exception as e:
            print(f"Socket.IO (client_stopped_recording from {sid}): Error during final processing: {e}")
            emit('processing_error', {"type": "error", "message": "Error processing final audio segment"})
        finally:
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)

    # Clean up the entry for the client if it exists, after processing
    if sid in client_audio_buffers: # Should be empty now
        del client_audio_buffers[sid]


if __name__ == '__main__':
    print("Starting Flask-SocketIO server on host 0.0.0.0, port 5001...")
    # Use socketio.run for development. This will use the Werkzeug development server
    # if gevent is not installed, or gevent if it is (preferred for Socket.IO).
    # For production, Gunicorn with gevent is recommended (see README).
    # The async_mode='gevent' in SocketIO() initialization is important for Gunicorn.
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, use_reloader=True)
    # debug=True enables verbose logging and auto-reloading.
    # use_reloader=True allows the server to restart on code changes if the underlying
    # development server supports it well with the chosen async_mode.
    # For gevent, the reloader might behave differently or might not be as robust.
    # If issues with reloader and gevent, set use_reloader=False.
