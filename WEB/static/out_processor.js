/**
 * AudioWorkletProcessor to smoothly play streaming PCM data.
 * It uses a simple ring buffer to absorb slight network jitter.
 */
class OutProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this.buffer = new Float32Array(44100 * 2); // 2 second max buffer
        this.readIndex = 0;
        this.writeIndex = 0;
        
        // Receive audio chunks from the main thread
        this.port.onmessage = (event) => {
            const incoming = event.data;
            for (let i = 0; i < incoming.length; i++) {
                this.buffer[this.writeIndex] = incoming[i];
                this.writeIndex = (this.writeIndex + 1) % this.buffer.length;
            }
        };
    }

    process(inputs, outputs, parameters) {
        const output = outputs[0];
        const channel = output[0];

        for (let i = 0; i < channel.length; i++) {
            if (this.readIndex !== this.writeIndex) {
                channel[i] = this.buffer[this.readIndex];
                this.readIndex = (this.readIndex + 1) % this.buffer.length;
            } else {
                channel[i] = 0; // Buffer underrun, play silence
            }
        }

        return true;
    }
}

registerProcessor('out-processor', OutProcessor);
