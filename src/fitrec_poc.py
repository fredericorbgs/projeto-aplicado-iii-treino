#!/usr/bin/env python3
"""Extrai userId, sport, timestamp e gender do FitRec filtrado e treina a prova de conceito.

Não grava o JSON de 5 GB. Descarta GPS, frequência cardíaca e demais séries.
"""

from __future__ import annotations

import json
import math
import re
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

URL = "https://mcauleylab.ucsd.edu/public_datasets/gdrive/fitrec/endomondoHR_proper.json"
OUT = Path(__file__).resolve().parent / "a2-poc-stats.json"
TOKEN = re.compile(
    r"'sport': '([^']*)'|'id': (\d+)|'gender': '([^']*)'|'timestamp': \[(\d+)|'userId': (\d+)"
)


def _flush(state: dict, rows: list) -> None:
    if state.get("sport") and state.get("user") and state.get("ts") is not None:
        rows.append((state["user"], state["sport"], state["ts"], state.get("gender") or "", state.get("id") or ""))


def feed(data: str, state: dict, rows: list) -> str:
    """Fecha a sessão anterior ao ver o próximo 'sport'. A ordem dos campos varia."""
    matches = list(TOKEN.finditer(data))
    safe = [m for m in matches if m.end() <= len(data) - 80]
    if not safe:
        return data[-200:] if len(data) > 200 else data
    for m in safe:
        sport, sid, gender, ts, user = m.groups()
        if sport is not None:
            _flush(state, rows)
            state.clear()
            state["sport"] = sport
        elif sid is not None and state.get("sport") and not state.get("id"):
            state["id"] = sid
        elif gender is not None and state.get("sport") and not state.get("gender"):
            state["gender"] = gender
        elif ts is not None and state.get("sport") and state.get("ts") is None:
            state["ts"] = int(ts)
        elif user is not None and state.get("sport") and not state.get("user"):
            state["user"] = user
    return data[safe[-1].end() :]


def dcg_at(rank: int) -> float:
    return 1.0 / math.log2(rank + 1)


def metrics(ranks: list[int], k: int, n_items: int) -> dict:
    """ranks: 1-based rank of the held-out sport. 0 if absent from the catalog."""
    n = len(ranks)
    hit = 0
    prec = 0.0
    ndcg = 0.0
    for r in ranks:
        if 1 <= r <= k:
            hit += 1
            prec += 1.0 / k
            ndcg += dcg_at(r)
    # random: one relevant item, uniform among n_items
    rand_hit = min(k, n_items) / n_items
    rand_ndcg = sum(dcg_at(r) for r in range(1, min(k, n_items) + 1)) / n_items
    return {
        "n": n,
        "precision": round(prec / n, 4),
        "recall": round(hit / n, 4),
        "ndcg": round(ndcg / n, 4),
        "random_precision": round(rand_hit / k, 4),
        "random_recall": round(rand_hit, 4),
        "random_ndcg": round(rand_ndcg, 4),
    }


