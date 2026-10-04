"""Catálogo listável: formatos, fontes do kit, sons, efeitos e grades.

Uso:
    python helpers/catalogo.py
    python helpers/catalogo.py fontes
    python helpers/catalogo.py sons
"""
from __future__ import annotations

import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ASSETS = AQUI.parent / "assets"

FORMATOS = {
    "16:9": {"largura": 1920, "altura": 1080, "uso": "YouTube, aula, webinar"},
    "9:16": {"largura": 1080, "altura": 1920, "uso": "Reels, Shorts, Stories"},
    "1:1": {"largura": 1080, "altura": 1080, "uso": "feed quadrado"},
    "4:5": {"largura": 1080, "altura": 1350, "uso": "feed Instagram vertical"},
    "21:9": {"largura": 2560, "altura": 1080, "uso": "cinemático / banner"},
}

EFEITOS = {
    "abertura": {
        "none": "sem abertura",
        "crt": "TV liga/desliga (tv_effect)",
        "fade": "fade in/out suave",
    },
    "emenda": {
        "none": "corte seco",
        "glitch": "glitch CRT/VHS na emenda",
        "flash": "flash branco rápido na emenda",
        "whip": "whip pan sintético (rgbashift forte)",
    },
    "intensidade": ["subtle", "medium", "strong"],
}

GRADES = [
    "none",
    "subtle",
    "neutral_punch",
    "warm_cinematic",
    "cool_night",
    "teal_orange",
    "high_contrast",
    "soft_pastel",
    "noir",
    "vivid_social",
    "documentary",
]

FONTES_KIT = {
    "montserrat": "Montserrat[wght].ttf#Black",
    "ibm": "IBMPlexMono-Regular.ttf",
    "bebas": "BebasNeue-Regular.ttf",
    "oswald": "Oswald[wght].ttf#Bold",
    "space": "SpaceGrotesk[wght].ttf#Bold",
    "outfit": "Outfit[wght].ttf#Bold",
    "archivo": "ArchivoBlack-Regular.ttf",
    "rubik": "Rubik[wght].ttf#Black",
    "barlow": "BarlowCondensed-Bold.ttf",
    "anton": "Anton-Regular.ttf",
    "bangers": "Bangers-Regular.ttf",
    "syne": "Syne[wght].ttf#Bold",
    "rajdhani": "Rajdhani-Bold.ttf",
    "teko": "Teko[wght].ttf#Bold",
    "blackops": "BlackOpsOne-Regular.ttf",
    "kanit": "Kanit-Bold.ttf",
}

SONS = {
    "tick": "marcação curta",
    "click": "clique seco",
    "impacto": "hit baixo",
    "whoosh": "passagem",
    "transicao": "transição suave",
    "riser": "subida para CTA",
    "pop": "pop curto",
    "bass": "thump grave",
    "swoosh": "varredura pink noise",
    "glitch": "estalo digital",
}


def fontes_paths() -> dict[str, Path]:
    base = ASSETS / "fontes"
    out: dict[str, Path] = {}
    for nome, arq in FONTES_KIT.items():
        file = arq.split("#", 1)[0]
        out[nome] = base / file
    return out


def sons_paths() -> dict[str, Path]:
    base = ASSETS / "sons"
    return {nome: base / f"{nome}.wav" for nome in SONS}


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser(description="Catálogo do kit de edição")
    ap.add_argument(
        "parte",
        nargs="?",
        choices=["formatos", "fontes", "sons", "efeitos", "grades", "tudo"],
        default="tudo",
    )
    args = ap.parse_args()
    data = {
        "formatos": FORMATOS,
        "fontes": FONTES_KIT,
        "sons": SONS,
        "efeitos": EFEITOS,
        "grades": GRADES,
    }
    if args.parte == "tudo":
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(data[args.parte], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
