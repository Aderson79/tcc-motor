"""Testes obrigatórios (Seção 16 da especificação)."""
import numpy as np
import pytest

from tcc import metrics, sampling
from tcc.embed import chunk
from tcc.profiles import add_noise, title_filter
from tcc.systems import va, vc
from tcc.systems.b1 import B1
from tcc.systems.b2 import B2

GOLD5 = {"O": 2, "R1": 1, "R2": 1, "R3": 1, "R4": 1, "R5": 1}
GOLD2 = {"O": 2, "R1": 1, "R2": 1}


def test_metricas_exemplo_1():
    lst = ["R1", "X", "O", "Y", "R2"]
    assert metrics.dcg(metrics.rels(lst, GOLD5)) == pytest.approx(2.386853, abs=1e-6)
    assert metrics.dcg([2, 1, 1, 1, 1]) == pytest.approx(3.948459, abs=1e-6)
    assert metrics.ndcg(lst, GOLD5) == pytest.approx(0.604502, abs=1e-6)
    assert metrics.precision(lst, GOLD5) == pytest.approx(0.6)
    assert metrics.average_precision(lst, GOLD5) == pytest.approx(0.453333, abs=1e-6)
    assert metrics.mrr_origin(lst, GOLD5) == pytest.approx(0.333333, abs=1e-6)


def test_metricas_exemplo_2():
    lst = ["X", "R1", "Y", "Z", "O"]
    assert metrics.dcg([2, 1, 1, 0, 0]) == pytest.approx(3.130930, abs=1e-6)
    assert metrics.ndcg(lst, GOLD2) == pytest.approx(0.448632, abs=1e-6)
    assert metrics.precision(lst, GOLD2) == pytest.approx(0.4)
    assert metrics.average_precision(lst, GOLD2) == pytest.approx(0.3, abs=1e-6)
    assert metrics.mrr_origin(lst, GOLD2) == pytest.approx(0.2)


def test_lista_perfeita_e_lista_sem_relevantes():
    assert metrics.ndcg(["O", "R1", "R2", "R3", "R4"], GOLD5) == pytest.approx(1.0)
    assert metrics.ndcg(["O", "R1", "R2", "X", "Y"], GOLD2) == pytest.approx(1.0)
    assert all(v == 0 for v in metrics.all_metrics(["V", "W", "X", "Y", "Z"], GOLD5).values())


def _eligible(n=60):
    return {l: [f"{l}{i:03d}" for i in range(n)] for l in "RIASEC"}


def test_sorteio():
    eligible = _eligible()
    dev = sampling.draw_dev(eligible, 1, 5)
    ev, info = sampling.draw_eval(eligible, {c for _, c in dev}, 2, 33)
    for letter in "RIASEC":
        assert sum(l == letter for l, _ in dev) == 5
        assert sum(l == letter for l, _ in ev) == 33
    assert not {c for _, c in dev} & {c for _, c in ev}
    assert len({c for _, c in ev}) == 198 and not info["redistributed"]
    assert dev == sampling.draw_dev(eligible, 1, 5)
    assert ev == sampling.draw_eval(eligible, {c for _, c in dev}, 2, 33)[0]
    assert dev != sampling.draw_dev(eligible, 3, 5)


def test_sorteio_com_falta_de_elegiveis():
    eligible = _eligible()
    eligible["A"] = eligible["A"][:28]
    dev = sampling.draw_dev(eligible, 1, 5)
    used = {c for _, c in dev}
    ev, info = sampling.draw_eval(eligible, used, 2, 33)
    codes = [c for _, c in ev]
    assert len(codes) == len(set(codes)) == 198 and not set(codes) & used
    assert sum(l == "A" for l, _ in ev) == 23 and info["deficit"] == 10
    assert all(c[0] == l for l, c in ev)  # type recorded = real type of the occupation


def test_substituicao_mesmo_tipo_e_nao_usada():
    eligible = _eligible(10)
    used = {f"R{i:03d}" for i in range(9)}
    assert sampling.draw_replacement(eligible, "R", used, 7, "dev", 0) == "R009"
    assert sampling.draw_replacement(eligible, "R", used | {"R009"}, 7, "dev", 0) is None


