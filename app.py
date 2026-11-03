"""App simples para demonstrar monitoramento de consultas no Datadog APM.

Endpoints:
  GET /produtos?nome=abc   -> consulta rápida (LIKE)
  GET /produtos/lenta      -> consulta propositalmente pesada (aparece como lenta no APM)
  GET /erro                -> gera erro SQL (aparece como erro no APM)
  GET /health              -> health check
"""
import os
import random
import sqlite3

from flask import Flask, jsonify, request

DB_PATH = os.getenv("DB_PATH", "exemplo.db")

app = Flask(__name__)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    db = get_db()
    db.execute(
        "CREATE TABLE IF NOT EXISTS produtos "
        "(id INTEGER PRIMARY KEY, nome TEXT, categoria TEXT, preco REAL)"
    )
    total = db.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
    if total == 0:
        categorias = ["bebidas", "limpeza", "padaria", "frios", "hortifruti"]
        dados = [
            (f"produto-{i}", random.choice(categorias), round(random.uniform(1, 200), 2))
            for i in range(3000)
        ]
        db.executemany(
            "INSERT INTO produtos (nome, categoria, preco) VALUES (?, ?, ?)", dados
        )
        db.commit()
    db.close()


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/produtos")
def listar():
    nome = request.args.get("nome", "")
    db = get_db()
    rows = db.execute(
        "SELECT * FROM produtos WHERE nome LIKE ? LIMIT 50", (f"%{nome}%",)
    ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@app.route("/produtos/lenta")
def listar_lenta():
    # Auto-join sem índice: força uma consulta pesada para aparecer no APM.
    db = get_db()
    row = db.execute(
        "SELECT COUNT(*) AS total FROM produtos a "
        "JOIN produtos b ON a.categoria = b.categoria"
    ).fetchone()
    db.close()
    return jsonify(total=row["total"])


@app.route("/erro")
def erro():
    db = get_db()
    try:
        db.execute("SELECT * FROM tabela_que_nao_existe")
    finally:
        db.close()
    return jsonify(ok=True)


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
