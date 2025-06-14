const micButton = document.getElementById('micButton');
const verseDisplay = document.getElementById('verseDisplay');
let isRecording = false;
let mediaRecorder;
let streamReference;
let socket; // This will now be the Socket.IO client instance

// Modify connectSocket to fully implement server event handlers
const connectSocket = () => {
    if (socket && socket.connected) {
        // console.log('Socket.IO already connected.'); // Can be noisy
        return socket;
    }
    // Connect to the Socket.IO server, specifically to the namespace
    // Path relative to current host/port
    socket = io('/api/audio_stream', {
        // Optional: transports: ['websocket'], // Can be useful for consistency
    });
    console.log('Attempting to connect to Socket.IO namespace /api/audio_stream on current host.');

    socket.on('connect', () => {
        console.log('Socket.IO: Connected successfully. SID:', socket.id);
        verseDisplay.textContent = 'Connected. Ready to stream.';
    });

    socket.on('disconnect', (reason) => {
        console.log('Socket.IO: Disconnected.', reason);
        verseDisplay.textContent = 'Disconnected. Click Start to reconnect.';
        isRecording = false;
        micButton.textContent = 'Start Microphone';
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
        }
        if (streamReference) {
            streamReference.getTracks().forEach(track => track.stop());
            streamReference = null;
        }
    });

    socket.on('connect_error', (error) => {
        console.error('Socket.IO: Connection Error.', error);
        verseDisplay.textContent = 'Failed to connect. Ensure server is running & accessible.';
        isRecording = false;
        micButton.textContent = 'Start Microphone';
    });

    // To store the latest transcription for display with verse results
    let latestFinalTranscription = ""; // Store the latest final transcript
    let currentInterimTranscription = ""; // Store the current interim transcript

    socket.on('transcription_update', (data) => {
        console.log('Socket.IO: Received transcription_update:', data);
        if (data && typeof data.text === 'string') {
            if (data.is_final) {
                latestFinalTranscription = data.text; // Or append: latestFinalTranscription += data.text + " ";
                currentInterimTranscription = ""; // Clear interim

                // Update UI to show final transcript and prepare for verse search
                verseDisplay.innerHTML = `
                    <p><strong>Final Transcription:</strong> ${latestFinalTranscription}</p>
                    <p><em>(Verse search will be based on this)</em></p>
                `;
                // The verse_update event from backend will follow if a verse is found
            } else {
                // Interim result, update ongoing transcription display
                currentInterimTranscription = data.text;
                verseDisplay.innerHTML = `
                    <p><em>Translating: ${currentInterimTranscription} ... (stability: ${data.stability ? data.stability.toFixed(2) : 'N/A'})</em></p>
                    ${latestFinalTranscription ? `<p><small>Previous final: ${latestFinalTranscription}</small></p>` : ""}
                `;
            }
        }
    });

    socket.on('verse_update', (data) => {
        console.log('Socket.IO: Received verse_update:', data);
        if (data && data.data) {
            const verse = data.data;
            // Display verse with the final transcription that triggered it
            verseDisplay.innerHTML = `
                <h3>Verse Found (Google ASR Stream)</h3>
                <p><strong>Gurmukhi:</strong> ${verse.verse_gurmukhi}</p>
                <p><strong>Meaning:</strong> ${verse.meaning_english}</p>
                <p><strong>Source:</strong> ${verse.source_page}</p>
                <hr>
                <p><small><em>Based on final transcription: ${latestFinalTranscription}</em></small></p>
            `;
        }
    });

    socket.on('processing_error', (data) => {
        console.error('Socket.IO: Received processing_error from backend:', data);
        if (data && data.message) {
            verseDisplay.innerHTML = `<p style="color: red;">Server Error: ${data.message}</p>`;
        } else {
            verseDisplay.innerHTML = `<p style="color: red;">An unspecified server error occurred.</p>`;
        }
    });

    // Example of handling a custom ack from server on connect if implemented
    // socket.on('connection_ack', (data) => {
    //     console.log('Socket.IO: Connection acknowledged by server:', data.message);
    // });

    return socket;
};


// Modify micButton event listener
micButton.addEventListener('click', async () => {
    if (!isRecording) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            streamReference = stream;
            console.log('Microphone access granted');

            isRecording = true; // Set recording state first
            micButton.textContent = 'Stop Microphone'; // Update button text

            if (!socket || !socket.connected) {
                verseDisplay.textContent = 'Connecting to server...';
                socket = connectSocket(); // Initialize or get existing socket

                // Wait for connection before starting MediaRecorder
                // Use a flag to ensure startLocalMediaRecording is called only once per connect sequence
                let mediaRecorderStarted = false;
                socket.once('connect', () => {
                    if (!mediaRecorderStarted) {
                        console.log("Socket.IO connected, proceeding to start MediaRecorder.");
                        verseDisplay.textContent = 'Recording (Socket.IO)... Speak into mic.';
                        startLocalMediaRecording(stream);
                        mediaRecorderStarted = true;
                    }
                });
                // If already connected from a previous session (e.g. page not reloaded),
                // or if connectSocket() immediately connects (less likely for new connections):
                if (socket && socket.connected && !mediaRecorderStarted) {
                     console.log("Socket.IO already connected (or connected very quickly), proceeding to start MediaRecorder.");
                     verseDisplay.textContent = 'Recording (Socket.IO)... Speak into mic.';
                     startLocalMediaRecording(stream);
                     mediaRecorderStarted = true;
                }
            } else { // Socket already exists and is connected
                 console.log("Socket.IO already connected, proceeding to start MediaRecorder.");
                 verseDisplay.textContent = 'Recording (Socket.IO)... Speak into mic.';
                 startLocalMediaRecording(stream);
            }

        } catch (err) {
            console.error('Error getting media or starting recording:', err);
            verseDisplay.textContent = 'Error setting up audio. See console.';
            isRecording = false; // Reset state
            micButton.textContent = 'Start Microphone';
        }
    } else { // Stop recording
        micButton.textContent = 'Start Microphone';
        isRecording = false;
        // verseDisplay.textContent = 'Stopping recording...'; // UI update handled by socket.disconnect or locally

        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
        } else { // If mediaRecorder wasn't even started or already stopped
             if (streamReference) {
                streamReference.getTracks().forEach(track => track.stop());
                streamReference = null;
            }
        }

        if (socket && socket.connected) {
            console.log('Socket.IO: Emitting client_stopped_recording.');
            socket.emit('client_stopped_recording', { reason: 'user_clicked_stop' });
            // Optional: socket.disconnect(); // Or let server manage based on activity
        }
        verseDisplay.textContent = 'Recording stopped (Socket.IO). Ready to start.';
    }
});


function startLocalMediaRecording(stream) {
    const options = { mimeType: 'audio/webm;codecs=opus' };
    try {
        mediaRecorder = new MediaRecorder(stream, options);
    } catch (e) {
        console.warn("Opus over WebM not supported, falling back to default", e);
        mediaRecorder = new MediaRecorder(stream);
    }

    mediaRecorder.ondataavailable = event => {
            if (event.data.size > 0 && socket && socket.connected) {
            // console.log('Socket.IO: Sending audio chunk. Size:', event.data.size); // Can be verbose
            socket.emit('audio_chunk', event.data);
        }
    };

    mediaRecorder.onstop = () => {
        console.log('MediaRecorder stopped.');
        // Ensure mic is released if not already
        if (streamReference) {
            streamReference.getTracks().forEach(track => track.stop());
            streamReference = null;
        }
        // UI is typically updated by the main stop recording logic or disconnect handler
    };

    mediaRecorder.start(1000); // Start with timeslice
}
