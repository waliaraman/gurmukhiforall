from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import time
import json
import uuid
from google.cloud import speech # Add this import
from queue import Queue # Standard library queue

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, async_mode='gevent', cors_allowed_origins="*")

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Updated Placeholder Functions ---

# --- Serve Frontend ---
@app.route('/')
def serve_index():
    # This will serve 'backend/static/index.html'
    # Flask's default static_folder is 'static'.
    # Ensure index.html references <script src="js/app.js"> or similar relative path.
    return send_from_directory(app.static_folder, 'index.html')

# transcribe_audio_placeholder function has been removed.
# Real ASR is handled by Google Cloud Speech-to-Text functions.

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
# The previous @app.route('/') for "Backend is running (HTTP)!" is replaced by serve_index.

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
            print(f"File saved to {filepath} via HTTP POST.")
            # All placeholder processing (ASR, embedding, search) is removed from this route.
            # Real ASR is handled via Socket.IO streaming with Google Cloud Speech.
            return jsonify({
                "message": "File uploaded successfully via HTTP POST. No ASR/search processing on this route.",
                "filename": filename
            }), 200
        except Exception as e:
            print(f"Error saving file via HTTP POST: {e}")
            return jsonify({"message": "Error saving file", "error": str(e)}), 500

    return jsonify({"message": "Unknown error during HTTP POST file upload"}), 500

# --- Google Cloud Speech-to-Text Integration ---

# Dictionary to hold active Google ASR streams, keyed by client SID
google_asr_streams = {}

def google_asr_request_generator(sid, audio_config_dict): # Renamed audio_config to audio_config_dict
    """Yields audio chunks for the Google Cloud Speech API.
    This generator is fed by the 'audio_chunk' Socket.IO event.
    It also sends the initial RecognitionConfig.
    """
    # The first request carries the configuration.
    # Subsequent requests carry raw audio bytes.
    # print(f"ASR_GEN ({sid}): Sending initial config: {audio_config_dict}")
    yield speech.StreamingRecognizeRequest(**audio_config_dict)

    while True:
        if sid in google_asr_streams and hasattr(google_asr_streams[sid], 'audio_queue'):
            chunk = google_asr_streams[sid].audio_queue.get()
            if chunk is None:
                # print(f"ASR_GEN ({sid}): Received None (end of stream signal).")
                return
            # print(f"ASR_GEN ({sid}): Yielding audio chunk. Size: {len(chunk)} bytes.")
            yield speech.StreamingRecognizeRequest(audio_content=chunk)
        else:
            # print(f"ASR_GEN ({sid}): No queue or stream found, stopping generator.")
            return


def process_google_asr_responses(responses, sid):
    """Processes responses from the Google ASR stream and emits to client."""
    num_chars_printed = 0
    try:
        for response in responses:
            if not response.results:
                # print(f"ASR_RESP ({sid}): Empty response result.")
                continue

            result = response.results[0]
            if not result.alternatives:
                # print(f"ASR_RESP ({sid}): Empty alternatives in result.")
                continue

            transcript = result.alternatives[0].transcript

            if result.is_final:
                print(f"ASR_RESP ({sid}): Final transcript: {transcript}")
                socketio.emit('transcription_update', {
                    'text': transcript,
                    'is_final': True,
                    'stability': result.stability,
                }, room=sid, namespace=STREAM_NAMESPACE)
                num_chars_printed = 0
            else:
                # print(f"ASR_RESP ({sid}): Interim transcript: {transcript} (Stability: {result.stability})")
                socketio.emit('transcription_update', {
                    'text': transcript,
                    'is_final': False,
                    'stability': result.stability,
                }, room=sid, namespace=STREAM_NAMESPACE)
                num_chars_printed = len(transcript)

    except Exception as e:
        print(f"ASR_RESP ({sid}): Error processing ASR responses: {e}")
        socketio.emit('processing_error', {'message': f'ASR Error: {str(e)}'}, room=sid, namespace=STREAM_NAMESPACE)
    finally:
        print(f"ASR_RESP ({sid}): Finished processing responses.")
        if sid in google_asr_streams:
            if hasattr(google_asr_streams[sid], 'audio_queue') and google_asr_streams[sid].audio_queue is not None:
                 google_asr_streams[sid].audio_queue.put(None)
            # Check if 'active' key exists before trying to set it to False
            if 'active' in google_asr_streams[sid]:
                 google_asr_streams[sid]['active'] = False # Mark as inactive
            # Optionally remove the entry if it's fully processed and thread is joined, or let disconnect handler do it.
            # For now, just marking inactive and ensuring generator stops.
            # del google_asr_streams[sid] # This might be too soon if disconnect handler also tries.
            # Ensure the entry is fully removed to allow re-starting on next audio_chunk if needed
            if sid in google_asr_streams:
                del google_asr_streams[sid]
            print(f"ASR_RESP ({sid}): Cleaned up ASR stream data for SID {sid}.")


