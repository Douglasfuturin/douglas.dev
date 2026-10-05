"""O contract da costura B: ninguém chama ffmpeg pelas costas.

    tools/video-use/.venv/bin/python tools/video-use/helpers/test_costura.py

Sem isto, a costura fecha hoje e vaza no mês que vem — a primeira pressa escreve
um `subprocess.run(["ffmpeg", ...])` novo e nada reclama. Este teste é o que faz o
trabalho dos dois lotes de migração ficar de pé.

Lê o código como texto, não importa nada: um helper que precise de ffmpeg presente
para ser importado continuaria passando calado.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
COSTURA = "ff.py"

# O que ainda não passou pelos lotes de migração, com o motivo e quem cobra.
# Lista que encolhe: cada item sai daqui quando o ticket que o nomeia fechar.
PERDOADOS = {
    # O vídeo de quadro tem render próprio; só o corte converge. Fora do escopo
    # de #8 por decisão registrada, não por esquecimento.
    "../../quadro": "vídeo de quadro — fora do escopo de #8",
}

# O que JÁ saiu daqui, para que a lista encolhendo fique visível:
#   videos/aula-*/work/  — 20 forks do modo 2, apagados em #4
#   kit-v2/              — cópia do kit, agora gerada do tronco em #3
#   videos/troco/        — virou plano em #14; as duas ferramentas de autor
#                          subiram para helpers/ em vez de morrer com a pasta

BINARIOS = {"ffmpeg", "ffprobe"}


def _chamadas_de_processo(arquivo: Path):
    """Todo ponto onde o arquivo dispara um processo, com a linha e o comando."""
    try:
        arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
    except SyntaxError as e:
        raise AssertionError(f"{arquivo.name} não compila: {e}")

    achados = []
    for no in ast.walk(arvore):
        if not isinstance(no, ast.Call):
            continue
        alvo = ast.unparse(no.func)
        if not alvo.startswith("subprocess."):
            continue
        if not no.args:
            continue
        # Só interessa quando o primeiro argumento é uma lista literal cujo
        # primeiro item é um binário nosso. `subprocess.run(cmd)` com a lista
        # montada antes escapa — e é por isso que o teste também olha o texto.
        primeiro = no.args[0]
        nome = None
        if isinstance(primeiro, ast.List) and primeiro.elts:
            head = primeiro.elts[0]
            if isinstance(head, ast.Constant) and isinstance(head.value, str):
                nome = Path(head.value).name
        if nome in BINARIOS:
            achados.append((no.lineno, nome))
    return achados


# A biblioteca de peças chega de fora, em pacote, e o compor dela nasceu
# chamando ffmpeg por subprocess. Olhar só helpers/ deixava isso passar.
V2 = AQUI.parents[1] / "v2"


def _helpers() -> list[Path]:
    daqui = (p for p in AQUI.glob("*.py")
             if p.name != COSTURA and not p.name.startswith("test_"))
    return sorted([*daqui, *V2.rglob("*.py")])


def test_nenhum_helper_dispara_ffmpeg_direto():
    culpados = []
    for arq in _helpers():
        for linha, binario in _chamadas_de_processo(arq):
            culpados.append(f"{arq.name}:{linha} chama {binario} por fora da costura")
    assert not culpados, "a costura B vazou:\n  " + "\n  ".join(culpados)


def test_nenhum_helper_define_run_dur_ou_probe_proprio():
    """Definir é o sintoma; o que dói é a segunda implementação que diverge."""
    culpados = []
    for arq in _helpers():
        arvore = ast.parse(arq.read_text(encoding="utf-8"))
        for no in arvore.body:                      # só o topo do arquivo
            if isinstance(no, ast.FunctionDef) and no.name in ("run", "dur", "probe"):
                corpo = ast.unparse(no)
                if "ff." not in corpo:
                    culpados.append(f"{arq.name}:{no.lineno} define {no.name}() próprio")
    assert not culpados, "implementação duplicada:\n  " + "\n  ".join(culpados)


def test_constantes_de_saida_moram_num_lugar_so():
    """Trocar o encoder tem que ser editar uma linha."""
    culpados = []
    for arq in _helpers():
        texto = arq.read_text(encoding="utf-8")
        for marca in ('"libx264"', "'libx264'", '"yuv420p"', "'yuv420p'"):
            if marca in texto:
                linha = next(i for i, l in enumerate(texto.splitlines(), 1) if marca in l)
                culpados.append(f"{arq.name}:{linha} escreve {marca} à mão")
    assert not culpados, "constante de saída solta:\n  " + "\n  ".join(culpados)


def test_alvos_de_loudness_nao_sao_escritos_a_mao():
    """A medida do vídeo de quadro e a da aula não podem discordar.

    O que é proibido é o NÚMERO solto no filtro. Montar o filtro é legítimo — as
    cadeias de filtro são a parte artística e ficam onde estão. O alvo é que não
    pode ser digitado duas vezes: são três (voz, trilha, transcrição) e cada um
    tem um nome na costura.
    """
    import re as _re
    culpados = []
    for arq in _helpers():
        for i, linha in enumerate(arq.read_text(encoding="utf-8").splitlines(), 1):
            if _re.search(r"loudnorm=I=-?\d", linha):       # número literal, não {ff.…}
                culpados.append(f"{arq.name}:{i} escreve o alvo de loudness à mão")
    assert not culpados, "alvo de loudness solto:\n  " + "\n  ".join(culpados)


def test_a_lista_de_perdoados_e_honesta():
    """Cada perdão nomeia o ticket que o remove. Perdão sem prazo vira permanente."""
    for caminho, motivo in PERDOADOS.items():
        assert "#" in motivo, f"o perdão de {caminho} não diz qual ticket o tira: {motivo}"


def main() -> int:
    casos = [
        ("nenhum helper dispara ffmpeg direto", test_nenhum_helper_dispara_ffmpeg_direto),
        ("nenhum helper define run/dur/probe",  test_nenhum_helper_define_run_dur_ou_probe_proprio),
        ("constantes de saída num lugar só",    test_constantes_de_saida_moram_num_lugar_so),
        ("alvos de loudness não são à mão",     test_alvos_de_loudness_nao_sao_escritos_a_mao),
        ("lista de perdoados é honesta",        test_a_lista_de_perdoados_e_honesta),
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
    print(f"({len(_helpers())} helpers conferidos; "
          f"{len(PERDOADOS)} áreas ainda perdoadas, cada uma com ticket)")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
