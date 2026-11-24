import random
import sys
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction

import sympy as sp


# ======================================================================
# PARTE 1 - LÓGICA DO CAMPO MINADO
# Coordenadas internas começam em 0 (linha 0, coluna 0).
# ======================================================================
class Estado(Enum):
    JOGANDO = "jogando"
    VITORIA = "vitoria"
    DERROTA = "derrota"


class Celula:
    """Uma casa do tabuleiro."""

    __slots__ = ("mina", "aberta", "marcada", "vizinhas")

    def __init__(self):
        self.mina = False      # tem mina?
        self.aberta = False    # já foi aberta?
        self.marcada = False   # tem bandeira?
        self.vizinhas = 0      # minas nas 8 casas ao redor


class CampoMinado:
    def __init__(self, linhas=9, colunas=9, minas=10, semente=None):
        if linhas < 2 or colunas < 2:
            raise ValueError("O tabuleiro precisa ter pelo menos 2x2.")
        if not 1 <= minas <= linhas * colunas - 1:
            raise ValueError("Quantidade de minas inválida para esse tabuleiro.")

        self.linhas = linhas
        self.colunas = colunas
        self.total_minas = minas
        self._rng = random.Random(semente)

        # Criar o tabuleiro
        self.tabuleiro = [[Celula() for _ in range(colunas)] for _ in range(linhas)]

        self.minas_posicionadas = False
        self.estado = Estado.JOGANDO
        self.celulas_abertas = 0
        self.bandeiras = 0

    # ---------- utilidades ----------
    @classmethod
    def com_minas_em(cls, linhas, colunas, posicoes_minas):
        """Cria um jogo com minas em posições escolhidas (útil para testes)."""
        jogo = cls(linhas, colunas, minas=max(1, len(posicoes_minas)))
        jogo.total_minas = len(posicoes_minas)
        for l, c in posicoes_minas:
            jogo.tabuleiro[l][c].mina = True
        jogo._calcular_vizinhas()
        jogo.minas_posicionadas = True
        return jogo

    def _dentro(self, l, c):
        return 0 <= l < self.linhas and 0 <= c < self.colunas

    def validar(self, l, c):
        if not self._dentro(l, c):
            raise IndexError(f"Coordenada fora do tabuleiro: ({l}, {c})")

    def vizinhos(self, l, c):
        """Coordenadas das (até 8) casas ao redor."""
        return [
            (l + dl, c + dc)
            for dl in (-1, 0, 1)
            for dc in (-1, 0, 1)
            if (dl or dc) and self._dentro(l + dl, c + dc)
        ]

    # ---------- minas e números ----------
    def _posicionar_minas(self, l_seguro, c_seguro):
        """
        Sorteia as minas só no primeiro clique: a casa clicada e seus
        vizinhos ficam livres, então o jogador nunca perde de cara.
        """
        proibidas = {(l_seguro, c_seguro)} | set(self.vizinhos(l_seguro, c_seguro))
        todas = [(l, c) for l in range(self.linhas) for c in range(self.colunas)]
        candidatas = [p for p in todas if p not in proibidas]
        if len(candidatas) < self.total_minas:       # tabuleiro apertado
            candidatas = [p for p in todas if p != (l_seguro, c_seguro)]

        for l, c in self._rng.sample(candidatas, self.total_minas):
            self.tabuleiro[l][c].mina = True
        self._calcular_vizinhas()
        self.minas_posicionadas = True

    def _calcular_vizinhas(self):
        for l in range(self.linhas):
            for c in range(self.colunas):
                cel = self.tabuleiro[l][c]
                cel.vizinhas = 0 if cel.mina else sum(
                    self.tabuleiro[a][b].mina for a, b in self.vizinhos(l, c)
                )

    # ---------- abrir ----------
    def abrir(self, l, c):
        """
        Abre a casa (l, c) e devolve a lista de casas abertas na jogada.
        Casa com bandeira ou já aberta: nada acontece. Mina: derrota.
        Casa com 0 minas ao redor: abre os vizinhos em cadeia.
        """
        self.validar(l, c)
        if self.estado != Estado.JOGANDO:
            return []

        celula = self.tabuleiro[l][c]
        if celula.aberta or celula.marcada:
            return []

        if not self.minas_posicionadas:
            self._posicionar_minas(l, c)

        if celula.mina:
            celula.aberta = True
            self.encerrar_derrota()
            return [(l, c)]

        abertas = []
        pilha = [(l, c)]                       # busca iterativa
        while pilha:
            cl, cc = pilha.pop()
            atual = self.tabuleiro[cl][cc]
            if atual.aberta or atual.marcada or atual.mina:
                continue
            atual.aberta = True
            self.celulas_abertas += 1
            abertas.append((cl, cc))
            if atual.vizinhas == 0:
                pilha.extend(self.vizinhos(cl, cc))

        self._verificar_vitoria()
        return abertas

    # ---------- bandeiras ----------
    def marcar(self, l, c):
        """Coloca/tira bandeira numa casa fechada. True se algo mudou."""
        self.validar(l, c)
        if self.estado != Estado.JOGANDO:
            return False
        celula = self.tabuleiro[l][c]
        if celula.aberta:
            return False
        celula.marcada = not celula.marcada
        self.bandeiras += 1 if celula.marcada else -1
        return True

    @property
    def minas_restantes(self):
        return self.total_minas - self.bandeiras

    # ---------- vitória e derrota ----------
    def _verificar_vitoria(self):
        """Vence quem abre todas as casas que NÃO têm mina."""
        if self.celulas_abertas == self.linhas * self.colunas - self.total_minas:
            self.estado = Estado.VITORIA
            for linha in self.tabuleiro:
                for cel in linha:
                    if cel.mina and not cel.marcada:
                        cel.marcada = True
                        self.bandeiras += 1

    def encerrar_derrota(self):
        """Marca derrota e revela todas as minas."""
        self.estado = Estado.DERROTA
        for linha in self.tabuleiro:
            for cel in linha:
                if cel.mina:
                    cel.aberta = True

    @property
    def terminou(self):
        return self.estado != Estado.JOGANDO

    # ---------- desenho em texto ----------
    def simbolo(self, l, c):
        cel = self.tabuleiro[l][c]
        if self.estado == Estado.DERROTA and cel.marcada and not cel.mina:
            return "X"            # bandeira errada
        if cel.marcada and not cel.aberta:
            return "F"            # bandeira
        if not cel.aberta:
            return "#"            # fechada
        if cel.mina:
            return "*"            # mina
        return str(cel.vizinhas) if cel.vizinhas else "."

    def texto(self, simbolo=None):
        simbolo = simbolo or self.simbolo
        cab = "    " + " ".join(f"{c + 1:>2}" for c in range(self.colunas))
        linhas = [cab, "    " + "---" * self.colunas]
        for l in range(self.linhas):
            corpo = " ".join(f"{simbolo(l, c):>2}" for c in range(self.colunas))
            linhas.append(f"{l + 1:>2} |{corpo}")
        return "\n".join(linhas)