def start_google_asr_for_client(sid):
    """Starts a new Google ASR stream for a given client SID."""
    if sid in google_asr_streams and google_asr_streams[sid].get('active', False):
        print(f"ASR_START ({sid}): Stream already active.")
        return

    try:
        client = speech.SpeechClient()

        recognition_config_dict = { # Using a dict for easy unpacking
            "encoding": speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            "sample_rate_hertz": 48000,
            "language_code": "pa-IN",
            "enable_automatic_punctuation": True,
        }
        streaming_config_obj = speech.StreamingRecognitionConfig( # This is the object for client.streaming_recognize
            config=speech.RecognitionConfig(**recognition_config_dict), # Pass the dict to RecognitionConfig
            interim_results=True
        )

        google_asr_streams[sid] = {
            'client': client,
            # The StreamingRecognizeRequest takes **kwargs from a dict for the initial config part
            'initial_request_config': {'config': recognition_config_dict, 'interim_results': True},
            'audio_queue': Queue(),
            'active': True,
            'responses_thread': None
        }

        audio_requests = google_asr_request_generator(sid, google_asr_streams[sid]['initial_request_config'])

        print(f"ASR_START ({sid}): Starting Google ASR stream...")
        responses = client.streaming_recognize(
            config=streaming_config_obj, # Use the StreamingRecognitionConfig object here
            requests=audio_requests
        )

        google_asr_streams[sid]['responses_thread'] = socketio.start_background_task(
            target=process_google_asr_responses,
            responses=responses,
            sid=sid
        )
        print(f"ASR_START ({sid}): Background task for responses started.")

    except Exception as e:
        print(f"ASR_START ({sid}): Failed to start Google ASR stream: {e}")
        socketio.emit('processing_error', {'message': f'Failed to start ASR: {str(e)}'}, room=sid, namespace=STREAM_NAMESPACE)
        if sid in google_asr_streams:
            del google_asr_streams[sid]

# --- Socket.IO Event Handlers ---
STREAM_NAMESPACE = '/api/audio_stream'

@socketio.on('connect', namespace=STREAM_NAMESPACE)
def handle_connect():
    sid = request.sid
    print(f"Socket.IO Client connected: {sid} to namespace {STREAM_NAMESPACE}")
    # Start a new Google ASR stream for this client session
    start_google_asr_for_client(sid)

@socketio.on('disconnect', namespace=STREAM_NAMESPACE)
def handle_disconnect():
    sid = request.sid
    print(f"Socket.IO Client disconnected: {sid} from namespace {STREAM_NAMESPACE}")
    # Signal the end of audio for this client's ASR stream and rely on
    # process_google_asr_responses for dictionary cleanup.
    if sid in google_asr_streams:
        if hasattr(google_asr_streams[sid], 'audio_queue') and google_asr_streams[sid]['audio_queue'] is not None:
            google_asr_streams[sid]['audio_queue'].put(None) # Signal generator to stop
        # The process_google_asr_responses function's finally block will handle deletion from google_asr_streams

@socketio.on('audio_chunk', namespace=STREAM_NAMESPACE)
def handle_audio_chunk(chunk_data):
    sid = request.sid

    if sid not in google_asr_streams or not google_asr_streams[sid].get('active', False):
        print(f"Socket.IO (audio_chunk from {sid}): No active ASR stream or stream was inactive. Attempting to start new one.")
        start_google_asr_for_client(sid)
        # Check if stream was successfully started before proceeding
        if sid not in google_asr_streams or not google_asr_streams[sid].get('active', False):
            print(f"Socket.IO (audio_chunk from {sid}): Failed to start ASR stream on-the-fly. Ignoring chunk.")
            # Optionally emit an error to the client if this happens
            # socketio.emit('processing_error', {'message': 'ASR stream could not be started.'}, room=sid, namespace=STREAM_NAMESPACE)
            return

    # Stream should be active now, or was already active
    if isinstance(chunk_data, bytes):
        # print(f"Socket.IO (audio_chunk from {sid}): Received audio chunk. Size: {len(chunk_data)} bytes. Adding to queue.") # Verbose
        google_asr_streams[sid]['audio_queue'].put(chunk_data)
    else:
        print(f"Socket.IO (audio_chunk from {sid}): Received non-bytes data, expected bytes. Type: {type(chunk_data)}")


@socketio.on('client_stopped_recording', namespace=STREAM_NAMESPACE)
def handle_client_stopped(data):
    sid = request.sid
    print(f"Socket.IO (client_stopped_recording from {sid}): Client indicated recording stopped. Data: {data}")

    if sid in google_asr_streams and google_asr_streams[sid].get('active', False):
        if hasattr(google_asr_streams[sid], 'audio_queue') and google_asr_streams[sid]['audio_queue'] is not None:
            google_asr_streams[sid]['audio_queue'].put(None)
            print(f"Socket.IO (client_stopped_recording from {sid}): Signaled end of audio to ASR generator.")
        # The ASR stream processing will handle final transcriptions and then cleanup.
        # No need to remove client_audio_buffers here as it's not used with Google ASR.
    else:
        print(f"Socket.IO (client_stopped_recording from {sid}): No active ASR stream found to stop.")

# Note: The old `client_audio_buffers` dictionary and the placeholder-based processing
# within Socket.IO event handlers have been removed by these changes.
# The embedding/search logic is currently within process_google_asr_responses (commented out or to be added).

if __name__ == '__main__':
    print("Starting Flask-SocketIO server on host 0.0.0.0, port 5001...")
    print("Frontend will be served from http://localhost:5001/")
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
