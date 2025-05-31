# Gurdwara Verse Projection System

## Project Description

This project aims to display verses being read by a Granthi in a Gurdwara on a projector, along with their meanings in real-time (eventually). The system involves capturing audio, transcribing it to Gurmukhi text, finding the corresponding verse in a database using text embeddings, and displaying the verse and its meaning on a frontend.

Key Technologies:
*   Frontend: HTML, JavaScript, Socket.IO Client
*   Backend: Python, Flask, Flask-CORS, Flask-SocketIO
*   Async Model (Backend): Gevent
*   WSGI Server (for production): Gunicorn
*   (Placeholders for ASR, Embedding, Search)

## Current Status

**Initial Placeholder Version:** This version has the basic web application structure with frontend and backend components. Core functionalities like Speech-to-Text (ASR), text embedding, and database search are currently implemented as **placeholders** that simulate the process with hardcoded data. This allows for testing the end-to-end flow of the application.

## Directory Structure

```
.
├── backend/
│   ├── uploads/            # Directory where uploaded audio is (temporarily) stored
│   ├── main.py             # Flask backend application
│   ├── requirements.txt    # Python dependencies
│   └── database_schema.txt # Outline of the proposed database structure
├── frontend/
│   ├── index.html          # Main HTML page for the frontend
│   └── app.js              # JavaScript for frontend logic (mic access, API calls)
└── README.md               # This file
```

## Local Development and Testing

Follow these steps to set up and run the project on your local machine.

### 1. Backend Setup & Execution

The backend is a Python Flask application integrated with Flask-SocketIO for real-time communication.

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```
2.  **Create a Python virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```
2.  **Create and activate a Python virtual environment** (if not already done).
3.  **Install dependencies (including Flask-SocketIO, Gevent, Gunicorn):**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the Backend Server for Development:**
    The primary way to run the backend for development, supporting WebSockets via Flask-SocketIO:
    ```bash
    python main.py
    ```
    *   This uses `socketio.run(app, ...)` internally, which starts a development server (often Werkzeug with Gevent if available) capable of handling both HTTP and Socket.IO traffic. By default, it should run on `http://localhost:5001`.

5.  **Alternative: Running with Gunicorn (for Production-like Environment):**
    For a more production-like setup, or if you prefer Gunicorn:
    ```bash
    gunicorn --worker-class gevent -w 1 main:app -b 0.0.0.0:5001
    ```
    *   Ensure `async_mode='gevent'` is set in `SocketIO(app, ...)` in `main.py` for this to work optimally.
    *   Replace `5001` with your desired port if changed.

**Note on Port Conflicts (Especially Port 5000/5001):**
The default port used in `main.py` is `5001`. If this port is in use by another service on your system (e.g., the "Control Center" on macOS Monterey and later, or other applications).
If you encounter errors like "address already in use" when starting the Gunicorn or Flask server, or if the server seems to start but is unresponsive, try using a different port:
1.  Open `backend/main.py`.
2.  Find the line `socketio.run(app, host='0.0.0.0', port=5001, ...)` or the Gunicorn command.
3.  Change the port in `main.py` and/or in the Gunicorn command (e.g., to `5002`).
    For `main.py` (via `socketio.run`):
    ```python
    socketio.run(app, host='0.0.0.0', port=5002, debug=True, use_reloader=True)
    ```
    For Gunicorn:
    ```bash
    gunicorn --worker-class gevent -w 1 main:app -b 0.0.0.0:5002
    ```
4.  Save the file and try running the server again.
5.  **Important:** If you change the backend port, you **must** also update the Socket.IO connection URL (`http://...` for Socket.IO client) and any `fetch` URLs in `frontend/app.js`. See the note below.

### 2. Frontend Setup & Execution

The frontend consists of static HTML and JavaScript files and uses the Socket.IO client library.