# ======================================================================
# PARTE 2 - GERADOR DE QUESTÕES DE CÁLCULO
# A resposta de cada questão é sorteada (2 a 12), independente do número da
# casa. O sympy calcula a resposta e o código confere a si mesmo.
# ======================================================================
x = sp.symbols("x")

TOPICOS = ("funcao", "limite", "derivada", "integral")
NOMES_TOPICO = {
    "funcao": "Funções",
    "limite": "Limites",
    "derivada": "Derivadas",
    "integral": "Integrais",
}


def _txt(expr):
    """Expressão em uma linha: 3*x**2 - x  ->  3x^2 - x"""
    return str(expr).replace("**", "^").replace("*", "")


@dataclass
class Questao:
    enunciado: str
    resposta: int
    passos: str
    topico: str

    def conferir(self, texto):
        """Compara o que o aluno digitou com a resposta (aceita 3, 3.0, 6/2, 3,0)."""
        try:
            return Fraction(texto.strip().replace(",", ".")) == self.resposta
        except (ValueError, ZeroDivisionError):
            return False


def _funcao(alvo):
    a = random.randint(1, 4)          # ponto onde calculamos
    k = random.randint(1, 5)          # coeficiente de x
    b = alvo - k * a                  # garante f(a) = alvo
    f = k * x + b
    resp = f.subs(x, a)
    enunciado = f"Seja f(x) = {_txt(f)}. Calcule f({a})."
    passos = f"f({a}) = {k}·({a}) + ({b}) = {resp}"
    return enunciado, resp, passos


