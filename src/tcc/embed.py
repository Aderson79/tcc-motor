"""Chunking, embeddings and exact search in pgvector (Etapa 2)."""
from __future__ import annotations

import json
import sys
from functools import lru_cache

import numpy as np

from . import catalog
from .common import GEN, ROOT, config


@lru_cache(maxsize=1)
def model():
    from sentence_transformers import SentenceTransformer
    cfg = config()["embedding"]
    m = SentenceTransformer(cfg["model"], revision=cfg["revision"])
    m.max_seq_length = cfg["max_seq_length"]
    return m


def n_tokens(text: str) -> int:
    """Token count of the model tokenizer, special tokens included, without truncation."""
    return len(model().tokenizer(text, add_special_tokens=True, truncation=False)["input_ids"])


def chunk(head: str, tasks: list[str], limit: int, count=n_tokens) -> tuple[list[str], int]:
    """Greedy chunking that never splits a statement.

    Returns the chunks and the number of single pieces that alone exceed the limit
    (those stay in a chunk of their own and are truncated by the model).
    """
    chunks: list[str] = []
    current = head
    oversized = int(count(head) > limit)
    for task in tasks:
        candidate = f"{current} {task}"
        if count(candidate) <= limit:
            current = candidate
        else:
            chunks.append(current)
            current = task
            oversized += int(count(task) > limit)
    chunks.append(current)
    return chunks, oversized


def embed_texts(texts: list[str]) -> np.ndarray:
    return model().encode(texts, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)


def embed_query(text: str) -> np.ndarray:
    return embed_texts([text])[0]


def occupation_vector(chunks: list[str]) -> np.ndarray:
    mean = embed_texts(chunks).mean(axis=0)
    return mean / np.linalg.norm(mean)


@lru_cache(maxsize=1)
def connection():
    import psycopg
    from pgvector.psycopg import register_vector
    conn = psycopg.connect(config()["database"]["dsn"], autocommit=True)
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    register_vector(conn)
    return conn


def search(vector: np.ndarray, k: int) -> list[str]:
    """Exact cosine search; ties broken by code."""
    rows = connection().execute(
        "SELECT code FROM occupations ORDER BY embedding <=> %s, code LIMIT %s",
        (np.asarray(vector, dtype=np.float32), k)).fetchall()
    return [r[0] for r in rows]


def pin() -> None:
    """Record the Hugging Face revision and library version in config.yaml (before lock)."""
    import sentence_transformers
    from huggingface_hub import model_info
    cfg = config()["embedding"]
    sha = model_info(cfg["model"]).sha
    path = ROOT / "config.yaml"
    text = path.read_text(encoding="utf-8")
    lines = []
    for line in text.splitlines():
        if line.startswith("  revision:"):
            line = f'  revision: "{sha}"'
        elif line.startswith("  sentence_transformers_version:"):
            line = f'  sentence_transformers_version: "{sentence_transformers.__version__}"'
        lines.append(line)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    config.cache_clear()
    print(f"revision={sha} sentence-transformers={sentence_transformers.__version__}")


def main() -> None:
    if "--pin" in sys.argv:
        pin()
        return
    cfg = config()["embedding"]
    if not cfg["revision"]:
        raise SystemExit("Rode antes `python -m tcc.embed --pin` para fixar a revisão do modelo.")
    cat = catalog.load()
    limit = cfg["max_seq_length"]
    n_chunks, oversized_total, vectors = [], 0, []
    for code in cat.codes:
        row = cat.df.loc[code]
        chunks, oversized = chunk(f"{row.title}. {row.description}", cat.tasks[code], limit)
        n_chunks.append(len(chunks))
        oversized_total += oversized
        vectors.append(occupation_vector(chunks))
    conn = connection()
    conn.execute("DROP TABLE IF EXISTS occupations")
    conn.execute(f"CREATE TABLE occupations (code text primary key, title text, embedding vector({cfg['dim']}))")
    with conn.cursor() as cur:
        cur.executemany("INSERT INTO occupations (code, title, embedding) VALUES (%s, %s, %s)",
                        [(c, cat.df.at[c, "title"], v.astype(np.float32)) for c, v in zip(cat.codes, vectors)])
    indexes = conn.execute("SELECT count(*) FROM pg_indexes WHERE tablename = 'occupations' "
                           "AND indexname <> 'occupations_pkey'").fetchone()[0]
    assert indexes == 0, "não pode haver índice aproximado"
    report = {
        "occupations": len(cat.codes),
        "occupations_split": int(sum(n > 1 for n in n_chunks)),
        "occupations_split_pct": round(100 * sum(n > 1 for n in n_chunks) / len(n_chunks), 3),
        "chunks_mean": float(np.mean(n_chunks)),
        "chunks_max": int(max(n_chunks)),
        "statements_over_limit": int(oversized_total),
        "device": str(model().device),
    }
    GEN.mkdir(parents=True, exist_ok=True)
    (GEN / "embed_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
