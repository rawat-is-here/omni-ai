from audio.audio_stream import AudioStream
from audio.energy_tracker import EnergyTracker
from audio.voice_activity import VoiceActivityDetector

stream = AudioStream()
energy_tracker = EnergyTracker()
vad = VoiceActivityDetector()

stream.start()

print("Speak or sing into the microphone...\n")

try:

    for frame in stream.frames():

        energy = energy_tracker.process(frame)

        voice = vad.process(energy)

        print(
            f"RMS={energy.rms:.5f} | "
            f"Voice={voice.is_voiced} | "
            f"Confidence={voice.confidence:.2f}"
        )

except KeyboardInterrupt:

    stream.stop()