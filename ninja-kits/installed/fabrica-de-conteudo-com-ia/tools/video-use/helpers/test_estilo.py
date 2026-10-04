"""Auto-teste do estilo. Sem framework — assert direto, um comando.

    tools/video-use/.venv/bin/python tools/video-use/helpers/test_estilo.py

Nada aqui abre vídeo nem renderiza: o estilo é dado, e resolver dado é a coisa
mais barata de cobrar que este projeto tem.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import estilo as es


# ---- resolver por nome ------------------------------------------------------


def test_os_quatro_estilos_existem():
    """Extraídos do que já era feito, não inventados."""
    for nome in ("aula-ccnp", "reel-mono", "reel-camera", "quadro"):
        assert nome in es.ESTILOS, f"faltou o estilo {nome}"


def test_resolve_os_oito_eixos():
    e = es.estilo("aula-ccnp")
    for eixo in es.EIXOS:
        assert eixo in e.eixos, f"o estilo resolveu sem o eixo {eixo}"


def test_nome_que_nao_existe_lista_os_validos():
    erro = None
    try:
        es.estilo("aula-que-nao-existe")
    except Exception as ex:
        erro = ex
    assert erro is not None, "estilo inexistente passou calado"
    assert "aula-ccnp" in str(erro), f"o erro não lista os válidos: {erro}"


def test_estilo_declara_de_que_bruto_parte():
    assert es.estilo("aula-ccnp").bruto == "live"
    assert es.estilo("reel-camera").bruto == "camera"


def test_orientacao_e_campo_do_estilo():
    """O eixo do projeto: formato é valor, não nome de módulo."""
    assert es.estilo("aula-ccnp").orientacao == "16:9"
    assert es.estilo("reel-mono").orientacao == "9:16"


def test_quadro_serve_os_dois_formatos():
    """O que derrubou as duas fábricas: um estilo que atende as duas orientações."""
    assert es.estilo("quadro").orientacao == "16:9"
    vertical = es.estilo("quadro", imagem={"orientacao": "9:16"})
    assert vertical.orientacao == "9:16" and vertical.vertical
    # e o resto do estilo — corte, trilha, desenho — segue sendo o mesmo
    assert vertical.eixos["corte"] == es.estilo("quadro").eixos["corte"]


# ---- herança ----------------------------------------------------------------


def test_herda_o_que_nao_sobrescreveu():
    filho = es.estilo("reel-mono-claro")
    pai = es.estilo("reel-mono")
    assert filho.eixos["corte"] == pai.eixos["corte"], "não herdou o corte do pai"
    assert filho.eixos["desenho"]["tema"] != pai.eixos["desenho"]["tema"], \
        "herdou até o que devia sobrescrever"


def test_herdar_de_pai_que_nao_existe_estoura_na_leitura():
    erro = None
    try:
        es.resolver({"herda": "fantasma"}, nome="orfao")
    except Exception as ex:
        erro = ex
    assert erro is not None, "estilo órfão passou calado"
    assert "fantasma" in str(erro)


def test_ciclo_de_heranca_nomeia_os_envolvidos():
    catalogo = {"a": {"herda": "b"}, "b": {"herda": "a"}}
    erro = None
    try:
        es.resolver(catalogo["a"], nome="a", catalogo=catalogo)
    except Exception as ex:
        erro = ex
    assert erro is not None, "o ciclo não estourou"
    assert "a" in str(erro) and "b" in str(erro), f"o erro não nomeia o ciclo: {erro}"


# ---- sobrescritas -----------------------------------------------------------


def test_sobrescrita_ganha_do_estilo():
    e = es.estilo("aula-ccnp", imagem={"altura": 1080})
    assert e.eixos["imagem"]["altura"] == 1080


def test_sobrescrita_num_eixo_nao_vaza_para_os_outros():
    base = es.estilo("aula-ccnp")
    e = es.estilo("aula-ccnp", imagem={"altura": 1080})
    for eixo in es.EIXOS:
        if eixo != "imagem":
            assert e.eixos[eixo] == base.eixos[eixo], f"a sobrescrita vazou para {eixo}"


def test_sobrescrita_parcial_mantem_o_resto_do_eixo():
    base = es.estilo("aula-ccnp")
    e = es.estilo("aula-ccnp", imagem={"altura": 1080})
    assert e.eixos["imagem"]["fps"] == base.eixos["imagem"]["fps"], \
        "mexer na altura zerou o resto do eixo de imagem"


def test_sobrescrita_nao_mexe_no_estilo_nomeado():
    es.estilo("aula-ccnp", imagem={"altura": 1080})
    assert es.estilo("aula-ccnp").eixos["imagem"]["altura"] != 1080, \
        "a sobrescrita contaminou o estilo guardado"


def test_eixo_que_nao_existe_estoura():
    erro = None
    try:
        es.estilo("aula-ccnp", velocidade={"x": 2})
    except Exception as ex:
        erro = ex
    assert erro is not None, "eixo inexistente passou calado"
    assert "velocidade" in str(erro)


def test_botao_que_nao_existe_dentro_do_eixo_estoura():
    erro = None
    try:
        es.estilo("aula-ccnp", imagem={"profundidade": 10})
    except Exception as ex:
        erro = ex
    assert erro is not None, "botão inexistente passou calado"
    assert "profundidade" in str(erro), f"o erro não nomeia o botão: {erro}"


# ---- recursos ---------------------------------------------------------------


def test_recursos_tem_posicao_declarada():
    """Ligar um recurso o põe no lugar dele, não no fim da fila."""
    e = es.estilo("aula-ccnp")
    pos = [es.RECURSOS[r]["posicao"] for r in e.recursos]
    assert pos == sorted(pos), f"os recursos saíram fora de ordem: {e.recursos}"


def test_desligar_recurso():
    e = es.estilo("aula-ccnp", recursos={"-": ["abertura"]})
    assert "abertura" not in e.recursos
    assert "explicador" in e.recursos, "desligar um recurso derrubou os outros"


def test_ligar_recurso_entra_na_posicao():
    e = es.estilo("reel-mono", recursos={"+": ["abertura"]})
    pos = [es.RECURSOS[r]["posicao"] for r in e.recursos]
    assert pos == sorted(pos), "o recurso ligado foi para o fim em vez da posição dele"


def test_recurso_que_nao_existe_estoura():
    erro = None
    try:
        es.estilo("aula-ccnp", recursos={"+": ["fumaca"]})
    except Exception as ex:
        erro = ex
    assert erro is not None, "recurso inexistente passou calado"
    assert "fumaca" in str(erro)


def test_desligar_recurso_que_ja_estava_desligado_nao_estoura():
    e = es.estilo("reel-mono", recursos={"-": ["abertura"]})
    assert "abertura" not in e.recursos


# ---- o corte vem do estilo --------------------------------------------------


def test_o_estilo_entrega_a_afinacao_de_corte():
    """O elo com a costura A: o estilo diz qual afinação, e ela sai pronta."""
    import clean_edl
    assert es.estilo("aula-ccnp").afinacao() == clean_edl.AULA
    assert es.estilo("reel-mono").afinacao() == clean_edl.TIGHT


def test_ajuste_de_corte_no_estilo_chega_na_afinacao():
    e = es.estilo("aula-ccnp", corte={"ajuste": {"pause_keep": 0.4}})
    assert e.afinacao().pause_keep == 0.4
    assert es.estilo("aula-ccnp").afinacao().pause_keep != 0.4, \
        "o ajuste contaminou o estilo guardado"


# ---- catálogo ---------------------------------------------------------------


def test_catalogo_lista_todos_com_formato_e_bruto():
    linhas = es.catalogo()
    assert len(linhas) == len(es.ESTILOS)
    for l in linhas:
        assert l["orientacao"] and l["bruto"], f"linha incompleta: {l}"


def test_catalogo_e_ordenado():
    nomes = [l["nome"] for l in es.catalogo()]
    assert nomes == sorted(nomes), "o catálogo saiu fora de ordem"


def test_todo_estilo_do_catalogo_resolve():
    """Nenhum estilo guardado pode estar quebrado — o catálogo é a prova."""
    for nome in es.ESTILOS:
        e = es.estilo(nome)
        assert e.nome == nome
        assert e.recursos == sorted(e.recursos, key=lambda r: es.RECURSOS[r]["posicao"])


def test_reel_avatar_herda_da_vsl_e_liga_o_broll():
    """Formato novo é estilo herdando: o reel de avatar é a VSL com b-roll, voz
    sintética e a pasta dos reels — o resto vem do pai."""
    e, vsl = es.estilo("reel-avatar"), es.estilo("vsl")
    assert e.bruto == "avatar" and e.vertical
    assert e.recursos == ["legenda", "broll", "trilha"], e.recursos
    assert e.eixos["voz"]["tratamento"] == "cru"
    assert e.eixos["corte"] == vsl.eixos["corte"] and e.adaptadores == vsl.adaptadores


def test_reel_editorial_guarda_as_regras_do_dono():
    """O molde do Nick virou estilo herdando do reel de avatar, com o que o dono decidiu
    em 30/09 como padrão: o que se repetia em três monta.py mora aqui uma vez."""
    e = es.estilo("reel-editorial")
    assert e.bruto == "avatar" and e.vertical and e.eixos["imagem"]["composicao"] == "editorial"
    assert e.eixos["imagem"]["fundo"] is None, (
        "o fundo é a placa do look de quem grava: vem do plano, e o confere cobra quando falta")
    assert e.eixos["imagem"]["costura"] == [768, 120], "tela dividida 40/60 com degradê"
    assert e.eixos["desenho"]["legenda_ig"] == 1450
    s = e.eixos["voz"]["sintese"]
    assert (s["modelo"], s["stability"], s["similarity_boost"]) == ("eleven_v4", 0.25, 0.85), s
    assert s["sotaque"].startswith("[in a Brazilian Portuguese accent") and s["sotaque"].count("[") == 1, (
        "só a marca de sotaque; marca de emoção não entra")
    t = e.eixos["trilha"]
    assert (t["cama"], t["duck"], t["fade_fim"]) == (-21.0, 3.0, 0.6), t
    assert es.estilo("reel-avatar").eixos["trilha"]["duck"] is None, "o botão novo vazou pro pai"


def test_criativo_herda_da_vsl_e_parte_do_banco():
    """O criativo dos ninjas virou estilo: da VSL vem a legenda viral no ritmo dela e a cama;
    o bruto é o banco de cenas, e o que é dele mora aqui, não num monta_criativo.py."""
    e, vsl = es.estilo("criativo"), es.estilo("vsl")
    assert e.bruto == "banco" and e.vertical and e.eixos["imagem"]["composicao"] == "cenas"
    assert e.recursos == ["legenda", "trilha"] and e.adaptadores == vsl.adaptadores, (e.recursos, e.adaptadores)
    assert e.eixos["desenho"]["ritmo"] == [0.167, 0.033]
    assert (e.eixos["desenho"]["destaque"], e.eixos["desenho"]["legenda_layout"]) == ("mk", "faixa_criativo")
    s = e.eixos["voz"]["sintese"]
    assert (e.eixos["voz"]["tratamento"], s["modelo"], s["tentativas"]) == ("cru", "eleven_multilingual_v2", 3), s
    t = e.eixos["trilha"]
    assert (t["cama"], t["duck"], t["fade_fim"]) == (-20.0, 1.5, 0.3), t
    assert e.eixos["entrega"]["pasta"] == "videos/criativos"
    assert vsl.eixos["desenho"]["destaque"] == "ac", "o amarelo do criativo vazou pra VSL"
    r = es.estilo("criativo-reel")
    assert (r.eixos["desenho"]["legenda_layout"], r.eixos["trilha"]["fade_fim"]) == ("faixa", 1.2)
    assert r.eixos["trilha"]["cama"] == -20.0 and r.bruto == "banco", "o resto vem do criativo"


def test_marca_do_aluno_entra_no_catalogo():
    """A pasta marca/ do aluno acrescenta estilo sem editar código: herda de um do kit, ganha o
    tema e a letra dela, e o erro dela sai com o arquivo no começo, antes de qualquer render."""
    import json, tempfile
    with tempfile.TemporaryDirectory() as d:
        pasta = Path(d)
        assert es.da_marca(pasta) == {}, "sem estilos.json a marca não acrescenta nada"
        arq = pasta / "estilos.json"
        arq.write_text(json.dumps({"_leia": "nota", "acme-reel": {
            "_nota": "nota também", "herda": "reel-editorial",
            "desenho": {"tema": "marca", "fonte": "marca/fontes/Acme.ttf#Black"},
            "imagem": {"fundo": "marca/placa.png"}}}), encoding="utf-8")
        novos = es.da_marca(pasta)
        assert list(novos) == ["acme-reel"], novos
        e = es.resolver(novos["acme-reel"], "acme-reel", {**es.ESTILOS, **novos})
        assert e.eixos["desenho"]["tema"] == "marca" and e.eixos["imagem"]["fundo"] == "marca/placa.png"
        assert e.eixos["voz"]["sintese"]["modelo"] == "eleven_v4", "o resto vem do reel-editorial"
        velho = dict(es.ESTILOS)
        try:
            es.ESTILOS.update(novos)        # o que a importação faz com a marca da raiz
            assert list(es.da_marca(pasta)) == ["acme-reel"], "ler a mesma marca de novo acusou ela mesma"
        finally:
            es.ESTILOS.clear()
            es.ESTILOS.update(velho)
        for ruim, diz in (({"reel-editorial": {"herda": "vsl"}}, "já existe no kit"),
                          ({"acme": {"herda": "nao-existe"}}, "nao-existe"),
                          ({"acme": {"herda": "vsl", "desenho": {"cor": "x"}}}, "cor")):
            arq.write_text(json.dumps(ruim), encoding="utf-8")
            try:
                es.da_marca(pasta)
            except ValueError as err:
                assert str(err).startswith(str(arq)) and diz in str(err), err
            else:
                raise AssertionError(f"{ruim} passou")
        arq.write_text("{", encoding="utf-8")
        try:
            es.da_marca(pasta)
        except ValueError as err:
            assert "JSON quebrado" in str(err), err
        else:
            raise AssertionError("JSON quebrado passou")


# ---- corrida ----------------------------------------------------------------


def main() -> int:
    casos = [
        ("os quatro estilos existem",        test_os_quatro_estilos_existem),
        ("resolve os oito eixos",            test_resolve_os_oito_eixos),
        ("nome errado lista os válidos",     test_nome_que_nao_existe_lista_os_validos),
        ("estilo declara o bruto",           test_estilo_declara_de_que_bruto_parte),
        ("orientação é campo do estilo",     test_orientacao_e_campo_do_estilo),
        ("quadro serve os dois formatos",    test_quadro_serve_os_dois_formatos),
        ("herda o que não sobrescreveu",     test_herda_o_que_nao_sobrescreveu),
        ("pai que não existe estoura",       test_herdar_de_pai_que_nao_existe_estoura_na_leitura),
        ("ciclo nomeia os envolvidos",       test_ciclo_de_heranca_nomeia_os_envolvidos),
        ("sobrescrita ganha do estilo",      test_sobrescrita_ganha_do_estilo),
        ("sobrescrita não vaza",             test_sobrescrita_num_eixo_nao_vaza_para_os_outros),
        ("sobrescrita parcial",              test_sobrescrita_parcial_mantem_o_resto_do_eixo),
        ("sobrescrita não contamina",        test_sobrescrita_nao_mexe_no_estilo_nomeado),
        ("eixo que não existe estoura",      test_eixo_que_nao_existe_estoura),
        ("botão que não existe estoura",     test_botao_que_nao_existe_dentro_do_eixo_estoura),
        ("recursos têm posição",             test_recursos_tem_posicao_declarada),
        ("desligar recurso",                 test_desligar_recurso),
        ("ligar recurso entra na posição",   test_ligar_recurso_entra_na_posicao),
        ("recurso que não existe estoura",   test_recurso_que_nao_existe_estoura),
        ("desligar o que já estava off",     test_desligar_recurso_que_ja_estava_desligado_nao_estoura),
        ("estilo entrega a afinação",        test_o_estilo_entrega_a_afinacao_de_corte),
        ("ajuste de corte chega",            test_ajuste_de_corte_no_estilo_chega_na_afinacao),
        ("catálogo lista tudo",              test_catalogo_lista_todos_com_formato_e_bruto),
        ("catálogo é ordenado",              test_catalogo_e_ordenado),
        ("todo estilo resolve",              test_todo_estilo_do_catalogo_resolve),
        ("reel-avatar herda da vsl",         test_reel_avatar_herda_da_vsl_e_liga_o_broll),
        ("reel-editorial: regras do dono",   test_reel_editorial_guarda_as_regras_do_dono),
        ("criativo herda da vsl",            test_criativo_herda_da_vsl_e_parte_do_banco),
        ("a marca do aluno entra",           test_marca_do_aluno_entra_no_catalogo),
    ]
    falhas = []
    for nome, caso in casos:
        try:
            caso()
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
