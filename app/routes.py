"""Rotas públicas e controle administrativo interno."""
import csv
import hmac
import io
import re
import secrets
from datetime import datetime, timezone
from functools import wraps

from flask import (
    Blueprint, Response, abort, current_app, flash, jsonify,
    redirect, render_template, request, session, url_for,
)
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.db import (
    CATEGORIES, STATUSES, get_db, get_occurrence, insert_occurrence,
    list_occurrences, update_status,
)

bp = Blueprint("site", __name__)
ID_RE = re.compile(r"^OC-[A-F0-9]{12}$")


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]


def csrf_valid():
    expected = session.get("csrf_token", "")
    supplied = request.form.get("csrf_token", "")
    return bool(expected and supplied and hmac.compare_digest(expected, supplied))


@bp.app_context_processor
def inject_csrf():
    return {"csrf_token": csrf_token}


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if session.get("is_admin") is not True:
            return redirect(url_for("site.admin_login"))
        return fn(*args, **kwargs)
    return wrapper


@bp.get("/")
def home():
    return render_template("home.html")


@bp.route("/registrar", methods=["GET", "POST"])
def register():
    fields = {"local": "", "categoria": "", "descricao": ""}
    errors = []
    if request.method == "POST":
        if not csrf_valid():
            abort(400, "Formulário inválido. Atualize a página e tente novamente.")
        fields = {key: request.form.get(key, "").strip() for key in fields}
        if not 3 <= len(fields["local"]) <= 120:
            errors.append("Informe um local entre 3 e 120 caracteres.")
        if fields["categoria"] not in CATEGORIES:
            errors.append("Selecione uma categoria válida.")
        if not 10 <= len(fields["descricao"]) <= 1000:
            errors.append("Descreva o problema com 10 a 1.000 caracteres.")
        if not errors:
            now = datetime.now(timezone.utc).isoformat(timespec="seconds")
            # 48 bits aleatórios para evitar protocolos sequenciais fáceis de enumerar.
            occurrence = {
                "id": "OC-" + secrets.token_hex(6).upper(),
                **fields,
                "status": "pendente",
                "data": now,
                "data_atualizacao": now,
            }
            insert_occurrence(occurrence)
            flash("Ocorrência registrada com sucesso! Guarde seu protocolo.", "success")
            return redirect(url_for("site.occurrence", occurrence_id=occurrence["id"]))
    return render_template("register.html", fields=fields, errors=errors)


@bp.get("/consulta")
def search():
    query = request.args.get("protocolo", "").strip().upper()
    if query:
        if not ID_RE.fullmatch(query):
            return render_template("search.html", error="Formato de protocolo inválido.", query=query), 400
        return redirect(url_for("site.occurrence", occurrence_id=query))
    return render_template("search.html", query="", error=None)


@bp.get("/ocorrencia/<occurrence_id>")
def occurrence(occurrence_id):
    if not ID_RE.fullmatch(occurrence_id):
        abort(404)
    item = get_occurrence(occurrence_id)
    if item is None:
        abort(404)
    return render_template("occurrence.html", item=item)


@bp.get("/api/ocorrencias/<occurrence_id>")
def api_occurrence(occurrence_id):
    if not ID_RE.fullmatch(occurrence_id):
        return jsonify(error="Protocolo inválido"), 404
    item = get_occurrence(occurrence_id)
    if not item:
        return jsonify(error="Ocorrência não encontrada"), 404
    return jsonify(dict(item))


@bp.get("/health")
def health():
    try:
        get_db().execute("SELECT 1").fetchone()
    except Exception:
        return jsonify(status="degraded"), 503
    return jsonify(status="ok")


@bp.get("/metrics")
def metrics():
    return Response(generate_latest(), content_type=CONTENT_TYPE_LATEST)


@bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if not current_app.config["ADMIN_PASSWORD"]:
        return render_template("admin_login.html", not_configured=True), 503
    if request.method == "POST":
        if not csrf_valid():
            abort(400)
        password = request.form.get("password", "")
        if hmac.compare_digest(password, current_app.config["ADMIN_PASSWORD"]):
            session.clear()
            session["is_admin"] = True
            session["csrf_token"] = secrets.token_urlsafe(32)
            return redirect(url_for("site.admin"))
        flash("Senha incorreta.", "error")
    return render_template("admin_login.html", not_configured=False)


@bp.post("/admin/logout")
@admin_required
def admin_logout():
    if not csrf_valid():
        abort(400)
    session.clear()
    return redirect(url_for("site.home"))


@bp.get("/admin")
@admin_required
def admin():
    return render_template("admin.html", items=list_occurrences())


@bp.post("/admin/ocorrencias/<occurrence_id>/status")
@admin_required
def admin_update(occurrence_id):
    if not csrf_valid():
        abort(400)
    status = request.form.get("status", "")
    if status not in STATUSES:
        abort(400)
    if not update_status(occurrence_id, status):
        abort(404)
    flash("Status interno atualizado.", "success")
    return redirect(url_for("site.admin"))


@bp.get("/admin/export.csv")
@admin_required
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "categoria", "local", "descricao", "status", "data", "data_atualizacao"])
    for item in get_db().execute("SELECT * FROM ocorrencias ORDER BY data DESC"):
        # Evitar execução de fórmulas ao abrir dados de usuários no Excel.
        safe = []
        for field in [item[k] for k in ("id", "categoria", "local", "descricao", "status", "data", "data_atualizacao")]:
            value = str(field)
            if value.lstrip().startswith(("=", "+", "-", "@")):
                value = "'" + value
            safe.append(value)
        writer.writerow(safe)
    return Response(
        "\ufeff" + output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=zelabairro_ocorrencias.csv"},
    )


@bp.app_errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404
