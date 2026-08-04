from audio.audio_stream import AudioStream
from audio.energy_tracker import EnergyTracker

stream = AudioStream()
tracker = EnergyTracker()

stream.start()

print("Listening...\n")

try:

    for frame in stream.frames():

        energy = tracker.process(frame)

        print(
            f"RMS : {energy.rms:.5f} | Peak : {energy.peak:.5f}"
        )

except KeyboardInterrupt:

    stream.stop()