def _limite(alvo):
    # alvo >= 2: com alvo = 1 o sympy simplifica (x - 1)/(x - 1) para 1
    if random.choice(["fatoracao", "seno"]) == "fatoracao":
        expr = (x**alvo - 1) / (x - 1)                # tende a alvo quando x -> 1
        resp = sp.limit(expr, x, 1)
        enunciado = f"Calcule o limite, quando x tende a 1, de {_txt(expr)}"
        passos = (
            "Substituindo x = 1 dá 0/0 (indeterminação).\n"
            f"Fatorando: x^{alvo} - 1 = (x - 1)·({_txt(sp.cancel((x**alvo - 1) / (x - 1)))})\n"
            f"Cancelando (x - 1) e fazendo x = 1, o resultado é {resp}."
        )
    else:
        expr = sp.sin(alvo * x) / x                   # tende a alvo quando x -> 0
        resp = sp.limit(expr, x, 0)
        enunciado = f"Calcule o limite, quando x tende a 0, de sen({alvo}x)/x"
        passos = (
            "Substituindo x = 0 dá 0/0.\n"
            f"Usando o limite fundamental sen(u)/u -> 1, com u = {alvo}x:\n"
            f"sen({alvo}x)/x = {alvo}·sen({alvo}x)/({alvo}x) -> {alvo}·1 = {resp}"
        )
    return enunciado, resp, passos


def _derivada(alvo):
    a = random.randint(1, 3)          # coeficiente de x²
    x0 = random.randint(1, 4)         # ponto da derivada
    b = alvo - 2 * a * x0             # garante f'(x0) = alvo
    c = random.randint(-5, 5)
    f = a * x**2 + b * x + c
    df = sp.diff(f, x)
    resp = df.subs(x, x0)
    enunciado = f"Seja f(x) = {_txt(f)}. Calcule f'({x0})."
    passos = f"f'(x) = {_txt(df)}\nf'({x0}) = {_txt(df.subs(x, x0))} = {resp}"
    return enunciado, resp, passos


def _integral(alvo):
    f = 2 * alvo * x if random.choice(["linear", "quadratica"]) == "linear" else 3 * alvo * x**2
    F = sp.integrate(f, x)
    resp = sp.integrate(f, (x, 0, 1))
    enunciado = f"Calcule a integral definida de 0 até 1 de {_txt(f)} dx"
    passos = f"Primitiva: F(x) = {_txt(F)}\nF(1) - F(0) = {F.subs(x, 1)} - {F.subs(x, 0)} = {resp}"
    return enunciado, resp, passos


_GERADORES = {"funcao": _funcao, "limite": _limite, "derivada": _derivada, "integral": _integral}


RESPOSTA_MIN, RESPOSTA_MAX = 2, 12   # faixa das respostas sorteada
def gerar_questao(topico="misto", alvo=None):
    """Gera uma questão de cálculo. topico: um de TOPICOS ou 'misto'.
    alvo: resposta desejada (inteira, 2 a 12); se None, é sorteada."""
    if alvo is None:
        alvo = random.randint(RESPOSTA_MIN, RESPOSTA_MAX)
    if not RESPOSTA_MIN <= alvo <= RESPOSTA_MAX:
        raise ValueError(f"alvo deve estar entre {RESPOSTA_MIN} e {RESPOSTA_MAX}")
    if topico == "misto":
        topico = random.choice(TOPICOS)
    enunciado, resp, passos = _GERADORES[topico](alvo)
    assert resp == alvo, f"Gerador '{topico}' errado: esperado {alvo}, obteve {resp}"
    return Questao(enunciado, int(resp), passos, topico)





















