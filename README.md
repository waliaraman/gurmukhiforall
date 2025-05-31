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
│   ├── static/
│   │   ├── index.html      # Main HTML page (served by Flask)
│   │   └── js/
│   │       └── app.js      # Client-side JavaScript (served by Flask)
│   ├── uploads/            # Directory where uploaded audio is (temporarily) stored
│   ├── main.py             # Flask-SocketIO backend application
│   ├── requirements.txt    # Python dependencies
│   └── database_schema.txt # Outline of the proposed database structure
└── README.md               # This file
```

## Running the Application Locally

The application is now served entirely from the Python Flask backend.

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```
2.  **Create and activate a Python virtual environment:**
    (If you haven't already, e.g., `python -m venv venv` then `source venv/bin/activate` or `venv\Scriptsctivate`)
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the Application Server:**
    *   **For Development (with auto-reload and debug mode):**
        ```bash
        python main.py
        ```
        This uses `socketio.run()` and will serve the application, including Socket.IO and HTTP routes.
    *   **For a Production-like Environment (using Gunicorn):**
        ```bash
        gunicorn --worker-class gevent -w 1 main:app -b 0.0.0.0:5001
        ```
        (Ensure `async_mode='gevent'` is set in `SocketIO(app, ...)` in `main.py`).

5.  **Access the Application:**
    Open your web browser and go to:
    ```
    http://localhost:5001/
    ```
    (Or the port you configured if different).

**Note on Port Conflicts (Especially Port 5000/5001):**
The default port used in `main.py` is `5001`. If this port is in use by another service on your system (e.g., the "Control Center" on macOS Monterey and later, or other applications).
If you encounter errors like "address already in use" when starting the Gunicorn or `python main.py` server, or if the server seems to start but is unresponsive, try using a different port:
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
5.  **Important:** If you change the backend port, you **must** also update the Socket.IO connection URL in `backend/static/js/app.js`.

<!-- The separate frontend setup is no longer needed as Flask serves the frontend. -->
**Accessing the Frontend:**
Since Flask now serves the frontend:
*   Ensure `backend/static/index.html` includes the Socket.IO client library (e.g., from CDN).
*   The `index.html` should reference `app.js` using a path like `/static/js/app.js`.
*   The `backend/static/js/app.js` should connect to Socket.IO using a relative path to the server, like `io('/api/audio_stream')`.

## Testing the Application

1.  **Ensure the application server is running** using one of the methods described in "Running the Application Locally" (e.g., `python backend/main.py`).
2.  **Access the application** in your browser at `http://localhost:5001/` (or the port you configured).
3.  **Open your browser's Developer Console** (usually by pressing F12 or Right-click -> Inspect, then select the Console and Network tabs).
    *   In the **Network tab**, after the page loads, verify that `index.html` (or `/`) is loaded, and `app.js` is loaded from `/static/js/app.js`.
4.  **Click the "Start Microphone" button.** Your browser will likely ask for permission to use your microphone. **Allow** it.
    *   The UI should indicate connection ("Connected. Ready to stream.") and then "Recording (Socket.IO)... Speak into mic.".
    *   The backend terminal (where you ran `python main.py` or Gunicorn) should show a log message like "Client connected to Socket.IO namespace...".
5.  **Speak for several seconds.**
    *   The UI in the browser should display "Live Transcription (Socket.IO): ..." followed by "Verse Found (Socket.IO Stream)...", updating as the backend processes audio chunks.
    *   The browser's Developer Console will show Socket.IO messages being sent and received (e.g., "Socket.IO: Received transcription_update...", "Socket.IO: Received verse_update...").
    *   The backend terminal will show logs for audio chunk reception, processing, and event emissions.
6.  **Click "Stop Microphone."**
    *   The UI should update to indicate recording has stopped (e.g., "Recording stopped (Socket.IO). Ready to start.").
    *   The backend terminal should log the `client_stopped_recording` event and any final processing.

This completes a test of the end-to-end streaming placeholder flow using the integrated Flask and Socket.IO setup.

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
