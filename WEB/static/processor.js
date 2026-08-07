/**
 * AudioWorkletProcessor to safely capture raw audio from the mic
 * without blocking the main UI thread.
 */
class MicProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        // We want to send chunks of 1024 samples to match the backend BUFFER_SIZE
        this.bufferSize = 1024;
        this.buffer = new Float32Array(this.bufferSize);
        this.framesRecorded = 0;
    }

    process(inputs, outputs, parameters) {
        // We only care about the first input (microphone)
        const input = inputs[0];
        if (!input || !input.length) return true;

        // Get the first channel (mono)
        const channel = input[0];
        
        for (let i = 0; i < channel.length; i++) {
            this.buffer[this.framesRecorded] = channel[i];
            this.framesRecorded++;

            // When buffer is full, post it to the main thread and reset
            if (this.framesRecorded === this.bufferSize) {
                // Send a copy of the buffer
                this.port.postMessage(this.buffer.slice());
                this.framesRecorded = 0;
            }
        }

        // Keep the processor alive
        return true;
    }
}

registerProcessor('mic-processor', MicProcessor);
