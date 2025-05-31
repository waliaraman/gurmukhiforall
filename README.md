# Gurdwara Verse Projection System

## Project Description

This project aims to display verses being read by a Granthi in a Gurdwara on a projector, along with their meanings in real-time (eventually). The system involves capturing audio, transcribing it to Gurmukhi text, finding the corresponding verse in a database using text embeddings, and displaying the verse and its meaning on a frontend.

Key Technologies:
*   Frontend: HTML, JavaScript
*   Backend: Python, Flask, Flask-CORS
*   WebSocket Communication: Flask-Sockets
*   WSGI Server (for WebSockets): Gunicorn with Gevent
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

The backend is a Python Flask application that now includes WebSocket support for real-time audio streaming.

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```
2.  **Create a Python virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```
2.  **Create and activate a Python virtual environment** (if not already done - see previous README version for details).
3.  **Install dependencies (including Gunicorn and Gevent):**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the Backend Server with Gunicorn (Recommended for WebSockets):**
    To enable WebSocket functionality for audio streaming, run the backend using Gunicorn with a Gevent worker:
    ```bash
    gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 main:app -b 0.0.0.0:5001
    ```
    *   Replace `5001` with your desired port if you changed it in `main.py`.
    *   This command starts the server, and you'll see Gunicorn logs in the terminal. The backend is now ready to accept both HTTP requests (on `/api/audio`) and WebSocket connections (on `/api/audio_stream`).

5.  **Alternative: Running with Flask's Development Server (HTTP Only):**
    You can still run the backend with `python main.py` (which internally uses `app.run(...)`):
    ```bash
    python main.py
    ```
    However, **this method will only serve the standard HTTP routes (like the original `/api/audio` for file uploads). The WebSocket endpoint (`/api/audio_stream`) will NOT function correctly with the Flask development server.** Use Gunicorn (as described above) for testing streaming features.

**Note on Port Conflicts (Especially Port 5000/5001):**
The default port used in `main.py` is `5001`. If this port is in use by another service on your system (e.g., the "Control Center" on macOS Monterey and later, or other applications).
If you encounter errors like "address already in use" when starting the Gunicorn or Flask server, or if the server seems to start but is unresponsive, try using a different port:
1.  Open `backend/main.py`.
2.  Find the line `app.run(debug=True, port=5001, host='0.0.0.0')` or the Gunicorn command.
3.  Change the port in `main.py` and/or in the Gunicorn command (e.g., to `5002`).
    For `main.py`:
    ```python
    app.run(debug=True, port=5002, host='0.0.0.0')
    ```
    For Gunicorn:
    ```bash
    gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 main:app -b 0.0.0.0:5002
    ```
4.  Save the file and try running the server again.
5.  **Important:** If you change the backend port, you **must** also update the WebSocket URL (`ws://...`) and `fetch` URL in `frontend/app.js`. See the note below.

### 2. Frontend Setup & Execution

The frontend consists of static HTML and JavaScript files.

1.  **Open a new terminal window/tab.**
2.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```
3.  **Serve the frontend using a local HTTP server:**
    For microphone access (`navigator.mediaDevices.getUserMedia`) to work correctly, the HTML page needs to be served over HTTP/S, not just opened as a local file (`file:///...`). Python's built-in HTTP server is convenient for this.
    ```bash
    python -m http.server 8080
    ```
    (You can use any port other than 5000 if it's free, e.g., 8000, 8080).
4.  **Access the frontend in your web browser:**
    Open your web browser and go to `http://localhost:8080` (or the port you chose).

**Important: Matching Backend URL in Frontend Code**
The frontend JavaScript (`frontend/app.js`) needs to know the correct URL for both the backend API (HTTP POST) and the WebSocket server.
By default:
*   HTTP `fetch` connects to `/api/audio` (relative path, assumes same host and port as frontend is served on, but will target backend port due to browser same-origin policy for fetch if backend runs on different port and CORS is set up). For clarity, the example below will use an absolute path.
*   WebSocket connects to `ws://localhost:5001/api/audio_stream`.

1.  Open `frontend/app.js`.
2.  **For WebSocket:** Find the line `socket = new WebSocket('ws://localhost:5001/api/audio_stream');`. Ensure the hostname and port (`localhost:5001`) match your Gunicorn server.
3.  **For HTTP Fallback (if used):** Find any `fetch` calls (e.g., if you re-enable the old POST method). Ensure the URL matches. Example: `fetch('http://localhost:5001/api/audio', { ... });`

Make sure these URLs are correct before testing, especially the WebSocket URL.

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
    *   Initially, "Live Transcription (Placeholder): [some Gurmukhi text]" and "Searching for verse...".
    *   Then, it should update to "Verse Found (Streamed Placeholder)" with Gurmukhi, Meaning, Source, and the "Based on transcription..." text.
8.  **Check your terminal console for the backend (Gunicorn server):**
    You should see log messages indicating:
    *   WebSocket connection established.
    *   Messages about receiving audio chunks, saving temporary files, and sending transcription/verse updates.
    *   (If you test the HTTP POST route `/api/audio` separately, you'll see logs for that too).
9.  **Check your browser's developer console:**
    You should see logs from `app.js`:
    *   "WebSocket connection established."
    *   "Sending audio chunk over WebSocket..."
    *   "WebSocket received JSON message: {type: 'transcription_update', ...}"
    *   "WebSocket received JSON message: {type: 'verse_update', ...}"

This completes a test of the end-to-end streaming placeholder flow.

## Current Features
*   **Real-time Audio Streaming (Placeholder):** Captures microphone audio, streams it to the backend via WebSockets, and receives (placeholder) transcriptions and verse lookups in real-time.
*   **Batch Audio Upload (Placeholder):** Still supports uploading a complete audio file via HTTP POST for (placeholder) processing (if `/api/audio` route is kept active and tested separately).


## Future Development
*   Replace placeholder ASR with a real Gurmukhi ASR service/model.
*   Implement actual text embedding generation using a suitable model.
*   Set up a database (e.g., PostgreSQL, SQLite) based on `database_schema.txt`.
*   Populate the database with Gurbani verses and meanings.
*   Implement similarity search against verse embeddings in the database.
*   Refactor audio handling to support streaming (user feedback).
*   Consider cloud deployment options (e.g., Google Cloud Platform).
