#!/usr/bin/env python3
"""Exporta o modelo agregado usado na demonstração local (app/).

Lê o FitRec filtrado em fluxo, monta o mesmo treino de fitrec_poc.py e grava só agregados:
modalidades, popularidade no treino e cosseno entre modalidades. Nenhuma linha de usuário sai daqui.
Antes de gravar, confere as métricas com resultados/reavaliacao.json.
"""

from __future__ import annotations

import json
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from fitrec_poc import URL, _flush, feed, metrics

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "app" / "modelo.js"
REAVALIACAO = ROOT / "resultados" / "reavaliacao.json"


def read_rows() -> list[tuple[str, str, int, str, str]]:
    rows: list[tuple[str, str, int, str, str]] = []
    state: dict = {}
    carry = ""
    seen = 0
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            seen += len(chunk)
            carry = feed(carry + chunk.decode("utf-8", "replace"), state, rows)
            if seen // (200 << 20) != (seen - len(chunk)) // (200 << 20):
                print(f"bytes={seen} rows={len(rows)}", flush=True)
    if carry:
        feed(carry + (" " * 80), state, rows)
    _flush(state, rows)
    print(f"done bytes={seen} rows={len(rows)}", flush=True)
    return rows


def main() -> None:
    rows = read_rows()
    by_user: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for user, sport, ts, _g, _i in rows:
        by_user[user].append((ts, sport))

    train_counts: dict[str, Counter] = {}
    test: list[tuple[str, str]] = []
    for user, seq in by_user.items():
        if len(seq) < 10:
            continue
        seq.sort()
        train_counts[user] = Counter(s for _t, s in seq[:-1])
        test.append((user, seq[-1][1]))

    item_index: dict[str, int] = {}
    for counts in train_counts.values():
        for sport in counts:
            if sport not in item_index:
                item_index[sport] = len(item_index)
    items = sorted(item_index, key=item_index.get)
    n_items = len(items)

    users = list(train_counts)
    mat = np.zeros((len(users), n_items), dtype=np.float64)
    for i, user in enumerate(users):
        for sport, c in train_counts[user].items():
            mat[i, item_index[sport]] = c
    norms = np.linalg.norm(mat, axis=0)
    norms[norms == 0] = 1.0
    normed = mat / norms
    sim = normed.T @ normed
    pop = mat.sum(axis=0)

    def hist_of(user: str) -> np.ndarray:
        h = np.zeros(n_items)
        for sport, c in train_counts[user].items():
            h[item_index[sport]] = c
        return h

    def rank(scores: np.ndarray, held: str) -> int:
        if held not in item_index:
            return 0
        j = item_index[held]
        return int(np.sum(scores > scores[j])) + 1

    def combo(h: np.ndarray) -> np.ndarray:
        parts = []
        for raw in (h, sim @ h):
            top = float(raw.max()) if raw.size else 0.0
            parts.append(raw if top <= 0 else raw / top)
        return parts[0] + parts[1]

    ranks = {"habito": [], "vizinhanca_itens": [], "popularidade": [], "combinado": []}
    for user, held in test:
        h = hist_of(user)
        ranks["habito"].append(rank(h, held))
        ranks["vizinhanca_itens"].append(rank(sim @ h, held))
        ranks["popularidade"].append(rank(pop, held))
        ranks["combinado"].append(rank(combo(h), held))

    esperado = json.loads(REAVALIACAO.read_text(encoding="utf-8"))
    for nome, rs in ranks.items():
        for k in (1, 5, 10):
            got = metrics(rs, k, n_items)
            want = esperado["todos"][nome][str(k)]
            for campo in ("recall", "ndcg"):
                if abs(got[campo] - want[campo]) > 1e-9:
                    raise SystemExit(f"divergência em {nome} K={k} {campo}: {got[campo]} != {want[campo]}")
    print("métricas conferem com resultados/reavaliacao.json", flush=True)

    modelo = {
        "fonte": "FitRec filtrado (Ni, Muhlstein e McAuley, 2019), treino com piso de dez sessões e última sessão retida",
        "usuarios_no_treino": len(users),
        "modalidades": items,
        "popularidade": [int(v) for v in pop],
        "similaridade": [[round(float(v), 6) for v in row] for row in sim],
        "resultados": {
            "n_teste": esperado["n_teste"],
            "n_troca": esperado["n_troca"],
            "todos_recall1": {k: esperado["todos"][k]["1"]["recall"] for k in ranks},
            "troca_recall1": {k: esperado["troca"][k]["1"]["recall"] for k in ranks},
            "aleatorio_recall1": esperado["todos"]["habito"]["1"]["random_recall"],
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("window.MODELO = " + json.dumps(modelo, ensure_ascii=False) + ";\n", encoding="utf-8")
    print(f"gravado {OUT} ({n_items} modalidades)", flush=True)


if __name__ == "__main__":
    main()
