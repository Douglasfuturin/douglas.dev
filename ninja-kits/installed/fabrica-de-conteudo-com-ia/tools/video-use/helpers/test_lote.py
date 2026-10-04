"""Auto-teste do lote de cenas. Nada sai da máquina: a rede é trocada por um dublê.

    tools/video-use/.venv/bin/python tools/video-use/helpers/test_lote.py

Gerar cena cobra na Higgsfield. O que se cobra aqui é que nada seja pedido sem `--gera`, que o
modo seco da fábrica pare no passo que cobra com a estimativa, e que a cena baixada chegue ao
banco com ficha, pronta para o criativo.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import fabrica as fb
import lote

PELE = "No readable text anywhere."


def _lote(d: Path, **extra) -> Path:
    """Um banco vazio com um lote de duas cenas, e a estética na pasta de cima."""
    (d / "estetica.json").write_text(json.dumps({"neutra": {"prompt": PELE}}), encoding="utf-8")
    (d / "banco").mkdir(exist_ok=True)
    arq = d / "banco" / "lote.json"
    arq.write_text(json.dumps({"estetica": "neutra", "cenas": {
        "porta": {"modelo": "kling", "prompt": "A door opens by itself.", "acabamento": "cctv", "cam": "03"},
        "mesa": {"modelo": "kling", "prompt": "A desk tidies itself."}}, **extra}), encoding="utf-8")
    return arq


@contextlib.contextmanager
def _rede(pedidos: list):
    """O dublê da API: grava (url, corpo) e devolve o que a Higgsfield devolveria."""
    antes = urllib.request.urlopen, urllib.request.urlretrieve

    def urlopen(r, timeout=None):
        corpo = json.loads(r.data) if r.data and r.get_method() != "PUT" else None
        pedidos.append((r.full_url, corpo))
        if "/estimate/" in r.full_url:
            resp = {"usd": "0.30"}
        elif r.full_url.endswith("generate-upload-url"):
            resp = {"upload_url": "https://up", "upload_headers": {}, "public_url": "https://foto.jpg"}
        elif r.full_url.startswith("https://status/"):
            resp = {"status": "completed", "video": {"url": "https://video.mp4"}}
        else:
            resp = {"status_url": f"https://status/{len(pedidos)}"}
        return io.BytesIO(json.dumps(resp).encode())

    urllib.request.urlopen = urlopen
    urllib.request.urlretrieve = lambda url, destino: Path(destino).write_bytes(b"mp4")
    try:
        yield
    finally:
        urllib.request.urlopen, urllib.request.urlretrieve = antes


def test_estima_pela_tabela_sem_chave_e_sem_rede(tmp: Path):
    lo = lote.ler(_lote(tmp))
    assert lote.confere(lo) == [], lote.confere(lo)
    assert lote.pele(lo) == " " + PELE
    assert lote.faltam(lo) == ["porta", "mesa"]
    assert abs(lote.estimativa(lo) - 2 * 4 * lote.USD_S["kling"]) < 1e-9, lote.estimativa(lo)
    # a duração e a proporção do lote vão no pedido e na conta
    (tmp / "curto").mkdir()
    curto = lote.ler(_lote(tmp / "curto", duracao=3, proporcao="16:9"))
    assert lote.params(curto, "kling")[1] == {"duration": 3, "aspect_ratio": "16:9", "sound": "off"}
    assert abs(lote.estimativa(curto) - 2 * 3 * lote.USD_S["kling"]) < 1e-9
    pedidos = []
    with _rede(pedidos), contextlib.redirect_stdout(io.StringIO()) as tela:
        lote.main([str(tmp / "banco" / "lote.json")], env=tmp / "sem-chave")
    assert not pedidos, f"estimar pela tabela não chama a API: {pedidos}"
    assert "2 cenas a gerar, US$ 0.67" in tela.getvalue() and "pela tabela" in tela.getvalue(), tela.getvalue()


def test_recusa_antes_de_gastar(tmp: Path):
    arq = _lote(tmp)
    d = json.loads(arq.read_text(encoding="utf-8"))
    d["cenas"]["rosto"] = {"modelo": "wan", "prompt": "The SAME person as in the reference images."}
    d["cenas"]["errada"] = {"modelo": "sora", "prompt": "x"}
    arq.write_text(json.dumps({**d, "estetica": "outra"}), encoding="utf-8")
    erros = " | ".join(lote.confere(lote.ler(arq)))
    for dito in ("'outra' não está", "modelo 'sora'", "pede `rosto`"):
        assert dito in erros, erros
    arq.write_text(json.dumps({**d, "rosto": ["eu.jpg"]}), encoding="utf-8")
    assert "a foto do rosto não existe" in " | ".join(lote.confere(lote.ler(arq)))


def test_gera_so_com_gera_e_a_cena_chega_ao_banco(tmp: Path):
    arq = _lote(tmp)
    (tmp / "eu.jpg").write_bytes(b"jpg")
    d = json.loads(arq.read_text(encoding="utf-8"))
    d["cenas"]["comigo"] = {"modelo": "wan", "prompt": "The SAME person walks in.", "acabamento": "celular"}
    arq.write_text(json.dumps({**d, "rosto": ["../eu.jpg"]}), encoding="utf-8")
    env = tmp / "env"
    env.write_text("HIGGSFIELD_KEY_ID=id\nHIGGSFIELD_KEY_SECRET=segredo\n", encoding="utf-8")
    pedidos = []
    with _rede(pedidos), contextlib.redirect_stdout(io.StringIO()):
        lote.main([str(arq)], env=env)
    assert all("/estimate/" in u for u, _ in pedidos), f"sem --gera, só estimativa: {pedidos}"
    pedidos.clear()
    with _rede(pedidos), contextlib.redirect_stdout(io.StringIO()):
        lote.main([str(arq), "--gera"], env=env)
    gerou = [(u, c) for u, c in pedidos if c and "prompt" in c and "/estimate/" not in u]
    assert len(gerou) == 3, pedidos
    assert all(c["prompt"].endswith(" " + PELE) for _, c in gerou), "a estética entra no fim de toda cena"
    wan = next(c for u, c in gerou if u.endswith("reference-to-video"))
    assert wan["image_urls"] == ["https://foto.jpg"] and wan["duration"] == 5, wan
    banco = tmp / "banco"
    assert sorted(p.stem for p in banco.glob("*.mp4")) == ["comigo", "mesa", "porta"]
    assert json.loads((banco / "pedidos.json").read_text(encoding="utf-8")) == {}
    # só a cena com acabamento ganha ficha; a sem acabamento é registrada à mão
    fichas = {f["id"]: f for f in json.loads((banco / "cenas.json").read_text(encoding="utf-8"))}
    assert sorted(fichas) == ["comigo", "porta"], fichas
    assert fichas["porta"]["arquivo"] == "porta.mp4" and fichas["porta"]["cam"] == "03", fichas["porta"]
    # a ficha acertada à mão fica, e de novo não gera nada
    fichas["porta"]["janela"] = [1.0, 3.5]
    (banco / "cenas.json").write_text(json.dumps(list(fichas.values())), encoding="utf-8")
    pedidos.clear()
    with _rede(pedidos), contextlib.redirect_stdout(io.StringIO()):
        lote.main([str(arq), "--gera"], env=env)
    assert all("/estimate/" in u for u, _ in pedidos), pedidos
    assert json.loads((banco / "cenas.json").read_text(encoding="utf-8"))[0]["janela"] == [1.0, 3.5]


def test_fala_espera_a_imagem_e_vai_com_a_voz(tmp: Path):
    """A cena `fala` (o avatar na Higgsfield): dura o trecho de voz, sobe a imagem e a voz, espera a
    imagem que ainda não existe, e o --so gera só a cena pedida."""
    arq = tmp / "lote.json"
    fala = lambda img: {"modelo": "fala", "prompt": "He talks.", "imagem": img, "audio": "v.wav", "voz": [3.6, 5.6]}
    arq.write_text(json.dumps({"cenas": {"t3": fala("s0.png"), "t4": fala("s0.png"), "t9": fala("falta.png")}}),
                   encoding="utf-8")
    for f in ("s0.png", "v.wav"):
        (tmp / f).write_bytes(b"x")
    lo = lote.ler(arq)
    assert lote.confere(lo) == [], lote.confere(lo)
    assert lote.corpo(lo, "t3") == ("wan/v2.7/image-to-video", {"duration": 2, "resolution": "720p"})
    assert abs(lote.estimativa(lo) - 3 * 2 * lote.USD_S["fala"]) < 1e-9, "paga o trecho, não os 5 s do modelo"
    sem = {**lo, "cenas": {"x": {"modelo": "fala", "prompt": "x"}}}
    assert "pede a `imagem`" in " | ".join(lote.confere(sem))
    env = tmp / "env"
    env.write_text("HIGGSFIELD_KEY_ID=id\nHIGGSFIELD_KEY_SECRET=segredo\n", encoding="utf-8")
    pedidos = []
    with _rede(pedidos), contextlib.redirect_stdout(io.StringIO()) as tela:
        lote.main([str(arq), "--gera", "--so", "t3", "t9"], env=env)
    gerou = [c for u, c in pedidos if c and "prompt" in c and "/estimate/" not in u]
    assert len(gerou) == 1 and gerou[0]["image_url"] == gerou[0]["audio_url"] == "https://foto.jpg", gerou
    assert gerou[0]["duration"] == 2 and "aspect_ratio" not in gerou[0], gerou[0]
    assert "t9 espera" in tela.getvalue(), tela.getvalue()
    assert sorted(p.stem for p in tmp.glob("*.mp4")) == ["t3"], "o --so não gera a t4"
    # a ação é o mesmo modelo sem a voz: só a imagem sobe
    d = json.loads(arq.read_text(encoding="utf-8"))
    d["cenas"]["gesto"] = {"modelo": "acao", "prompt": "He snaps.", "imagem": "s0.png", "duracao": 3}
    arq.write_text(json.dumps(d), encoding="utf-8")
    pedidos.clear()
    with _rede(pedidos), contextlib.redirect_stdout(io.StringIO()):
        lote.main([str(arq), "--gera", "--so", "gesto"], env=env)
    gesto = [c for u, c in pedidos if c and "prompt" in c and "/estimate/" not in u]
    assert len(gesto) == 1 and "audio_url" not in gesto[0] and gesto[0]["duration"] == 3, gesto


def test_fabrica_para_no_passo_que_cobra(tmp: Path):
    """Banco vazio e um lote de duas cenas: o seco mostra `$ cenas` com a estimativa e a voz que
    falta, e nem a execução chama a API."""
    if not (Path(fb.__file__).parent / "criativo.py").exists():
        return
    _lote(tmp)
    plano = {"estilo": "criativo", "slug": "porta", "projeto": "provas", "fonte": "voz.mp3",
             "_dir": str(tmp), "saida": str(tmp / "saida"), "trabalho": "_trabalho", "banco": "banco",
             "lote": "banco/lote.json", "locutor": {"id": "voz-de-teste"},
             "trechos": [["Oi.", "porta"], ["Tchau.", "mesa"]]}
    pedidos = []
    with _rede(pedidos):
        seco = fb.fabrica(plano, seco=True)
        assert [(p.nome, p.cobra) for p in seco.passos] == [
            ("cenas", "Higgsfield, 2 cenas, ~US$ 0.67"), ("narração", "ElevenLabs")], seco.passos
        assert seco.passos[0].cmd[-1] == "--gera" and seco.passos[0].cmd[-3].endswith("lote.py")
        tela = io.StringIO()
        with contextlib.redirect_stdout(tela):
            seco.imprime()
            fb.fabrica(plano)
        assert " $ cenas" in tela.getvalue(), tela.getvalue()
    assert not pedidos, f"a fábrica chamou a API sozinha: {pedidos}"
    assert not list((tmp / "banco").glob("*.mp4"))
    # com as cenas no banco, a cadeia segue para a voz
    for c in ("porta", "mesa"):
        (tmp / "banco" / f"{c}.mp4").write_bytes(b"mp4")
    (tmp / "banco" / "cenas.json").write_text(json.dumps([
        {"id": "porta", "arquivo": "porta.mp4", "acabamento": "cctv"},
        {"id": "mesa", "arquivo": "mesa.mp4", "acabamento": "celular"}]), encoding="utf-8")
    assert [p.nome for p in fb.fabrica(plano, seco=True).passos] == ["narração"]


def main() -> int:
    casos = [
        ("estima pela tabela sem chave",         test_estima_pela_tabela_sem_chave_e_sem_rede),
        ("recusa antes de gastar",               test_recusa_antes_de_gastar),
        ("gera só com --gera, a cena tem ficha", test_gera_so_com_gera_e_a_cena_chega_ao_banco),
        ("a fala espera a imagem, vai com a voz", test_fala_espera_a_imagem_e_vai_com_a_voz),
        ("a fábrica para no passo que cobra",    test_fabrica_para_no_passo_que_cobra),
    ]
    falhas = []
    with tempfile.TemporaryDirectory() as td:
        for nome, caso in casos:
            sub = Path(td) / nome.replace(" ", "_").replace("/", "_")
            sub.mkdir(parents=True)
            try:
                caso(sub)
                print(f"  ok   {nome}")
            except Exception as e:
                falhas.append((nome, e))
                print(f"  FALHA {nome}: {e!r}")
    print(f"\n{len(casos) - len(falhas)}/{len(casos)} passaram")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