1.  **Ensure Socket.IO Client is Included:**
    The `frontend/index.html` file should include the Socket.IO client library script (e.g., from a CDN) in its `<head>` or before the closing `</body>` tag. Example:
    ```html
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.5/socket.io.min.js"></script>
    ```
2.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```
3.  **Serve the frontend using a local HTTP server:**
    ```bash
    python -m http.server 8080
    ```
    (Or your preferred port).
4.  **Access the frontend in your web browser:**
    Open `http://localhost:8080`.

**Important: Matching Backend URL in Frontend Code**
The frontend JavaScript (`frontend/app.js`) needs to know the correct URL for the Socket.IO server.
By default, it attempts to connect to `http://localhost:5001/api/audio_stream` for Socket.IO.

1.  Open `frontend/app.js`.
2.  Find the line `const socketUrl = 'http://localhost:5001/api/audio_stream';`. Ensure the hostname and port match your backend server (whether run via `python main.py` or Gunicorn).
3.  If you are also using the HTTP POST fallback (`/api/audio`), ensure its `fetch` URL is also correct.

Make sure these URLs are correct before testing.

### 3. Testing the Application

1.  **Ensure both the backend and frontend servers are running** as described above.
2.  **Open your browser's Developer Console** (usually by pressing `F12` or right-clicking and selecting "Inspect" -> "Console"). This will help you see logs from the JavaScript and any potential errors.
3.  On the webpage (`http://localhost:8080`), you should see the "Gurdwara Verse Projection" title and a "Start Microphone" button.
4.  **Click the "Start Microphone" button.** Your browser will likely ask for permission to use your microphone. **Allow** it.
    *   The button text should change to "Stop Microphone".
    *   The status message `Recording... Speak into the microphone.` should appear.
5.  **Speak a few words** into your microphone.
6.  **Click the "Stop Microphone" button.**
    *   The button text should change back to "Start Microphone".
    *   You should see a status message like `Sending audio to backend...`.
7.  **Observe the display area:**
    After a short delay (simulating processing), the display area should update to show:
    *   Initially, "Live Transcription (Socket.IO): [some Gurmukhi text]" and "Searching for verse...".
    *   Then, it should update to "Verse Found (Socket.IO Stream)" with Gurmukhi, Meaning, Source, and the "Based on transcription (Socket.IO)..." text.
8.  **Check your terminal console for the backend (run with `python main.py` or Gunicorn):**
    You should see log messages indicating:
    *   "Client connected to Socket.IO namespace..."
    *   Messages about receiving audio chunks, (e.g., "Socket.IO (audio_chunk from ...): Received audio chunk..."), saving temporary files, and sending transcription/verse updates via Socket.IO.
    *   (If you test the HTTP POST route `/api/audio` separately, you'll see standard Flask logs for that).
9.  **Check your browser's developer console:**
    You should see logs from `app.js`:
    *   "Socket.IO: Connected successfully..."
    *   "Socket.IO: Sending audio chunk..." (if you uncommented this log in `ondataavailable`)
    *   "Socket.IO: Received transcription_update: {type: 'transcription_update', ...}"
    *   "Socket.IO: Received verse_update: {type: 'verse_update', ...}"

This completes a test of the end-to-end streaming placeholder flow using Socket.IO.

## Current Features
*   **Real-time Audio Streaming (Placeholder via Socket.IO):** Captures microphone audio, streams it to the backend using Socket.IO events, and receives (placeholder) transcriptions and verse lookups in real-time.
*   **Batch Audio Upload (Placeholder via HTTP POST):** Still supports uploading a complete audio file for (placeholder) processing.


## Future Development
*   Replace placeholder ASR with a real Gurmukhi ASR service/model.
*   Implement actual text embedding generation using a suitable model.
*   Set up a database (e.g., PostgreSQL, SQLite) based on `database_schema.txt`.
*   Populate the database with Gurbani verses and meanings.
*   Implement similarity search against verse embeddings in the database.
*   Refactor audio handling to support streaming (user feedback).
*   Consider cloud deployment options (e.g., Google Cloud Platform).