# ======================================================================
# PARTE 3 - REGRAS QUE UNEM O JOGO E O CÁLCULO
# ======================================================================
class JogoCalculo:
    """
    Envolve o CampoMinado e adiciona:
      - números escondidos atrás de questões ("?")
      - vidas (errar uma questão custa uma vida)
      - desempenho por tópico (acertos e erros)
    """

    def __init__(self, linhas, colunas, minas, topico="misto", vidas=3, semente=None):
        self.campo = CampoMinado(linhas, colunas, minas, semente)
        self.topico = topico
        self.vidas_iniciais = vidas
        self.vidas = vidas
        self.resolvidas = set()          # casas cujo número já foi desvendado
        self.questoes = {}               # (l, c) -> Questao já sorteada
        self.desempenho = {t: [0, 0] for t in TOPICOS}   # tópico -> [acertos, erros]
        self.motivo_derrota = None       # "mina" ou "vidas"

    # ---------- atalhos ----------
    @property
    def estado(self):
        return self.campo.estado

    @property
    def terminou(self):
        return self.campo.terminou

    @property
    def acertos(self):
        return sum(a for a, _ in self.desempenho.values())

    @property
    def erros(self):
        return sum(e for _, e in self.desempenho.values())

    # ---------- ações ----------
    def abrir(self, l, c):
        abertas = self.campo.abrir(l, c)
        if self.estado == Estado.DERROTA and self.motivo_derrota is None:
            self.motivo_derrota = "mina"
        return abertas

    def marcar(self, l, c):
        return self.campo.marcar(l, c)

    def pendente(self, l, c):
        """A casa está aberta, tem número e a questão ainda não foi resolvida?"""
        cel = self.campo.tabuleiro[l][c]
        return cel.aberta and not cel.mina and cel.vizinhas > 0 and (l, c) not in self.resolvidas

    def pendentes(self):
        return [
            (l, c)
            for l in range(self.campo.linhas)
            for c in range(self.campo.colunas)
            if self.pendente(l, c)
        ]

    def pergunta(self, l, c):
        """Devolve a Questao da casa, ou None se não houver questão pendente."""
        self.campo.validar(l, c)
        if self.terminou or not self.pendente(l, c):
            return None
        if (l, c) not in self.questoes:
            self.questoes[(l, c)] = gerar_questao(self.topico)
        return self.questoes[(l, c)]

    def responder(self, l, c, texto):
        """
        Confere a resposta. Retorna (acertou, questao).
        Acertou ou errou, o número da casa passa a ser mostrado; errar custa
        uma vida e, se acabarem as vidas, o jogo termina em derrota.
        """
        q = self.pergunta(l, c)
        if q is None:
            raise ValueError("Essa casa não tem questão pendente.")

        acertou = q.conferir(texto)
        self.desempenho[q.topico][0 if acertou else 1] += 1
        self.resolvidas.add((l, c))

        if not acertou:
            self.vidas -= 1
            if self.vidas <= 0:
                self.motivo_derrota = "vidas"
                self.campo.encerrar_derrota()
        return acertou, q

    # ---------- desenho ----------
    def simbolo(self, l, c):
        s = self.campo.simbolo(l, c)
        if self.terminou:
            return s                               # fim de jogo: mostra tudo
        if s.isdigit() and (l, c) not in self.resolvidas:
            return "?"                             # número escondido
        return s

    def texto(self):
        return self.campo.texto(self.simbolo)


# ======================================================================
# PARTE 4 - INTERFACE NO TERMINAL (coordenadas começam em 1 para o jogador)
# ======================================================================
DIFICULDADES = {
    "1": ("Fácil", 6, 6, 6),
    "2": ("Médio", 9, 9, 10),
    "3": ("Difícil", 12, 12, 25),
}
MENU_TOPICOS = {
    "1": "funcao",
    "2": "limite",
    "3": "derivada",
    "4": "integral",
    "5": "misto",
}

AJUDA = """
Comandos (L = linha, C = coluna):
  a L C   abrir a casa
  r L C   resolver a questão de uma casa aberta ('?')
  m L C   colocar/tirar bandeira
  p       listar casas com questão pendente
  ajuda   mostrar esta ajuda
  s       sair

Legenda:  #  fechada   F  bandeira   ?  número escondido   .  zero minas ao redor
"""


def escolher(titulo, opcoes, padrao):
    print(f"\n{titulo}")
    for chave, valor in opcoes.items():
        print(f"  {chave} - {valor}")
    escolha = input(f"Escolha [{padrao}]: ").strip() or padrao
    return escolha if escolha in opcoes else padrao


def mostrar_status(jogo):
    print(f"\nVidas: {jogo.vidas}/{jogo.vidas_iniciais}"
          f"   Minas restantes: {jogo.campo.minas_restantes}"
          f"   Questões pendentes: {len(jogo.pendentes())}")
    print(jogo.texto())


