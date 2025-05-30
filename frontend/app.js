const micButton = document.getElementById('micButton');
const verseDisplay = document.getElementById('verseDisplay');
let isRecording = false;
let mediaRecorder;
let audioChunks = [];
let streamReference; // To keep track of the stream for stopping tracks

micButton.addEventListener('click', async () => {
    if (!isRecording) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            streamReference = stream; // Save stream reference
            console.log('Microphone access granted');
            micButton.textContent = 'Stop Microphone';
            isRecording = true;
            audioChunks = []; // Clear previous chunks

            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                console.log('Recording stopped');
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                audioChunks = []; // Clear chunks after creating blob

                const formData = new FormData();
                formData.append('audio_file', audioBlob, 'recording.webm');

                try {
                    verseDisplay.textContent = 'Sending audio to backend...';
                    const response = await fetch('/api/audio', {
                        method: 'POST',
                        body: formData
                    });
                    const responseData = await response.json();
                    if (response.ok) {
                        console.log('Audio process response:', responseData);
                        const verse = responseData.found_verse;
                        if (verse) {
                            verseDisplay.innerHTML = `
                                <h3>Verse Found (Placeholder)</h3>
                                <p><strong>Gurmukhi:</strong> ${verse.verse_gurmukhi}</p>
                                <p><strong>Meaning:</strong> ${verse.meaning_english}</p>
                                <p><strong>Source:</strong> ${verse.source_page}</p>
                                <hr>
                                <p><small><em>Transcribed (Placeholder): ${responseData.transcribed_text}</em></small></p>
                            `;
                        } else {
                            verseDisplay.textContent = 'Verse data not found in response, though audio processed.';
                        }
                    } else {
                        console.error('Failed to process audio:', responseData);
                        verseDisplay.textContent = `Error: ${responseData.message || 'Failed to process audio.'}`;
                    }
                } catch (err) {
                    console.error('Error sending/processing audio:', err);
                    verseDisplay.textContent = 'Error sending audio to backend or processing it.';
                }
            };

            mediaRecorder.start();
            console.log('Recording started');
            verseDisplay.textContent = 'Recording... Speak into the microphone.';

        } catch (err) {
            console.error('Microphone access denied:', err);
            verseDisplay.textContent = 'Microphone access denied. Please allow microphone access in your browser settings.';
        }
    } else {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
        }
        if (streamReference) {
            streamReference.getTracks().forEach(track => track.stop()); // Stop microphone stream
            streamReference = null;
        }
        micButton.textContent = 'Start Microphone';
        isRecording = false;
    }
});