def main() -> None:
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
            if seen // (50 << 20) != (seen - len(chunk)) // (50 << 20):
                print(f"bytes={seen} rows={len(rows)}", flush=True)
    if carry:
        feed(carry + (" " * 80), state, rows)
    _flush(state, rows)
    print(f"done bytes={seen} rows={len(rows)}", flush=True)

    ids = [r[4] for r in rows if r[4]]
    dup = len(ids) - len(set(ids))
    sports = Counter(r[1] for r in rows)
    genders = Counter(r[3] or "ausente" for r in rows)
    by_user: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for user, sport, ts, _g, _i in rows:
        by_user[user].append((ts, sport))
    lengths = [len(v) for v in by_user.values()]
    lengths.sort()

    def pct(p: float) -> int:
        if not lengths:
            return 0
        i = min(len(lengths) - 1, max(0, int(round(p * (len(lengths) - 1)))))
        return lengths[i]

    # model: users with at least 10 sessions
    train_counts: dict[str, Counter] = {}
    test: list[tuple[str, str]] = []
    for user, seq in by_user.items():
        if len(seq) < 10:
            continue
        seq.sort()
        held = seq[-1][1]
        train_counts[user] = Counter(s for _t, s in seq[:-1])
        test.append((user, held))

    item_index = {}
    for counts in train_counts.values():
        for sport in counts:
            if sport not in item_index:
                item_index[sport] = len(item_index)
    items = [None] * len(item_index)
    for sport, j in item_index.items():
        items[j] = sport
    n_items = len(items)
    # item-item cosine on binary user vectors would be heavy; co-occurrence on counts:
    # represent each item as a vector over users (956). Fine.
    import numpy as np

    users = list(train_counts)
    uindex = {u: i for i, u in enumerate(users)}
    mat = np.zeros((len(users), n_items), dtype=np.float64)
    for u, counts in train_counts.items():
        i = uindex[u]
        for sport, c in counts.items():
            mat[i, item_index[sport]] = c
    norms = np.linalg.norm(mat, axis=0)
    norms[norms == 0] = 1.0
    normed = mat / norms
    sim = normed.T @ normed
    # A diagonal permanece 1: a próxima sessão pode ser a mesma modalidade.
    pop = mat.sum(axis=0)

    def ranks_for(score_of) -> list[int]:
        out = []
        for user, held in test:
            scores = score_of(user)
            if held not in item_index:
                out.append(0)
                continue
            j = item_index[held]
            better = int(np.sum(scores > scores[j]))
            out.append(better + 1)
        return out

    def knn_scores(user: str) -> np.ndarray:
        hist = np.zeros(n_items, dtype=np.float64)
        for sport, c in train_counts[user].items():
            hist[item_index[sport]] = c
        return sim @ hist

    def pop_scores(_user: str) -> np.ndarray:
        return pop

    def habit_scores(user: str) -> np.ndarray:
        hist = np.zeros(n_items, dtype=np.float64)
        for sport, c in train_counts[user].items():
            hist[item_index[sport]] = c
        return hist

    def combo_scores(user: str) -> np.ndarray:
        """Soma o hábito e a vizinhança, cada um reescalado pelo próprio máximo."""
        parts = []
        for raw in (habit_scores(user), knn_scores(user)):
            top = float(raw.max()) if raw.size else 0.0
            parts.append(raw if top <= 0 else raw / top)
        return parts[0] + parts[1]

    knn_ranks = ranks_for(knn_scores)
    pop_ranks = ranks_for(pop_scores)
    habit_ranks = ranks_for(habit_scores)
    combo_ranks = ranks_for(combo_scores)
    switch_at = []
    for i, (user, held) in enumerate(test):
        mode = train_counts[user].most_common(1)[0][0]
        if held != mode:
            switch_at.append(i)
    sessoes_piso = sum(len(v) for u, v in by_user.items() if len(v) >= 10)
    summary = {
        "bytes_read": seen,
        "sessoes": len(rows),
        "usuarios": len(by_user),
        "modalidades": len(sports),
        "ids_duplicados": dup,
        "genero": genders.most_common(),
        "sessoes_por_usuario": {
            "min": lengths[0] if lengths else 0,
            "p25": pct(0.25),
            "mediana": pct(0.50),
            "p75": pct(0.75),
            "max": lengths[-1] if lengths else 0,
            "media": round(sum(lengths) / len(lengths), 1) if lengths else 0,
        },
        "top_modalidades": sports.most_common(12),
        "piso_10": {
            "usuarios": len(test),
            "sessoes": sessoes_piso,
            "modalidades_no_treino": n_items,
        },
        "avaliacao": {},
    }
    for k in (5, 10):
        summary["avaliacao"][str(k)] = {
            "vizinhanca_itens": metrics(knn_ranks, k, n_items),
            "popularidade": metrics(pop_ranks, k, n_items),
            "habito": metrics(habit_ranks, k, n_items),
        }
    def pack(ranks: list[int]) -> dict:
        return {str(k): metrics(ranks, k, n_items) for k in (1, 5, 10)}

    def take(ranks: list[int]) -> list[int]:
        return [ranks[i] for i in switch_at]

    ajuste = {
        "n_teste": len(test),
        "n_troca": len(switch_at),
        "n_repeticao": len(test) - len(switch_at),
        "todos": {
            "vizinhanca_itens": pack(knn_ranks),
            "habito": pack(habit_ranks),
            "popularidade": pack(pop_ranks),
            "combinado": pack(combo_ranks),
        },
        "troca": {
            "vizinhanca_itens": pack(take(knn_ranks)),
            "habito": pack(take(habit_ranks)),
            "popularidade": pack(take(pop_ranks)),
            "combinado": pack(take(combo_ranks)),
        },
    }
    ajuste_path = Path(__file__).resolve().parent / "a3-ajuste-stats.json"
    ajuste_path.write_text(json.dumps(ajuste, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(ajuste, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