def fazer_questao(jogo, l, c):
    q = jogo.pergunta(l, c)
    if q is None:
        print("Essa casa não tem questão pendente. (Ela precisa estar aberta e com '?'.)")
        return
    print(f"\n[{NOMES_TOPICO[q.topico]}] {q.enunciado}")
    resposta = input("Sua resposta: ")
    acertou, q = jogo.responder(l, c, resposta)
    if acertou:
        print(f"Correto! (resposta {q.resposta}). O número da casa foi revelado.")
    else:
        print(f"Errou! A resposta era {q.resposta}. Resolução:\n{q.passos}")
        print(f"Você perdeu uma vida ({max(jogo.vidas, 0)} restante(s)).")


def mostrar_resultado(jogo):
    print("\n" + jogo.texto())
    if jogo.estado == Estado.VITORIA:
        print("\nPARABÉNS! Você abriu todas as casas seguras!")
    elif jogo.motivo_derrota == "mina":
        print("\nBOOM! Você abriu uma mina. Fim de jogo.")
    else:
        print("\nAs vidas acabaram. Fim de jogo.")

    print("\n--- Seu desempenho em Cálculo ---")
    for t in TOPICOS:
        acertos, erros = jogo.desempenho[t]
        if acertos + erros:
            print(f"  {NOMES_TOPICO[t]:<10} {acertos} certa(s), {erros} errada(s)")
    total = jogo.acertos + jogo.erros
    if total:
        print(f"  Total: {jogo.acertos}/{total} ({100 * jogo.acertos // total}% de acerto)")
    else:
        print("  Nenhuma questão respondida.")


def jogar(semente=None):
    print("=" * 40)
    print("      CAMPO MINADO DE CÁLCULO")
    print("=" * 40)

    chave_topico = escolher(
        "Tópico das questões:",
        {"1": "Funções", "2": "Limites", "3": "Derivadas", "4": "Integrais", "5": "Misto"},
        "5",
    )
    chave_dif = escolher(
        "Dificuldade (tabuleiro):",
        {k: f"{n} ({l}x{c}, {m} minas)" for k, (n, l, c, m) in DIFICULDADES.items()},
        "1",
    )
    _, linhas, colunas, minas = DIFICULDADES[chave_dif]
    jogo = JogoCalculo(linhas, colunas, minas, MENU_TOPICOS[chave_topico], semente=semente)
    print(AJUDA)

    while not jogo.terminou:
        mostrar_status(jogo)
        partes = input("\n> ").strip().lower().split()
        if not partes:
            continue
        cmd = partes[0]

        if cmd == "s":
            print("Jogo encerrado.")
            return jogo
        if cmd in ("ajuda", "h", "?"):
            print(AJUDA)
            continue
        if cmd == "p":
            pend = jogo.pendentes()
            print("Pendentes (linha, coluna):",
                  ", ".join(f"({l + 1},{c + 1})" for l, c in pend) if pend else "nenhuma")
            continue
        if cmd not in ("a", "m", "r") or len(partes) != 3:
            print("Comando inválido. Exemplo: a 3 4   (digite 'ajuda' para ver os comandos)")
            continue

        try:
            l, c = int(partes[1]) - 1, int(partes[2]) - 1
            jogo.campo.validar(l, c)
        except ValueError:
            print("Use números para linha e coluna.")
            continue
        except IndexError:
            print("Essa posição está fora do tabuleiro.")
            continue

        cel = jogo.campo.tabuleiro[l][c]
        if cmd == "a":
            if cel.aberta:
                print("Essa casa já está aberta." +
                      (" Use 'r' para resolver a questão." if jogo.pendente(l, c) else ""))
            elif cel.marcada:
                print("Tire a bandeira antes de abrir essa casa.")
            else:
                novas = jogo.abrir(l, c)
                if not jogo.terminou:
                    print(f"{len(novas)} casa(s) aberta(s). Use 'r' nas casas com '?' para ver os números.")
        elif cmd == "m":
            if not jogo.marcar(l, c):
                print("Não dá para marcar uma casa já aberta.")
        else:
            fazer_questao(jogo, l, c)

    mostrar_resultado(jogo)
    return jogo


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")   # evita erro de acento no Windows
    except Exception:
        pass
    try:
        while True:
            jogar()
            if input("\nJogar de novo? (s/n) ").strip().lower() != "s":
                break
    except (EOFError, KeyboardInterrupt):
        print()
    print("Até a próxima, bons estudos!")


if __name__ == "__main__":
    main()
