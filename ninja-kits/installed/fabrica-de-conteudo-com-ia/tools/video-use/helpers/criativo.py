#!/usr/bin/env python3
"""O criativo: voz em off sobre cenas do banco, cada cena cobrindo o trecho da fala que ilustra.

    V=tools/video-use/.venv/bin/python
    $V tools/video-use/helpers/fabrica.py <pasta>/plano.json --seco   # confere, não renderiza
    $V tools/video-use/helpers/fabrica.py <pasta>/plano.json          # monta e entrega
    $V tools/video-use/helpers/criativo.py voz <trabalho>             # a narração (cobra na ElevenLabs)

Quem chama os passos é a fábrica, pelos estilos `criativo` (anúncio) e `criativo-reel`: ela
confere o plano, põe nele o que é do estilo e grava <trabalho>/criativo.json, que é o que cada
passo daqui lê. A trilha é a cama da fábrica, depois da legenda. A linguagem (primeiro quadro,
laço, choque cômico) está em docs/linguagem-do-criativo.md; cena nova sai do helpers/lote.py,
que estima antes de gastar.

É a fala que corta, não um tamanho fixo: a transcrição dá a hora de cada trecho, e cada cena dura
exatamente o trecho que cobre (com 2,6 s fixos os takes saíam antes da hora).

O plano (tempos em segundos da voz):
  estilo      "criativo" | "criativo-reel"
  slug        o nome do final
  fonte       a voz (vo.mp3): o relógio do criativo. Enquanto ela não existe, a cadeia para no
              passo que cobra
  transcript  a transcrição da voz; padrão transcripts/<nome da voz>.json, na pasta do plano
  banco       a pasta do banco de cenas: cenas.json, as cenas que ele cita e acabadas/, o cache
              do acabamento
  locutor     {id, nome, ajustes}: a voz da ElevenLabs e os voice_settings dela. O modelo e o teto
              de gerações vêm do estilo (voz.sintese)
  trechos     [[fala, cena], …] ou [fala, cena, troca]: a troca é o acabamento ("documentario") ou
              {acabamento, hora, cam} — o documentário reaproveita cena de câmera de segurança sem
              o "CAM 02", e o telejornal ao vivo não pode pular de 03:37 pra 12:18. A ficha e a
              troca levam também `data` (AAAA-MM-DD), a que a filmadora escreve; sem ela, hoje
  cor         a cor da estética, por cima de todo acabamento ("neutra" | "technicolor")
  punch       as palavras em destaque (a do "comenta")
  funde       [["E COM", "O QUE AS PESSOAS"]]: dois cards vizinhos que o agrupador partiu
  trilha      {faixa, cama, duck, fade_fim}: o eixo do estilo, ajustado para este vídeo
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
import urllib.request
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path

import ff
from filmagem_achada import CORES, TIPOS, acabar

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
PY = sys.executable
CAUDA = 0.6   # respiro depois da última palavra


def norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    return re.sub(r"[^a-z0-9 ]", " ", "".join(c for c in t if unicodedata.category(c) != "Mn")).split()


def voz(texto, voice_id, ajustes, saida, antes="", depois="", modelo="eleven_multilingual_v2"):
    """Uma leitura na ElevenLabs (cobra). A chave mora em <raiz>/.env.local."""
    env = dict(l.strip().split("=", 1) for l in open(RAIZ / ".env.local", encoding="utf-8")
               if "=" in l and not l.startswith("#"))
    # antes/depois: o texto em volta de um trecho emendado, pra leitura sair no tom da frase e não solta
    corpo = json.dumps({"text": texto, "model_id": modelo, "voice_settings": ajustes,
                        **({"previous_text": antes} if antes else {}), **({"next_text": depois} if depois else {})}).encode()
    r = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128",
                               data=corpo, headers={"xi-api-key": env["ELEVENLABS_API_KEY"], "Content-Type": "application/json"})
    saida.write_bytes(urllib.request.urlopen(r).read())


def palavras_do_roteiro(trechos, palavras):
    """A voz lê o roteiro, então o texto é conhecido: a legenda sai dele, com a pontuação
    dele (é ela que fecha o card no fim da frase; o Whisper tira o ponto e sai
    "ARTIFICIAL O MATHEUS"), e do Whisper vem só a hora. Onde ele ouviu outra coisa
    ("carrocés", "11", "ar" + "condicionado"), vale o roteiro, no tempo que ele ocupou."""
    rot = " ".join(t for t, _ in trechos).split()
    chave = lambda w: "".join(norm(w))
    sm = SequenceMatcher(None, [chave(w) for w in rot], [chave(w["text"]) for w in palavras], autojunk=False)
    saida = []                                   # invariante: saida tem as palavras rot[:a1]
    for op, a1, a2, b1, b2 in sm.get_opcodes():
        if op == "equal":
            saida += [{"text": rot[a1 + k], "start": palavras[b1 + k]["start"], "end": palavras[b1 + k]["end"],
                       "type": "word"} for k in range(a2 - a1)]
            continue
        if a1 == a2:                             # ouviu o que não está no roteiro: some
            continue
        if b1 < b2:
            t0, t1 = palavras[b1]["start"], palavras[b2 - 1]["end"]
        elif saida:                              # engoliu a palavra: divide o tempo com a anterior
            ant = saida.pop(); a1 -= 1; t0, t1 = ant["start"], ant["end"]
        else:                                    # engoliu logo a primeira: vai no silêncio do começo
            t0, t1 = 0.0, palavras[0]["start"] if palavras else 0.0
        novas = rot[a1:a2]
        pesos = [len(chave(w)) or 1 for w in novas]
        vao = max(t1 - t0, 0.12 * len(novas))
        for w, p in zip(novas, pesos):
            d = vao * p / sum(pesos)
            saida.append({"text": w, "start": round(t0, 3), "end": round(t0 + d, 3), "type": "word"})
            t0 += d
    return saida


def pausa(audio, t0, t1):
    """O maior silêncio (início, fim) entre o fim de uma palavra (t0) e o começo da seguinte (t1),
    medido no áudio; a emenda corta no meio dele. O Whisper fecha a palavra antes de o som acabar:
    em 28/09 o corte pela média dos tempos dele comeu 100 ms de "eles!" e deixou um clique."""
    # a janela sobra dos dois lados pra pegar a pausa inteira: o Whisper às vezes cola as duas palavras
    # (fim 20,58, início 20,58) e a pausa real, 20,68–21,25, saía cortada no fim da janela
    a, b = max(0.0, t0 - 0.6), t1 + 0.9
    r = ff.run(["ffmpeg", "-hide_banner", "-nostats", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", str(audio),
                "-af", "silencedetect=noise=-40dB:d=0.05", "-f", "null", "-"], capture=True, quiet=True)
    ini = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    fim = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    vaos = [(s, e) for s, e in zip(ini, fim + [b - a] * (len(ini) - len(fim)))
            if a + s <= t1 + 0.3 and a + e >= t0 - 0.05]        # só a que encosta na fronteira do Whisper
    if not vaos:
        return (t0 + t1) / 2, (t0 + t1) / 2
    s, e = max(vaos, key=lambda v: v[1] - v[0])
    return a + s, a + e


def cena(cid, catalogo, banco, acabamento=None, hora=None, cam=None, cor="neutra", data=None, canto=None):
    """A cena do banco com o acabamento pedido, feita uma vez e guardada em <banco>/acabadas/. `canto`:
    onde começa o texto do aparelho (sem ele, o canto da tela; o anúncio passa o da zona segura)."""
    c = catalogo[cid]
    tipo = acabamento or c.get("acabamento")
    if not tipo:
        sys.exit(f"a cena {cid} não tem acabamento na ficha nem no trecho")
    src = Path(banco) / c["arquivo"]
    hora, cam = hora or c.get("hora", "03:12:47"), cam or c.get("cam", "02")   # câmera escondida pede uma câmera por lugar
    data = data or c.get("data") or date.today().isoformat()   # só a filmadora escreve, e só nela entra no nome
    # a impressão dos parâmetros do acabamento entra no nome: mudou o TIPOS, a cena é refeita (em 28/09 o
    # acabamento mudou de qualidade e o cache velho seria reaproveitado sem ninguém ver)
    # a cor da estética ("cor" no plano) entra no nome e na impressão; a neutra deixa o nome de antes.
    # A conversão de 24 a 30 também entra: em 04/10 ela passou de cópia a mistura, e o cache velho ficaria
    q = hashlib.md5((json.dumps(TIPOS[tipo], sort_keys=True) + CORES[cor] + ff.taxa(24)).encode()).hexdigest()[:6]
    pronta = Path(banco) / "acabadas" / (f"{src.stem}--{tipo}--{hora.replace(':', '')}{'' if cam == '02' else '--cam' + cam}"
                                         f"{'' if cor == 'neutra' else '--' + cor}"
                                         f"{'--' + data.replace('-', '') if tipo == 'filmadora' else ''}"
                                         f"{'--c%dx%d' % tuple(canto) if canto else ''}--{q}.mp4")
    if not pronta.exists():
        pronta.parent.mkdir(parents=True, exist_ok=True)
        acabar(src, pronta, tipo, hora, cam, cor, data, **({"canto": tuple(canto)} if canto else {}))
    return pronta, c.get("janela", [0.2, 2.8])


# ---- o plano ----------------------------------------------------------------


def _rel(doc: dict, c: str) -> Path:
    p = Path(c)
    return p if p.is_absolute() else Path(doc.get("_dir", ".")) / p


def fonte(doc: dict) -> Path:
    return _rel(doc, doc["fonte"])


def canto(doc: dict) -> tuple[int, int] | None:
    """Com `zona` no plano (o anúncio), o texto do aparelho começa no canto dela, e não no da tela.
    `canto` no plano manda: null deixa o texto no canto da tela (é cenário, e a zona tem outra peça ali)."""
    if "canto" in doc:
        return tuple(doc["canto"]) if doc["canto"] else None
    z = doc.get("zona")
    return (z[0], z[1]) if z else None


def transcript(doc: dict) -> Path:
    v = fonte(doc)
    return _rel(doc, doc["transcript"]) if doc.get("transcript") else _rel(doc, f"transcripts/{v.stem}.json")


def catalogo(doc: dict) -> dict:
    return {c["id"]: c for c in json.loads((_rel(doc, doc["banco"]) / "cenas.json").read_text(encoding="utf-8"))}


def _trechos(doc: dict) -> list[tuple[str, str, dict]]:
    """(fala, cena, troca) de cada trecho; a troca vazia é a ficha da cena como está."""
    return [(t[0], t[1], ({"acabamento": t[2]} if isinstance(t[2], str) else t[2]) if len(t) > 2 else {})
            for t in doc["trechos"]]


def brutas(doc: dict) -> list[Path]:
    """O que o acabamento lê: a ficha do banco e cada cena citada."""
    banco, cat = _rel(doc, doc["banco"]), catalogo(doc)
    return [banco / "cenas.json", *dict.fromkeys(banco / cat[c]["arquivo"] for _, c, _ in _trechos(doc))]


def confere(doc: dict) -> list[str]:
    """Tudo o que dá para recusar antes do primeiro comando, com o motivo."""
    erros = []
    if not doc.get("banco"):
        return ["o plano não tem `banco`: a pasta com o cenas.json"]
    banco = _rel(doc, doc["banco"])
    if not (banco / "cenas.json").exists():
        return [f"o banco não tem cenas.json: {banco}"]
    cat = catalogo(doc)
    if (doc.get("cor") or "neutra") not in CORES:
        erros.append(f"cor '{doc['cor']}' não existe. Disponíveis: {', '.join(CORES)}")
    for fala, cid, troca in _trechos(doc):
        if cid not in cat:
            erros.append(f"cena fora do banco: {cid} (em \"{fala}\")")
            continue
        tipo = troca.get("acabamento") or cat[cid].get("acabamento")
        if tipo not in TIPOS:
            erros.append(f"a cena {cid} pede o acabamento '{tipo}'. Disponíveis: {', '.join(TIPOS)}")
        elif not (banco / cat[cid]["arquivo"]).exists():
            erros.append(f"a cena {cid} não está no disco: {banco / cat[cid]['arquivo']}")
        data = troca.get("data") or cat[cid].get("data")
        if data:
            try:
                date.fromisoformat(data)
            except (TypeError, ValueError):
                erros.append(f"a cena {cid} pede a data '{data}': escreva AAAA-MM-DD")
    v, t = fonte(doc), transcript(doc)
    if not v.exists() and not (doc.get("locutor") or {}).get("id"):
        erros.append("sem a voz e sem `locutor.id`: não há quem leia o texto")
    if not t.exists() and (t.name != f"{v.stem}.json" or t.parent.name != "transcripts"):
        erros.append(f"a transcrição que falta sai em transcripts/{v.stem}.json: aponte `transcript` pra lá "
                     f"ou tire o campo")
    return erros


def alinhadas(doc: dict) -> list[dict]:
    """As palavras do roteiro na hora em que a voz as disse."""
    palavras = [w for w in json.loads(transcript(doc).read_text(encoding="utf-8"))["words"]
                if w.get("type", "word") == "word"]
    return palavras_do_roteiro([(f, c) for f, c, _ in _trechos(doc)], palavras)


# ---- os passos ----------------------------------------------------------------


def narracao(doc: dict, trab: Path) -> None:
    """A voz (cobra na ElevenLabs): o texto dos trechos lido de uma vez, no locutor do plano,
    com o teto de gerações do estilo."""
    s, loc, saida = doc["_estilo"]["sintese"], doc["locutor"], fonte(doc)
    if saida.exists():
        sys.exit(f"{saida.name} já existe: apague antes, se for refazer (refazer cobra de novo)")
    log = saida.with_name(f"{saida.stem}.tentativas.json")
    feitas = json.loads(log.read_text(encoding="utf-8")) if log.exists() else []
    if len(feitas) >= s["tentativas"]:
        sys.exit(f"já foram {len(feitas)} gerações em {log.name}: o teto do estilo é {s['tentativas']}")
    texto = " ".join(f for f, _, _ in _trechos(doc))
    saida.parent.mkdir(parents=True, exist_ok=True)
    voz(texto, loc["id"], loc.get("ajustes", {}), saida, modelo=s["modelo"])
    log.write_text(json.dumps(feitas + [{"texto": texto, "modelo": s["modelo"], "locutor": loc}],
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{saida}  {ff.dur(saida):.2f}s  voz {loc.get('nome', loc['id'])}")


def base(doc: dict, trab: Path) -> None:
    """Cada cena com o acabamento dela (do cache do banco quando já existe), emendadas na hora
    da fala, com a voz por baixo e a cauda no fim."""
    fps, vo, banco, cat = doc["_estilo"]["fps"], fonte(doc), _rel(doc, doc["banco"]), catalogo(doc)
    trechos, al = _trechos(doc), alinhadas(doc)
    feitas = [(cid, *cena(cid, cat, banco, **troca, cor=doc.get("cor") or "neutra", canto=canto(doc)))
              for _, cid, troca in trechos]
    fim = ff.dur(vo) + CAUDA
    ts, k = [], 0
    for fala, _, _ in trechos:
        ts.append(al[k]["start"] if ts else 0.0)
        k += len(fala.split())
    ts = [round(t * fps) / fps for t in ts + [fim]]   # corte em quadro inteiro: a soma não escorrega da voz
    # Cada cena cobre o seu trecho. O momento dela fecha a janela (o joinha vem depois dos 2 s):
    # trecho curto mostra o fim da janela; trecho maior que a cena desacelera, não congela.
    ins, fc = [], ""
    for i, (cid, arq, (j0, j1)) in enumerate(feitas):
        d = max(0.4, ts[i + 1] - ts[i]); L = ff.dur(arq)
        ini = max(0.0, min(j1 - d if d <= j1 - j0 else j0, L - d))
        lento = max(1.0, d / (L - ini))
        ins += ["-i", str(arq)]
        # a cena gerada vem a 24, e desacelerada fica mais lenta ainda: mistura em vez de repetir quadro
        taxa = ff.taxa(0 if lento > 1.01 else ff.probe(arq).fps, fps)
        fc += (f"[{i}:v]trim=start={ini:.3f}:end={ini + d / lento:.3f},setpts=(PTS-STARTPTS)*{lento:.4f},"
               f"setsar=1,{taxa}[v{i}];")
        print(f"{ts[i]:6.2f}s  {d:4.1f}s  {cid}  {ini:.1f}-{ini + d / lento:.1f}s da cena"
              + (f"  ({lento:.2f}x mais lenta)" if lento > 1.01 else ""))
    n = len(feitas)
    fc += "".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[v];[{n}:a]apad=whole_dur={fim:.3f}[a]"
    ff.run(["ffmpeg", "-y", *ins, "-i", str(vo), "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
            "-t", f"{fim:.3f}", *ff.args_video(fps=fps), *ff.args_audio(), str(trab / "base.mp4")], quiet=True)


def cards(doc: dict, trab: Path) -> None:
    """O plano da legenda viral: o texto do roteiro na hora da voz, com o acento e o ritmo do
    estilo e o layout de todo card (o rodapé do anúncio é do botão; o Reels usa a faixa)."""
    est, fala, crus = doc["_estilo"], trab / "fala.json", trab / "cards.json"
    fala.write_text(json.dumps({"words": alinhadas(doc)}, ensure_ascii=False), encoding="utf-8")
    punch = ["--punch", ",".join(doc["punch"])] if doc.get("punch") else []     # a palavra-chave do "comenta"
    subprocess.run([PY, str(AQUI / "cards_da_fala.py"), str(fala), *punch, "-o", str(crus)], check=True)
    cs = json.loads(crus.read_text(encoding="utf-8"))
    cs = cs.get("cards", cs) if isinstance(cs, dict) else cs
    # quatro átonas seguidas ("e com o que") saem num card só delas; `funde` junta com o vizinho
    txc = lambda c: " ".join(w["tx"] for w in c["words"]).upper()
    for a, b in doc.get("funde", []):
        i = next((i for i in range(len(cs) - 1) if txc(cs[i]) == a and txc(cs[i + 1]) == b), None)
        if i is None:
            sys.exit(f"funde: não há card \"{a}\" seguido de \"{b}\". Cards: {' | '.join(map(txc, cs))}")
        cs[i:i + 2] = [{**cs[i], "t1": cs[i + 1]["t1"], "words": cs[i]["words"] + cs[i + 1]["words"]}]
    if est.get("layout"):
        cs = [{**c, "layout": est["layout"]} for c in cs]
    if est.get("fonte"):        # a letra da marca (estilo.py, desenho.fonte)
        cs = [{**c, "fonte": est["fonte"]} for c in cs]
    plano = {**({"acento": est["acento"]} if est.get("acento") else {}),
             **({"ritmo": {"entrada": est["ritmo"][0], "stagger": est["ritmo"][1]}} if est.get("ritmo") else {}),
             "cards": cs, "brolls": [], "camera": [], "sons": []}
    # Só reescreve se mudou: o plano de criativo curto fica abaixo do piso de tamanho da impressão
    # e este passo roda de novo, mas a legenda, que lê o instante deste arquivo, não.
    saida, texto = trab / "legenda.json", json.dumps(plano, ensure_ascii=False)
    if not saida.exists() or saida.read_text(encoding="utf-8") != texto:
        saida.write_text(texto, encoding="utf-8")


PASSOS = {"voz": narracao, "base": base, "cards": cards}


def main() -> None:
    ap = argparse.ArgumentParser(description="O criativo, passo a passo (quem chama é a fábrica)")
    ap.add_argument("passo", choices=list(PASSOS))
    ap.add_argument("trabalho", type=Path, help="a pasta de trabalho, onde a fábrica deixou o criativo.json")
    a = ap.parse_args()
    PASSOS[a.passo](json.loads((a.trabalho / "criativo.json").read_text(encoding="utf-8")), a.trabalho)


if __name__ == "__main__":
    main()
