# Gurdwara Verse Projection System

## Project Description

This project aims to display verses being read by a Granthi in a Gurdwara on a projector, along with their meanings in real-time (eventually). The system involves capturing audio, transcribing it to Gurmukhi text, finding the corresponding verse in a database using text embeddings, and displaying the verse and its meaning on a frontend.

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

The backend is a Python Flask application.

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```
2.  **Create a Python virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```
3.  **Activate the virtual environment:**
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
    *   On Windows (Git Bash or PowerShell):
        ```bash
        venv/Scripts/activate
        ```
4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Run the Flask development server:**
    ```bash
    python main.py
    ```
    By default, the backend server will start on `http://127.0.0.1:5000`. You should see output in your terminal indicating that the server is running (e.g., `* Running on http://127.0.0.1:5000/`). This terminal will also show logs for incoming requests and processing.

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
    *   A heading: "Verse Found (Placeholder)"
    *   **Gurmukhi:** A sample Gurmukhi verse (hardcoded).
    *   **Meaning:** A sample English meaning (hardcoded).
    *   **Source:** A sample source/page (hardcoded).
    *   **Transcribed (Placeholder):** The hardcoded Gurmukhi text that the backend "transcribed".
8.  **Check your terminal console for the backend (Flask app):**
    You should see log messages indicating:
    *   A POST request to `/api/audio`.
    *   The audio file being saved (e.g., `File saved to uploads/recording_xxxxxxxxxx.webm`).
    *   Messages from the placeholder ASR, embedding, and search functions.
9.  **Check your browser's developer console:**
    You should see logs from `app.js`, including the response data received from the backend.

This completes a test of the end-to-end placeholder flow.

## Future Development
*   Replace placeholder ASR with a real Gurmukhi ASR service.
*   Implement actual text embedding generation.
*   Set up a database (e.g., PostgreSQL, SQLite) based on `database_schema.txt`.
*   Populate the database with Gurbani verses and meanings.
*   Implement similarity search against verse embeddings in the database.
*   Refactor audio handling to support streaming (user feedback).
*   Consider cloud deployment options (e.g., Google Cloud Platform).