def test_filtro_de_titulo():
    assert title_filter("Registered Nurses", "I like helping a nurse care for people.") == ["nurse"]
    assert title_filter("Registered Nurses", "I enjoy caring for people who are unwell.") == []
    # stopwords e palavras com menos de 3 letras não disparam o filtro
    assert title_filter("Directors of IT and the Arts", "It is the work of an IT person and of others.") == []
    assert title_filter("Art Directors", "I love art and making arts with friends.") == ["art"]


def test_molde_va_limites_de_intensidade():
    assert va.level(4.99) == "moderate" and va.level(5.0) == "high"
    assert va.level(2.99) == "low" and va.level(3.0) == "moderate"


def test_molde_va_ordem_e_empate():
    text = va.fill_template([4.0, 6.0, 4.0, 1.0, 6.0, 2.99], "I like things.")
    assert text == ("Interest profile, from strongest to weakest:\n"
                    "Investigative interests: high; Enterprising interests: high;\n"
                    "Realistic interests: moderate; Artistic interests: moderate;\n"
                    "Conventional interests: low; Social interests: low.\n\n"
                    "Self-description: I like things.")


def test_parser_da_reordenacao():
    assert vc.parse("7, 2, 15, 1, 9") == [7, 2, 15, 1, 9]
    assert vc.parse("7, 2, 15, 1") is None            # menos de 5
    assert vc.parse("7, 2, 15, 1, 7") is None         # repetidos
    assert vc.parse("7, 2, 15, 1, 21") is None        # fora de 1–20
    assert vc.parse("0, 2, 15, 1, 9") is None
    assert vc.parse("7, 2, 15, 1, 9, 3") is None      # mais de 5


def test_prompt_da_reordenacao_lista_os_20_candidatos():
    text = vc.rerank_prompt("PROFILE", [(f"T{i}", f"D{i}") for i in range(1, 21)])
    assert "Person's interests:\nPROFILE\n\nCandidates:\n1. T1: D1\n2. T2: D2\n" in text
    assert text.endswith("20. T20: D20") and "{" not in text


def test_b2_perfil_igual_ao_da_ocupacao():
    matrix = np.array([[1.0, 2, 3, 4, 5, 6], [6.0, 5, 4, 3, 2, 1], [3.0, 3, 3, 3, 3, 3], [2.0, 7, 1, 4, 4, 3]])
    b2 = B2(["a", "b", "c", "d"], matrix)
    r = b2.correlations(matrix[3])
    assert r[3] == pytest.approx(1.0)
    assert b2.rank(matrix[3], 1) == ["d"]
    assert b2.zero_variance == 1 and r[2] == -1.0     # variância zero -> −1


def test_bm25_parametros():
    b1 = B1(["a", "b", "c"], ["repair engines and machines", "teach children to read", "paint large murals"])
    assert b1.bm25.k1 == 1.2 and b1.bm25.b == 0.75
    assert b1.rank("I like to repair machines", 1) == ["a"]


def test_desempate_pelo_codigo():
    b1 = B1(["b", "a", "c"], ["same text here", "same text here", "other words"])
    assert b1.rank("nothing matches", 3) == ["a", "b", "c"]


def test_ruido():
    base = np.array([[1.0, 7.0, 4.0, 1.2, 6.9, 3.0]] * 50)
    a = add_noise(base, 1.0, 123)
    assert a.min() >= 1.0 and a.max() <= 7.0
    assert np.array_equal(a, add_noise(base, 1.0, 123))
    assert not np.array_equal(a, add_noise(base, 1.0, 124))
    assert not np.allclose(a, base)


def test_chunking_nunca_parte_enunciado():
    count = lambda text: len(text.split())
    chunks, oversized = chunk("Title. Desc", ["a b c", "d e f g", "h " * 12, "i j"], limit=8, count=count)
    assert chunks == ["Title. Desc a b c", "d e f g", "h " * 12, "i j"]
    assert oversized == 1
