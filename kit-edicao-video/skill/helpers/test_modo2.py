"""Auto-teste do modo 2. Sem framework — assert direto, um comando.

    tools/video-use/.venv/bin/python tools/video-use/helpers/test_modo2.py

Cada caso aqui existe porque o defeito correspondente ficou numa das quatro
cópias e não nas outras três.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import modo2 as m2


def _plano(**extra) -> dict:
    p = {
        "pares": {
            "a": {"obs": "/brutos/obs.mp4", "celular": "/brutos/IMG_1.MOV", "offset": 1.25},
            "b": {"obs": "/brutos/obs2.mp4", "celular": "/brutos/IMG_2.MOV", "offset": -0.4},
        },
        "tarja": "crop=2560:1505:0:47",
    }
    p.update(extra)
    return p


def _trechos(*pares):
    return [{"start": a, "end": b, "par": c} for a, b, c in pares]


# ---- a chapa ----------------------------------------------------------------


def test_chapa_sai_no_tamanho_do_quadro(tmp: Path):
    from PIL import Image
    png = m2.chapa(m2.Geometria(), tmp / "chapa.png")
    assert Image.open(png).size == (1920, 1080)


def test_a_camera_nao_encosta_na_tela():
    """Quatro de quatro alunos relataram a câmera cobrindo a spec. Sobreposição zero."""
    g = m2.Geometria()
    sx, sy, sw, sh = g.tela
    cx = g.camera[0]
    assert cx - g.borda >= sx + sw, \
        f"a câmera invade a tela: começa em {cx - g.borda}, a tela acaba em {sx + sw}"


def test_geometria_antiga_continua_nomeada():
    """Refazer a aula de 12/08 não pode ser adivinhar onde a tela ficava."""
    assert m2.GEOMETRIAS["antiga"].tela == (65, 123, 1552, 873)
    assert m2.GEOMETRIAS["antiga"] != m2.GEOMETRIAS["atual"]


# ---- cobertura --------------------------------------------------------------


def test_trecho_sem_camera_aborta_antes_do_render():
    """O buraco tem que aparecer antes do encode, não depois de vinte minutos."""
    plano = _plano(buracos=[[73.3, 92.3]])
    erro = None
    try:
        m2.confere_cobertura(plano, _trechos((70.0, 80.0, "a")))
    except Exception as e:
        erro = e
    assert erro is not None, "o trecho sem câmera passou"
    assert "73.3" in str(erro), f"o erro não diz qual buraco: {erro}"


def test_trecho_que_nao_toca_o_buraco_passa():
    plano = _plano(buracos=[[73.3, 92.3]])
    m2.confere_cobertura(plano, _trechos((10.0, 20.0, "a"), (95.0, 99.0, "a")))


def test_sem_buraco_declarado_nada_aborta():
    m2.confere_cobertura(_plano(), _trechos((0.0, 10.0, "a")))


# ---- os segmentos -----------------------------------------------------------


def _cmds(plano, trechos, tmp):
    cmds, _ = m2.segmentos(plano, trechos, m2.Geometria(),
                           tmp / "chapa.png", tmp / "trab")
    return cmds


def test_a_chapa_em_laco_sempre_leva_limite_de_duracao(tmp: Path):
    """A chapa é imagem parada. Sem -t o render espera um quadro que não acaba."""
    for cmd in _cmds(_plano(), _trechos((10.0, 14.0, "a")), tmp):
        assert "-loop" in cmd
        i = cmd.index("-loop")
        assert "-t" in cmd[i:i + 4], f"entrada em laço sem -t: {' '.join(cmd)}"


def test_as_duas_fontes_zeram_o_pts(tmp: Path):
    """O -ss de entrada faz o primeiro quadro nascer com PTS != 0, e a emenda
    pisca preto. As DUAS fontes precisam do setpts."""
    cmd = _cmds(_plano(), _trechos((10.0, 14.0, "a")), tmp)[0]
    fc = cmd[cmd.index("-filter_complex") + 1]
    assert fc.count("setpts=PTS-STARTPTS") == 2, \
        f"só uma das fontes zera o PTS: {fc}"


def test_o_offset_do_clap_entra_por_par(tmp: Path):
    """Cada par OBS+celular tem o seu offset. Trocar de par troca de offset."""
    a = _cmds(_plano(), _trechos((10.0, 14.0, "a")), tmp)[0]
    b = _cmds(_plano(), _trechos((10.0, 14.0, "b")), tmp)[0]
    assert "11.250" in " ".join(a), "o offset de 'a' não entrou"
    assert "9.600" in " ".join(b), "o offset de 'b' não entrou"


def test_varias_fontes_com_um_offset_cada(tmp: Path):
    """A aula gravada em três partes e a gravada em uma usam o mesmo código."""
    cmds = _cmds(_plano(), _trechos((10.0, 14.0, "a"), (50.0, 54.0, "b")), tmp)
    assert len(cmds) == 2
    a, b = " ".join(cmds[0]), " ".join(cmds[1])
    assert "IMG_1.MOV" in a and "obs.mp4" in a
    assert "IMG_2.MOV" in b and "obs2.mp4" in b, "o segundo par não trouxe o próprio OBS"


def test_um_par_so_dispensa_dizer_qual(tmp: Path):
    """A aula de uma sentada não precisa repetir o nome do par em cada trecho."""
    plano = _plano(); plano["pares"] = {"unico": plano["pares"]["a"]}
    cmds = _cmds(plano, [{"start": 1.0, "end": 2.0}], tmp)
    assert len(cmds) == 1


def test_par_que_nao_existe_lista_os_validos(tmp: Path):
    erro = None
    try:
        _cmds(_plano(), _trechos((1.0, 2.0, "z")), tmp)
    except Exception as e:
        erro = e
    assert erro is not None and "a, b" in str(erro).replace("'", "")


def test_a_tarja_e_declarada_por_aula(tmp: Path):
    """Numa aula a tarja foi 47px, na de 12/08 foram 80px. Medida, não herdada."""
    cmd = _cmds(_plano(tarja="crop=2560:1472:0:80"), _trechos((1.0, 2.0, "a")), tmp)[0]
    assert "crop=2560:1472:0:80" in cmd[cmd.index("-filter_complex") + 1]


def test_as_caixas_de_borrao_sao_dado(tmp: Path):
    """A lista de dados sensíveis de uma aula tem que ser legível sem ler código."""
    cmd = _cmds(_plano(borroes=[[100, 200, 300, 40]]), _trechos((1.0, 2.0, "a")), tmp)[0]
    assert "boxblur" in cmd[cmd.index("-filter_complex") + 1]


def test_sem_borrao_nao_sobra_filtro_solto(tmp: Path):
    cmd = _cmds(_plano(), _trechos((1.0, 2.0, "a")), tmp)[0]
    assert "boxblur" not in cmd[cmd.index("-filter_complex") + 1]


def test_trecho_sem_par_declarado_estoura(tmp: Path):
    plano = _plano(); plano["pares"] = {}
    erro = None
    try:
        m2.segmentos(plano, [{"start": 1.0, "end": 2.0}], m2.Geometria(),
                     tmp / "c.png", tmp / "t")
    except Exception as e:
        erro = e
    assert erro is not None, "trecho sem câmera declarada passou"


def main() -> int:
    casos = [
        ("chapa no tamanho do quadro",   test_chapa_sai_no_tamanho_do_quadro),
        ("câmera não encosta na tela",   lambda _: test_a_camera_nao_encosta_na_tela()),
        ("geometria antiga nomeada",     lambda _: test_geometria_antiga_continua_nomeada()),
        ("trecho sem câmera aborta",     lambda _: test_trecho_sem_camera_aborta_antes_do_render()),
        ("trecho longe do buraco passa", lambda _: test_trecho_que_nao_toca_o_buraco_passa()),
        ("sem buraco nada aborta",       lambda _: test_sem_buraco_declarado_nada_aborta()),
        ("chapa em laço leva -t",        test_a_chapa_em_laco_sempre_leva_limite_de_duracao),
        ("as duas fontes zeram o PTS",   test_as_duas_fontes_zeram_o_pts),
        ("offset por par",               test_o_offset_do_clap_entra_por_par),
        ("várias fontes, um offset cada", test_varias_fontes_com_um_offset_cada),
        ("tarja declarada por aula",     test_a_tarja_e_declarada_por_aula),
        ("borrões são dado",             test_as_caixas_de_borrao_sao_dado),
        ("sem borrão, sem filtro solto", test_sem_borrao_nao_sobra_filtro_solto),
        ("trecho sem par estoura",       test_trecho_sem_par_declarado_estoura),
        ("um par só dispensa dizer qual", test_um_par_so_dispensa_dizer_qual),
        ("par que não existe lista",     test_par_que_nao_existe_lista_os_validos),
    ]
    falhas = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for nome, caso in casos:
            try:
                caso(tmp)
                print(f"  ok   {nome}")
            except Exception as e:
                falhas.append((nome, e))
                print(f"  FALHA {nome}: {e}")
    print(f"\n{len(casos) - len(falhas)}/{len(casos)} passaram")
    if falhas:
        print("falhou: " + ", ".join(n for n, _ in falhas))
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
