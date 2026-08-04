from dataclasses import dataclass

@dataclass(slots=True)
class HarmonyContext:

    recent_notes: list

    phrase_info: object | None

    rhythm_info: object | None

    scale_result: object | None

    key_result: object | None

    tempo: float | None

    beat_position: float | None
class HarmonyContextBuilder:

    def __init__(self):

        self.phrase = PhraseAnalyzer()

        self.rhythm = RhythmTracker()

        self.scale = ScaleDetector()
    def build(
        self,
        memory: MusicMemory,
    ) -> HarmonyContext:

        phrase = self.phrase.analyze(memory)

        rhythm = self.rhythm.analyze(memory)

        scale = self.scale.detect(memory)

        return HarmonyContext(

            recent_notes=memory.get_notes(),

            phrase_info=phrase,

            rhythm_info=rhythm,

            scale_result=scale,

            key_result=None,

            tempo=None,

            beat_position=None,
        )
