"""Auto-teste do mixa. Um comando, um vídeo de três segundos.

    tools/video-use/.venv/bin/python tools/video-use/helpers/test_mixa.py

O mixa é o último passo do som, e o defeito dele só aparece no fim do vídeo,
onde ninguém mais está olhando.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import ff


def _dura(p: Path, faixa: str) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", faixa, "-show_entries",
                        "stream=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
    return float(r.stdout.strip())


def _amostras(p: Path) -> np.ndarray:
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-ac", "1", "-ar", "48000",
                        "-f", "f32le", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32)


def test_a_fala_acaba_antes_e_o_audio_vai_ate_o_fim(tmp: Path):
    """Voz sintética acaba antes da imagem: no Eleven v4 a chamada fica 0,5 s parada
    depois da última palavra. O amix seguia a voz, e a trilha cortava seco 0,34 s
    antes do fim, no meio do fade. O áudio tem que cobrir o vídeo, e a trilha
    tem que chegar no fim já apagada."""
    video = tmp / "reel.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error",
                    "-f", "lavfi", "-i", "testsrc=size=320x568:rate=30:duration=3",
                    "-f", "lavfi", "-i", "sine=frequency=300:duration=2",
                    "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", str(video)], check=True)
    trilha = tmp / "trilha.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
                    "sine=frequency=660:duration=6", str(trilha)], check=True)
    assert _dura(video, "a:0") < 2.1, "o vídeo de teste devia ter a voz mais curta"

    out = tmp / "final.mp4"
    subprocess.run([sys.executable, str(AQUI / "mixa.py"), str(video), "--trilha", str(trilha),
                    "--fade-fim", "0.5", "-o", str(out)], check=True, capture_output=True)

    imagem, som = _dura(out, "v:0"), _dura(out, "a:0")
    assert som >= imagem - 0.05, f"o áudio acaba em {som:.2f}s e a imagem em {imagem:.2f}s"
    x = _amostras(out)
    rms = lambda a, b: float(np.sqrt((x[int(a * 48000):int(b * 48000)] ** 2).mean()))
    so_trilha, fim = rms(2.2, 2.4), rms(imagem - 0.08, imagem - 0.02)
    assert so_trilha > 1e-3, f"depois da fala a trilha devia soar sozinha: {so_trilha}"
    assert fim < so_trilha / 10, f"a trilha chega no fim sem fade: {fim:.4f} contra {so_trilha:.4f}"


def test_trilha_da_raiz_de_qualquer_pasta(tmp: Path):
    """O plano escreve `trilha.faixa` a partir da raiz da pasta, e o resolver só procurava na
    pasta de quem rodou: de outra, o --seco do exemplo do reel editorial caía em "trilha não achada"."""
    import os
    import mixa
    rel = Path(mixa.__file__).resolve().relative_to(mixa.RAIZ)
    antes = os.getcwd()
    os.chdir(tmp)
    try:
        assert mixa.resolver(str(rel)) == mixa.RAIZ / rel, mixa.resolver(str(rel))
    finally:
        os.chdir(antes)


def test_escolhe_a_do_clima_ha_mais_tempo_sem_tocar(tmp: Path):
    """Em 03/10 a mesma faixa tocava em doze vídeos. Cada vídeo novo leva a do clima que está há
    mais tempo sem tocar; o mesmo vídeo leva sempre a mesma; o seco não marca; clima sem faixa
    (o kit, que não leva as nossas) devolve None e o vídeo segue sem trilha, como antes."""
    import json
    import mixa
    (tmp / "eleven").mkdir()
    (tmp / "eleven" / "catalogo.json").write_text(json.dumps({"faixas": [
        {"nome": "a1", "clima": "a", "arquivo": "a1.m4a"},
        {"nome": "a2", "clima": "a", "arquivo": "a2.m4a"},
        {"nome": "a3", "clima": "a"},                      # ainda não gerada
        {"nome": "b1", "clima": "b", "arquivo": "b1.m4a"}]}), encoding="utf-8")
    antes = mixa.MUSICA, mixa.USADAS
    mixa.MUSICA, mixa.USADAS = tmp, tmp / "usadas.json"
    try:
        nome = lambda clima, video, grava=True: Path(mixa.escolhe(clima, video, grava)).stem
        assert [nome("a", v) for v in ("v1", "v2", "v3")] == ["a1", "a2", "a1"]
        assert nome("a", "v1") == "a1", "o mesmo vídeo trocou de música"
        assert nome("a", "v4", grava=False) == "a2" and nome("a", "v5", grava=False) == "a2", "o seco marcou"
        assert nome("b", "v4") == "b1"
        assert mixa.escolhe("c", "v4") is None
        assert len(json.loads(mixa.USADAS.read_text(encoding="utf-8"))) == 4
    finally:
        mixa.MUSICA, mixa.USADAS = antes


def main() -> int:
    casos = [
        ("o áudio vai até o fim da imagem", test_a_fala_acaba_antes_e_o_audio_vai_ate_o_fim),
        ("trilha da raiz, de outra pasta",  test_trilha_da_raiz_de_qualquer_pasta),
        ("rodízio da trilha por clima",     test_escolhe_a_do_clima_ha_mais_tempo_sem_tocar),
    ]
    falhas = []
    with tempfile.TemporaryDirectory() as td:
        for nome, caso in casos:
            sub = Path(td) / nome.replace(" ", "_")
            sub.mkdir()
            try:
                caso(sub)
                print(f"  ok   {nome}")
            except Exception as e:
                falhas.append((nome, e))
                print(f"  FALHA {nome}: {e}")
    print(f"\n{len(casos) - len(falhas)}/{len(casos)} passaram")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
