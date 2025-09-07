import pylabeador.errors
import pylabeador.syllabify
from src.pylabeador import pylabeador

errors = []
with open("commonspanish") as fin, open("spanish-hyphens.txt", "w") as fout:
    for i, line in enumerate(fin):
        text = line.strip()
        print(i, text)
        try:
            w = pylabeador.syllabify.hyphenate(text)
            print(f"{w.original_word} {w.hyphenated} {w.stressed}", file=fout)
        except pylabeador.errors.HyphenatorError as e:
            errors.append(str(e))
print("DONE")

if errors:
    print("With errors:")
    for err in errors:
        print(err)
