"""Auto-teste do avatar montado de um lote. Nada sai da máquina: a cena "baixada" é feita aqui.

    tools/video-use/.venv/bin/python tools/video-use/helpers/test_avatar_lote.py

O que se cobra: a fatia da voz tem a duração da cena (com silêncio quando a voz acaba antes), o verde
da cena vira alfa e a pessoa fica, e a cena que falta entra como marcador na janela dela.
"""
from __future__ import annotations

import json
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))

import avatar_lote as al
import ff


def _lote(d: Path) -> Path:
    with wave.open(str(d / "voz.wav"), "wb") as w:            # 1 s de voz
        w.setparams((1, 2, 48000, 0, "NONE", "not compressed"))
        w.writeframes(b"\1\0" * 48000)
    Image.new("RGBA", (200, 300), (90, 60, 40, 255)).save(d / "foto.png")
    # a cena baixada: verde liso com a "pessoa" (um retângulo cinza) no meio
    ff.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=0x1fb34a:s=360x640:r=30:d=2",
            "-vf", "drawbox=x=120:y=200:w=120:h=240:color=gray:t=fill", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            str(d / "fala.mp4")], quiet=True)
    arq = d / "lote.json"
    arq.write_text(json.dumps({"voz": "voz.wav", "dur": 1.5, "marcador": "foto.png", "cenas": {
        "fala": {"modelo": "fala", "voz": [0.5, 2.5], "audio": "fatias/fala.wav", "janela": [0.6, 1.0]},
        "falta": {"modelo": "fala", "voz": [1.0, 3.0], "audio": "fatias/falta.wav", "janela": [1.0, 1.5],
                  "acao": "estala os dedos"}}}), encoding="utf-8")
    return arq


def main() -> None:
    with tempfile.TemporaryDirectory() as t:
        lo = al.ler(_lote(Path(t)))
        al.fatias(lo)
        with wave.open(str(Path(t) / "fatias" / "fala.wav")) as w:
            assert w.getnframes() == 2 * 48000, "a fatia dura a cena inteira, com silêncio depois da voz"
            q = np.frombuffer(w.readframes(w.getnframes()), np.int16)
            assert q[:24000].all() and not q[24000:].any(), "meio segundo de voz e o resto em silêncio"

        out = al.monta(lo)
        assert abs(ff.dur(out) - 1.5) < 0.1, ff.dur(out)
        raw = ff.run(["ffmpeg", "-v", "error", "-c:v", "libvpx-vp9", "-i", str(out), "-vf", "fps=10",
                      "-f", "rawvideo", "-pix_fmt", "rgba", "-"], capture=True, binario=True, quiet=True).stdout
        q = np.frombuffer(raw, np.uint8).reshape(-1, al.H, al.W, 4)
        assert q[2, ..., 3].max() == 0, "antes da primeira janela, nada"
        assert q[8, 50, 50, 3] < 30 and q[8, al.H // 2, al.W // 2, 3] > 220, "o verde vira alfa, a pessoa fica"
        assert q[12, ..., 3].mean() > q[8, ..., 3].mean(), "a cena que falta entra como marcador"
        f = Image.open(al.foto(lo, "fala", 0.5))
        assert f.size == (120, 240) and f.getchannel("A").getpixel((60, 120)) == 255, "a foto é a pessoa, sem verde"
    print("ok: test_avatar_lote")


if __name__ == "__main__":
    main()
