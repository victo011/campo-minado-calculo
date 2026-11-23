"""Confere de forma independente se enunciado e resposta de cada questão batem.
Lê o TEXTO do enunciado, interpreta com sympy e recalcula a resposta."""
import re, sys, random, importlib
import sympy as sp
from sympy.parsing.sympy_parser import (parse_expr, standard_transformations,
    implicit_multiplication_application, convert_xor)

mod = importlib.import_module(sys.argv[1])
TR = standard_transformations + (implicit_multiplication_application, convert_xor)
x = sp.symbols("x")

def P(s):
    s = s.replace("sen(", "sin(")
    return parse_expr(s, transformations=TR, local_dict={"x": x})

def gerar(topico):
    try:
        return mod.gerar_questao(topico)              # versão nova
    except TypeError:
        return mod.gerar_questao(random.randint(1, 8), topico)  # versão antiga

def recalcular(q):
    e = q.enunciado
    if q.topico == "funcao":
        m = re.match(r"Seja f\(x\) = (.+)\. Calcule f\((-?\d+)\)\.$", e)
        return P(m[1]).subs(x, int(m[2]))
    if q.topico == "derivada":
        m = re.match(r"Seja f\(x\) = (.+)\. Calcule f'\((-?\d+)\)\.$", e)
        return sp.diff(P(m[1]), x).subs(x, int(m[2]))
    if q.topico == "limite":
        m = re.match(r"Calcule o limite, quando x tende a (-?\d+), de (.+)$", e)
        return sp.limit(P(m[2]), x, int(m[1]))
    if q.topico == "integral":
        m = re.match(r"Calcule a integral definida de 0 até 1 de (.+) dx$", e)
        return sp.integrate(P(m[1]), (x, 0, 1))

erros, total, respostas = [], 0, {}
for t in mod.TOPICOS:
    for _ in range(300):
        q = gerar(t); total += 1
        respostas[q.resposta] = respostas.get(q.resposta, 0) + 1
        try:
            ok = sp.simplify(recalcular(q) - q.resposta) == 0
        except Exception as ex:
            ok, q.passos = False, f"(falha ao interpretar: {ex!r})"
        if not ok:
            erros.append((q.topico, q.enunciado, q.resposta))
print(f"{total} questões testadas, {len(erros)} com problema")
for e in sorted(set(erros))[:8]: print("  ", e)
print("respostas geradas:", dict(sorted(respostas.items())))
