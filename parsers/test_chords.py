from parsers.chord_extractor import ChordExtractor

extractor = ChordExtractor()

tests = [

    "C:maj",

    "A:min",

    "G:7",

    "F:maj7",

    "D:min7",

    "Bb:maj",

    "Eb:min",

    "N",

]

for chord in tests:

    result = extractor.from_name(chord, 0, 2)

    print(chord, "->", result)