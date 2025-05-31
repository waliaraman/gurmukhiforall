const micButton = document.getElementById('micButton');
const verseDisplay = document.getElementById('verseDisplay');
let isRecording = false;
let mediaRecorder;
// let audioChunks = []; // We send chunks directly now for streaming
let streamReference;
let socket; // WebSocket variable

micButton.addEventListener('click', async () => {
    if (!isRecording) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            streamReference = stream;
            console.log('Microphone access granted');
            micButton.textContent = 'Stop Microphone';
            isRecording = true;
            verseDisplay.textContent = 'Connecting to WebSocket...';

            // Establish WebSocket connection
            socket = new WebSocket('ws://localhost:5001/api/audio_stream'); // Ensure port matches backend

            socket.onopen = () => {
                console.log('WebSocket connection established.');
                verseDisplay.textContent = 'Recording... Speak into microphone (streaming).';

                // Start MediaRecorder
                // Options to match typical streaming scenarios, like Opus in WebM
                const options = { mimeType: 'audio/webm;codecs=opus' };
                try {
                    mediaRecorder = new MediaRecorder(stream, options);
                } catch (e) {
                    console.warn("Opus over WebM not supported, falling back to default", e);
                    mediaRecorder = new MediaRecorder(stream); // Fallback to default
                }


                mediaRecorder.ondataavailable = event => {
                    if (event.data.size > 0 && socket && socket.readyState === WebSocket.OPEN) {
                        console.log('Sending audio chunk over WebSocket:', event.data);
                        socket.send(event.data);
                    }
                };

                mediaRecorder.onstop = () => { // This onstop is for the MediaRecorder itself
                    console.log('MediaRecorder stopped.');
                    if (streamReference) { // Ensure tracks are stopped if not already
                        streamReference.getTracks().forEach(track => track.stop());
                        streamReference = null;
                    }
                };

                // Start recording with a timeslice to get chunks, e.g., every second
                mediaRecorder.start(1000);
                console.log('MediaRecorder started with 1s timeslice.');
            };

            // Keep a variable to store the latest transcription to display alongside verse
            let latestTranscription = "";

            socket.onmessage = event => {
                try {
                    const messageData = JSON.parse(event.data);
                    console.log('WebSocket received JSON message:', messageData);

                    if (messageData.type === 'transcription_update' && messageData.text) {
                        latestTranscription = messageData.text;
                        verseDisplay.innerHTML = `
                            <p><strong>Live Transcription (Placeholder):</strong> ${latestTranscription}</p>
                            <p><em>Searching for verse...</em></p>
                        `;
                    } else if (messageData.type === 'verse_update' && messageData.data) {
                        const verse = messageData.data;
                        verseDisplay.innerHTML = `
                            <h3>Verse Found (Streamed Placeholder)</h3>
                            <p><strong>Gurmukhi:</strong> ${verse.verse_gurmukhi}</p>
                            <p><strong>Meaning:</strong> ${verse.meaning_english}</p>
                            <p><strong>Source:</strong> ${verse.source_page}</p>
                            <hr>
                            <p><small><em>Based on transcription (Placeholder): ${latestTranscription}</em></small></p>
                        `;
                    } else if (messageData.type === 'error' && messageData.message) {
                        console.error('Backend error message:', messageData.message);
                        verseDisplay.innerHTML = `<p style="color: red;">Error from backend: ${messageData.message}</p>`;
                    } else {
                        console.log('WebSocket received other data:', event.data);
                    }
                } catch (e) {
                    console.warn('WebSocket received non-JSON message or processing error:', event.data, e);
                    if (event.data instanceof Blob) {
                        console.log('WebSocket received Blob (likely echo, ignoring). Size:', event.data.size);
                    }
                }
            };

            socket.onerror = error => {
                console.error('WebSocket error:', error);
                verseDisplay.textContent = 'WebSocket error. See console for details.';
                isRecording = false;
                micButton.textContent = 'Start Microphone';
                if (mediaRecorder && mediaRecorder.state === 'recording') {
                    mediaRecorder.stop();
                }
                 if (streamReference) {
                    streamReference.getTracks().forEach(track => track.stop());
                    streamReference = null;
                }
            };

            socket.onclose = event => {
                console.log('WebSocket connection closed:', event.code, event.reason);
                if (isRecording) { // If closed unexpectedly
                    verseDisplay.textContent = 'WebSocket closed. Click Start to retry.';
                    isRecording = false;
                    micButton.textContent = 'Start Microphone';
                }
                if (mediaRecorder && mediaRecorder.state === 'recording') {
                    mediaRecorder.stop();
                }
                 if (streamReference) {
                    streamReference.getTracks().forEach(track => track.stop());
                    streamReference = null;
                }
            };

        } catch (err) {
            console.error('Error getting media or starting WebSocket:', err);
            verseDisplay.textContent = 'Error setting up audio streaming. See console.';
            isRecording = false;
            micButton.textContent = 'Start Microphone';
        }
    } else { // Stop recording
        micButton.textContent = 'Start Microphone';
        isRecording = false;
        verseDisplay.textContent = 'Stopping recording...';

        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop(); // This will trigger ondataavailable for any remaining data, then onstop
        }

        if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
            // Send a signal that client is stopping, or just close.
            // For this iteration, just closing is fine. The backend will see ws.receive() return None.
            console.log('Closing WebSocket connection.');
            socket.close();
        }


        if (streamReference) { // Should be stopped by mediaRecorder.onstop or socket.onclose, but ensure
            streamReference.getTracks().forEach(track => track.stop());
            streamReference = null;
        }
        verseDisplay.textContent = 'Recording stopped. Ready to start again.';
    }
});
