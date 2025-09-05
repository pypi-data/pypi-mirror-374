try:
    from .process import *
except:
    from process import *

import os


def annote(
    input_path: str
):

    fnames = [os.path.splitext(f)[0] for f in os.listdir(input_path) if f.endswith('.wav')]


    for fname in fnames:
        wav_path = os.path.join(input_path, fname + ".wav")
        tg_path = wav_path.replace(".wav", "_whisper.TextGrid")
        vad_path = wav_path.replace(".wav", "_VAD.TextGrid")

        transcribe_wav_file(wav_path, vad=vad_path)
        word_timestamp(wav_path, tg_path)


if __name__ == "__main__":
    annote(
        input_path=os.path.abspath("data")
    )