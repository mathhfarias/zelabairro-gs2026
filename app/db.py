"""Persistência SQLite para o MVP ZelaBairro.

IDs são protocolos públicos e não equivalem a protocolo oficial da prefeitura.
"""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from flask import current_app, g

CATEGORIES = {
    "sinalizacao": "Sinalização",
    "mobiliario": "Mobiliário urbano",
    "calcada": "Calçada",
    "outros": "Outros",
}
STATUSES = {
    "pendente": "Pendente",
    "em_analise": "Em análise",
    "concluido": "Concluído (fluxo interno)",
}


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_db():
    if "db" not in g:
        db_file = Path(current_app.config["DATABASE_PATH"])
        db_file.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(str(db_file), timeout=15)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout = 15000")
        g.db = db
    return g.db


def close_db(_exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS ocorrencias (
            id TEXT PRIMARY KEY,
            categoria TEXT NOT NULL,
            local TEXT NOT NULL,
            descricao TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pendente',
            data TEXT NOT NULL,
            data_atualizacao TEXT NOT NULL,
            CHECK (status IN ('pendente', 'em_analise', 'concluido'))
        )
    """)
    db.execute("CREATE INDEX IF NOT EXISTS idx_ocorrencias_data ON ocorrencias(data DESC)")
    db.commit()


def insert_occurrence(occurrence):
    db = get_db()
    db.execute("""
        INSERT INTO ocorrencias (id, categoria, local, descricao, status, data, data_atualizacao)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        occurrence["id"], occurrence["categoria"], occurrence["local"],
        occurrence["descricao"], occurrence["status"],
        occurrence["data"], occurrence["data_atualizacao"],
    ))
    db.commit()


def get_occurrence(occurrence_id):
    return get_db().execute(
        "SELECT * FROM ocorrencias WHERE id = ?", (occurrence_id,)
    ).fetchone()


def list_occurrences():
    return get_db().execute(
        "SELECT * FROM ocorrencias ORDER BY data DESC LIMIT 200"
    ).fetchall()


def update_status(occurrence_id, new_status):
    db = get_db()
    cur = db.execute(
        "UPDATE ocorrencias SET status = ?, data_atualizacao = ? WHERE id = ?",
        (new_status, utc_now(), occurrence_id),
    )
    db.commit()
    return cur.rowcount > 0
