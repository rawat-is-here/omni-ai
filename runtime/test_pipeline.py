from runtime.audio_pipeline import AudioPipeline

pipeline = AudioPipeline()

pipeline.start()

print("Sing...")

for note in pipeline.notes():

    print(note)