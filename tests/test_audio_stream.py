from audio.audio_stream import AudioStream


stream = AudioStream()

stream.start()

print("Listening...\n")

try:

    for frame in stream.frames():

        print(
            frame.frame_index,
            frame.timestamp,
            len(frame.samples)
        )

except KeyboardInterrupt:

    stream.stop()