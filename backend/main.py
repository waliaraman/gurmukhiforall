from flask import Flask, request, jsonify
import os
import time

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def transcribe_audio_placeholder(audio_filepath):
    print(f"ASR Placeholder: Simulating transcription for {audio_filepath}...")
    time.sleep(1) # Shorter delay
    gurmukhi_text = "ਇਕ ਓਅੰਕਾਰ ਸਤਿ ਨਾਮੁ ਕਰਤਾ ਪੁਰਖੁ ਨਿਰਭਉ ਨਿਰਵੈਰੁ ਅਕਾਲ ਮੂਰਤਿ ਅਜੂਨੀ ਸੈਭੰ ਗੁਰ ਪ੍ਰਸਾਦਿ ॥"
    print(f"ASR Placeholder: Simulated transcription: {gurmukhi_text}")
    return gurmukhi_text

def generate_embedding_placeholder(text):
    '''Placeholder for generating text embeddings.'''
    print(f"Embedding Placeholder: Simulating embedding generation for text: '{text[:30]}...'")
    time.sleep(0.5)
    dummy_embedding = [0.1, 0.2, 0.3, 0.4, 0.5] # Example fixed-size embedding
    print(f"Embedding Placeholder: Generated dummy embedding: {dummy_embedding}")
    return dummy_embedding

def search_similar_verse_placeholder(embedding):
    '''Placeholder for searching similar verses in the database using embeddings.'''
    print(f"Search Placeholder: Simulating search with embedding: {embedding}")
    time.sleep(1)
    # This is a hardcoded example. In a real system, this would query a database.
    found_verse = {
        "verse_gurmukhi": "ਗੁਰੁ ਸੇਵਹਿ ਸੋ ਸਿਖ ਸੇਵਕੁ ਭਾਈ ॥",
        "meaning_english": "They who serve the Guru are Sikhs, servants, spiritual siblings.",
        "source_page": "Ang 601"
    }
    print(f"Search Placeholder: Found dummy verse: {found_verse['verse_gurmukhi']}")
    return found_verse

@app.route('/')
def home():
    return "Backend is running!"

@app.route('/api/audio', methods=['POST'])
def process_audio():
    if 'audio_file' not in request.files:
        return jsonify({"message": "No audio file part in the request"}), 400

    file = request.files['audio_file']

    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    if file:
        filename = f"recording_{int(time.time())}.webm"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(filepath)
            print(f"File saved to {filepath}")

            transcribed_text = transcribe_audio_placeholder(filepath)
            embedding = generate_embedding_placeholder(transcribed_text)
            found_verse_data = search_similar_verse_placeholder(embedding)

            return jsonify({
                "message": "Audio processed (placeholders for ASR, embedding, search).",
                "filename": filename,
                "transcribed_text": transcribed_text,
                "generated_embedding": embedding, # For debugging/info
                "found_verse": found_verse_data
            }), 200
        except Exception as e:
            print(f"Error processing file: {e}")
            return jsonify({"message": "Error processing file", "error": str(e)}), 500

    return jsonify({"message": "Unknown error during audio processing"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
