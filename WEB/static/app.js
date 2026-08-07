let audioContext;
let micStream;
let audioWorkletNode;
let outProcessorNode;
let socket;
let isRecording = false;
let currentChordName = null;

// UI Elements
const startBtn = document.getElementById('start-btn');
const statusText = document.getElementById('status-text');
const chordDisplay = document.getElementById('current-chord');
const scaleBadge = document.getElementById('scale-badge');
const visualizerBars = document.querySelector('.visualizer-bars');
const bars = document.querySelectorAll('.bar');

// Handle WebSocket messages from backend
function handleWebSocketMessage(event) {
    if (event.data instanceof ArrayBuffer) {
        // Binary audio chunk from the Python RealtimeSynth
        if (outProcessorNode) {
            const float32Array = new Float32Array(event.data);
            outProcessorNode.port.postMessage(float32Array);
        }
        return;
    }

    const data = JSON.parse(event.data);
    
    if (data.type === "chord") {
        const chordStr = data.chord;
        
        // Update UI
        if (currentChordName !== chordStr) {
            currentChordName = chordStr;
            chordDisplay.textContent = chordStr;
            
            // Pop animation
            chordDisplay.classList.remove('pop');
            void chordDisplay.offsetWidth; // trigger reflow
            chordDisplay.classList.add('pop');
        }
    } else if (data.type === "key_locked") {
        scaleBadge.textContent = "Key: " + data.key;
        scaleBadge.classList.add('locked');
        statusText.textContent = "Accompaniment Active";
    }
}

// Connect to WebSocket and start audio pipeline
async function startSession() {
    try {
        // 1. Establish WebSocket connection
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        socket = new WebSocket(`${protocol}//${window.location.host}/ws/omni`);
        socket.binaryType = "arraybuffer"; // Important: Receive binary data as ArrayBuffer
        
        socket.onopen = async () => {
            console.log("WebSocket connected");
            statusText.textContent = "Listening... (Sing for 8s)";
            scaleBadge.textContent = "Detecting Scale...";
            scaleBadge.classList.add('visible');
            scaleBadge.classList.remove('locked');
            visualizerBars.classList.add('active');

            // 2. Get Microphone Access
            micStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
            audioContext = new (window.AudioContext || window.webkitAudioContext)({
                sampleRate: 44100 // Force match Python backend
            });

            // 3. Load the AudioWorklet Processors
            await audioContext.audioWorklet.addModule('/static/processor.js');
            await audioContext.audioWorklet.addModule('/static/out_processor.js');

            const source = audioContext.createMediaStreamSource(micStream);
            audioWorkletNode = new AudioWorkletNode(audioContext, 'mic-processor');
            
            outProcessorNode = new AudioWorkletNode(audioContext, 'out-processor');
            outProcessorNode.connect(audioContext.destination);

            // 4. Send chunks to the backend
            audioWorkletNode.port.onmessage = (event) => {
                const pcmData = event.data; // Float32Array
                
                // Animate visualizer slightly based on data
                if (Math.random() > 0.8) {
                    const rms = Math.sqrt(pcmData.reduce((acc, val) => acc + val * val, 0) / pcmData.length);
                    const height = Math.min(100, rms * 1000); // arbitrary scaling
                    bars.forEach(bar => {
                        bar.style.height = `${4 + Math.random() * height}px`;
                    });
                }

                if (socket.readyState === WebSocket.OPEN) {
                    // Send raw bytes to WebSocket
                    socket.send(pcmData.buffer);
                }
            };

            source.connect(audioWorkletNode);
        };

        socket.onmessage = handleWebSocketMessage;
        
        socket.onclose = () => {
            console.log("WebSocket closed");
            stopSession();
        };

        // Update UI
        isRecording = true;
        startBtn.textContent = "Stop Singing";
        startBtn.classList.add('recording');

    } catch (err) {
        console.error("Error starting session:", err);
        alert("Microphone access denied or WebSocket error.");
        stopSession();
    }
}

function stopSession() {
    isRecording = false;
    startBtn.textContent = "Start Singing";
    startBtn.classList.remove('recording');
    statusText.textContent = "Ready to listen.";
    chordDisplay.textContent = "--";
    scaleBadge.classList.remove('visible');
    visualizerBars.classList.remove('active');
    
    if (audioWorkletNode) {
        audioWorkletNode.disconnect();
        audioWorkletNode = null;
    }
    
    if (outProcessorNode) {
        outProcessorNode.disconnect();
        outProcessorNode = null;
    }
    
    if (audioContext) {
        audioContext.close();
        audioContext = null;
    }
    
    if (micStream) {
        micStream.getTracks().forEach(track => track.stop());
        micStream = null;
    }

    if (socket) {
        socket.close();
        socket = null;
    }
    
    bars.forEach(bar => bar.style.height = '4px');
}

startBtn.addEventListener('click', () => {
    if (isRecording) {
        stopSession();
    } else {
        startSession();
    }
});
