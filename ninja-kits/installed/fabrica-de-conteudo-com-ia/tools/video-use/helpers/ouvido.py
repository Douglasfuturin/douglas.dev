#!/usr/bin/env python3
"""O ouvido: um modelo que escuta o áudio, dos dois lados do corte.

O whisper escreve a frase como devia ser: apaga o falso começo ("olha esses
cri- olha esses criativos" vira um "criativos" de 1s) e completa a palavra
cortada ("treina-" vira "treinamento"). O `clean_edl` lê esse texto, então não
enxerga nenhum dos dois. Em 22/09/2026 o V1 da VSL do Hermes saiu com quatro
gaguejadas e com os centavos das três versões do preço cortados; um modelo que
ouve achou tudo por centavos.

    python ouvido.py planeja take.wav      # antes: falso começo e retake, com --drop sugerido
    python ouvido.py confere limpo.wav     # depois: reprova se sobrou tropeço

`confere` roda N passadas independentes e só aceita o que aparece em pelo menos
duas: uma passada sozinha inventa. Cada ponto aceito ainda passa por uma
transcrição literal cega em volta dele — o revisor que procura problema inventa
perto de emenda. Sai com código 1 se sobrar ponto de gravidade
2 ou mais — é trava, não relatório. Sem OPENROUTER_API_KEY, avisa e sai com 0:
o ouvido é rede de segurança, não pré-requisito do corte.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import tempfile
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

MODELO = "google/gemini-3.8-flash"
TIPOS = ["gagueira", "palavra_comida", "corte_audivel", "frase_confusa", "pronuncia", "ruido", "volume"]

PROBLEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["t", "tipo", "trecho", "gravidade"],
    "properties": {
        "t": {"type": "string", "description": "mm:ss.s"},
        "tipo": {"type": "string", "enum": TIPOS},
        "trecho": {"type": "string", "description": "exatamente como soa, com '-' na palavra cortada"},
        "gravidade": {"type": "integer", "description": "1 leve, 2 quem presta atenção nota, 3 qualquer um nota"},
    },
}
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["problemas"],
          "properties": {"problemas": {"type": "array", "items": PROBLEMA}}}

PEDIDO = {
    "confere": (
        "Você é revisor de áudio de um vídeo em português brasileiro, uma pessoa falando, já "
        "editado (as pausas foram cortadas). Ouça INTEIRO e liste cada ponto onde quem ouve "
        "tropeça: gagueira, palavra repetida, frase que recomeça, palavra comida ou cortada no "
        "meio, emenda brusca, frase que de ouvido não faz sentido, ruído, salto de volume. "
        "Dê o tempo (mm:ss.s) e o trecho exato como soa. Não invente: sem problema, não liste. "
        "Não comente conteúdo nem estilo."),
    "planeja": (
        "Você vai ajudar a editar um take BRUTO de narração em português brasileiro. Ouça INTEIRO "
        "e liste cada falso começo, gaguejada, frase refeita e retake — tudo que um editor "
        "cortaria. Dê o tempo (mm:ss.s) do COMEÇO do trecho a jogar fora e, no trecho, o que é "
        "dito até o recomeço bom (ex.: 'olha esses cri-'). Use o tipo 'gagueira' para os dois "
        "casos. Não liste pausa nem respiração."),
}


def segundos(t: str) -> float:
    m, _, s = t.strip().partition(":")
    return float(m) * 60 + float(s) if s else float(m)


def consenso(passadas: list[list[dict]], janela: float = 2.0, minimo: int = 2) -> list[dict]:
    """Pontos que aparecem em pelo menos `minimo` passadas, a menos de `janela`
    segundos um do outro. Devolve um por grupo, com a maior gravidade vista."""
    todos = sorted((segundos(p["t"]), i, p) for i, ps in enumerate(passadas) for p in ps)
    grupos: list[list] = []
    for t, i, p in todos:
        if grupos and t - grupos[-1][-1][0] <= janela:
            grupos[-1].append((t, i, p))
        else:
            grupos.append([(t, i, p)])
    out = []
    for g in grupos:
        if len({i for _, i, _ in g}) >= minimo:
            t, _, p = g[len(g) // 2]
            out.append({**p, "s": round(t, 1), "gravidade": max(x["gravidade"] for _, _, x in g),
                        "passadas": len({i for _, i, _ in g})})
    return out


def _mp3(fonte: Path, ini: float | None = None, dur: float | None = None) -> bytes:
    import ff
    corte = (["-ss", f"{ini:.2f}", "-t", f"{dur:.2f}"] if ini is not None else [])
    with tempfile.TemporaryDirectory() as d:
        alvo = Path(d) / "ouvido.mp3"
        # mono 16k: o modelo ouve fala, e o arquivo cabe folgado na requisição
        ff.run(["ffmpeg", "-y", *corte, "-i", str(fonte), "-vn", "-ac", "1", "-ar", "16000", "-b:a", "48k",
                str(alvo)], quiet=True)
        return alvo.read_bytes()


LITERAL = ("Transcreva LITERALMENTE este trecho em português. Ele começa e termina no meio da fala; "
           "ignore as bordas. Escreva gaguejada, palavra repetida e frase refeita exatamente como "
           "soam ('olha esses cri- olha esses criativos'); palavra cortada no meio vira o pedaço "
           "seguido de '-'; emenda brusca vira [corte]. Responda só a transcrição.")


def repete_frase(texto: str, n: int = 4, janela: int = 40) -> str | None:
    """Frase de n+ palavras que volta logo em seguida: o retake inteiro que o
    whisper junta numa tentativa só. Em 24/09/2026 a microlead saiu com "nesse
    vídeo eu vou te mostrar e te provar com a minha própria empresa" duas vezes,
    e a checagem de palavra colada não viu."""
    import re
    t = re.findall(r"[\wÀ-ÿ]+", texto.lower())
    for i in range(len(t) - n):
        seq = t[i:i + n]
        for j in range(i + n, min(len(t) - n + 1, i + janela)):
            if t[j:j + n] == seq:
                return " ".join(seq)
    return None


def tropeco(texto: str) -> bool:
    """A transcrição literal mostra o defeito? Palavra cortada, [corte] ou
    repetição colada — as duas primeiras e últimas palavras não contam (borda)."""
    import re
    miolo = " ".join(texto.split()[2:-2]).lower()
    return bool(re.search(r"\w-(\s|$)|\[corte\]|\b(\w{2,})\b[\s,.]+\2\b", miolo)) or bool(repete_frase(miolo))


def _literal(audio: bytes, modelo: str, chave: str, semente: int) -> str:
    corpo = json.dumps({"model": modelo, "seed": semente, "messages": [{"role": "user", "content": [
        {"type": "text", "text": LITERAL},
        {"type": "input_audio", "input_audio": {"data": base64.b64encode(audio).decode(), "format": "mp3"}}]}]}).encode()
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", corpo,
                                 {"Authorization": f"Bearer {chave}", "Content-Type": "application/json"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=120))["choices"][0]["message"]["content"]
    except Exception:
        return ""


def verifica(fonte: Path, p: dict, modelo: str, chave: str) -> bool:
    """Segunda opinião cega: o revisor que procura problema inventa perto de
    emenda. Transcreve 14s em volta do ponto (o tempo do modelo erra ±2s), três
    vezes, sem dizer o que foi acusado; confirma se alguma mostrar o tropeço.
    Em 22/09/2026 dois alarmes de 2/3 passadas no r1r2 consertado saíram limpos
    nas três. Limite: interjeição ("ih", "vixe") não tem marca pra achar."""
    trecho = _mp3(fonte, max(0.0, p["s"] - 7), 14)
    with ThreadPoolExecutor(3) as ex:
        textos = list(ex.map(lambda s: _literal(trecho, modelo, chave, s), (1, 2, 3)))
    return any(tropeco(t) for t in textos)


def _escuta(audio: bytes, pedido: str, modelo: str, chave: str, semente: int) -> list[dict] | None:
    corpo = json.dumps({
        "model": modelo, "seed": semente,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": pedido},
            {"type": "input_audio", "input_audio": {"data": base64.b64encode(audio).decode(), "format": "mp3"}}]}],
        "response_format": {"type": "json_schema", "json_schema": {"name": "ouvido", "strict": True, "schema": SCHEMA}},
    }).encode()
    for tentativa in range(3):
        try:
            req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", corpo,
                                         {"Authorization": f"Bearer {chave}", "Content-Type": "application/json"})
            txt = json.load(urllib.request.urlopen(req, timeout=300))["choices"][0]["message"]["content"]
            return json.loads(txt[txt.find("{"): txt.rfind("}") + 1])["problemas"]
        except Exception as e:
            if tentativa == 2:
                print(f"  passada {semente} falhou: {e}", file=sys.stderr)
                return None
            time.sleep(2 ** tentativa)


def _chave() -> str | None:
    """A chave da OpenRouter: do ambiente, do .env.local da raiz (onde moram as outras chaves do
    pacote) ou do .env do Hermes, que é onde ela mora nesta máquina. Em 29/09 o ouvido pulou calado
    a VSL de upsell inteira porque a chave não estava exportada, e as gaguejadas chegaram até o
    ouvido dele."""
    if os.environ.get("OPENROUTER_API_KEY"):
        return os.environ["OPENROUTER_API_KEY"]
    for env in (Path(__file__).resolve().parents[3] / ".env.local", Path.home() / ".hermes" / ".env"):
        if env.exists():
            for linha in env.read_text(encoding="utf-8").splitlines():
                if linha.startswith("OPENROUTER_API_KEY=") and linha.split("=", 1)[1].strip().strip('"'):
                    return linha.split("=", 1)[1].strip().strip('"')
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("modo", choices=["planeja", "confere"])
    ap.add_argument("fonte", type=Path, help="áudio ou vídeo")
    ap.add_argument("--passadas", type=int, default=3)
    ap.add_argument("--modelo", default=MODELO)
    ap.add_argument("--json", type=Path, help="grava os pontos aceitos aqui")
    a = ap.parse_args()

    chave = _chave()
    if not chave:
        print("ouvido: sem OPENROUTER_API_KEY (no ambiente ou no .env.local), pulei — ouça você mesmo antes de seguir", file=sys.stderr)
        return 0
    audio = _mp3(a.fonte)
    with ThreadPoolExecutor(a.passadas) as ex:
        passadas = [p for p in ex.map(lambda s: _escuta(audio, PEDIDO[a.modo], a.modelo, chave, s),
                                      range(1, a.passadas + 1)) if p is not None]
    if len(passadas) < 2:
        print("ouvido: menos de duas passadas voltaram, sem consenso possível", file=sys.stderr)
        return 2
    aceitos = consenso(passadas)
    if a.json:
        a.json.write_text(json.dumps(aceitos, ensure_ascii=False, indent=1), encoding="utf-8")

    if a.modo == "planeja":
        import clean_edl
        voz = clean_edl.fala_do_audio(a.fonte)
        for p in aceitos:
            # o tempo do modelo é de ouvido (±1s): o drop começa no silêncio antes
            # dele e acaba no silêncio seguinte. apara_pausas recusa se cair em voz.
            ini = max([b for _, b in voz if b <= p["s"] + 0.3] or [0.0])
            fim = min([x for x, _ in voz if x > ini + 0.15] or [p["s"] + 1.0])
            print(f"  {p['s']:7.1f}s  “{p['trecho']}”  → --drop {ini:.2f} {fim:.2f}  (confira)")
        print(f"ouvido planeja: {len(aceitos)} trecho(s) pra cortar, em {len(passadas)} passadas")
        return 0

    aceitos = [p for p in aceitos if verifica(a.fonte, p, a.modelo, chave)]
    # áudio curto: uma leitura literal inteira, sem depender do revisor apontar o
    # ponto (o retake de frase inteira passou nas 3 passadas do revisor em 24/09)
    import ff
    if ff.dur(a.fonte) <= 180:
        with ThreadPoolExecutor(3) as ex:
            inteiros = list(ex.map(lambda sm: _literal(audio, a.modelo, chave, sm), (1, 2, 3)))
        frases = [f for f in (repete_frase(t) for t in inteiros) if f]
        if len(frases) >= 2:
            aceitos.append({"t": "?", "s": 0.0, "tipo": "gagueira", "trecho": f"frase repetida: “{frases[0]}…”",
                            "gravidade": 3, "passadas": len(frases)})
    if a.json:
        a.json.write_text(json.dumps(aceitos, ensure_ascii=False, indent=1), encoding="utf-8")
    graves = [p for p in aceitos if p["gravidade"] >= 2]
    for p in aceitos:
        print(f"  {int(p['s'] // 60):02d}:{p['s'] % 60:04.1f}  [{p['tipo']} g{p['gravidade']}]  "
              f"“{p['trecho']}”  ({p['passadas']}/{len(passadas)} passadas)")
    print(f"ouvido confere: {len(aceitos)} ponto(s), {len(graves)} de gravidade 2+ — "
          + ("REPROVADO" if graves else "ok"))
    return 1 if graves else 0


def _autoteste() -> None:
    p = lambda t, g=2: {"t": t, "tipo": "gagueira", "trecho": "x", "gravidade": g}
    # três passadas acham o mesmo ponto com tempos um pouco diferentes: um grupo
    c = consenso([[p("00:14")], [p("00:13.5", 3)], [p("00:14.4")]])
    assert len(c) == 1 and c[0]["gravidade"] == 3 and c[0]["passadas"] == 3, c
    # ponto de uma passada só não passa
    assert consenso([[p("01:00")], [], [p("03:00")]]) == [], "aceitou ponto sem consenso"
    # dois pontos distantes não se fundem
    c = consenso([[p("00:10"), p("00:40")], [p("00:10.5"), p("00:41")]])
    assert [x["s"] for x in c] == [10.0, 40.0] or len(c) == 2, c
    assert segundos("06:13.5") == 373.5 and segundos("12.0") == 12.0
    # a transcrição literal confirma tropeço de verdade e não confunde "e-mail"
    assert tropeco("e esse aqui cuida do suporte por e-mail. Diz- a pessoa diz que comprou")
    assert tropeco("confere se entrou no ar. Olha esses cri- olha esses criativos aqui que")
    assert tropeco("aprovação e nada sobe o orçamento orçamento e campanha nova também dependem")
    assert not tropeco("cuida do meu suporte por e-mail. A pessoa diz que comprou e não recebeu")
    assert not tropeco("[corte]ste meu negócio. E esse aqui cuida do meu suporte por e-mail. A pessoa")
    assert repete_frase("pelo celular nesse vídeo eu vou te mostrar e te provar com a minha empresa nesse vídeo eu vou te mostrar e te provar")
    assert not repete_frase("sem freelancer sem agência sem passar o dia no computador e sem escrever nenhuma linha de código")
    print("ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--autoteste"]:
        _autoteste()
    else:
        sys.exit(main())
