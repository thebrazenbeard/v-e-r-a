from __future__ import annotations

import argparse
import json
import wave

import numpy as np

from .acoustics import acoustic_fingerprint


def _read_wav(path: str) -> tuple[np.ndarray, int]:
    with wave.open(path, "rb") as w:
        channels = w.getnchannels()
        width = w.getsampwidth()
        sr = w.getframerate()
        frames = w.readframes(w.getnframes())

    if width == 1:
        x = np.frombuffer(frames, dtype=np.uint8).astype(np.float64)
        x = (x - 128.0) / 128.0
    elif width == 2:
        x = np.frombuffer(frames, dtype="<i2").astype(np.float64) / 32768.0
    elif width == 4:
        x = np.frombuffer(frames, dtype="<i4").astype(np.float64) / 2147483648.0
    else:
        raise ValueError(f"unsupported PCM sample width: {width}")

    if channels > 1:
        x = x.reshape(-1, channels).mean(axis=1)
    return x, sr


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract a UNVTRSLR acoustic fingerprint from a PCM WAV file."
    )
    parser.add_argument("wav")
    parser.add_argument("--indent", type=int, default=2)
    args = parser.parse_args()
    x, sr = _read_wav(args.wav)
    print(json.dumps(acoustic_fingerprint(x, sr), indent=args.indent, sort_keys=True))


if __name__ == "__main__":
    main()
