"""Aplicação ZelaBairro: mesma base para Secure DevOps e BI & Startup."""
import os
import time
from pathlib import Path

from flask import Flask, g, request
from prometheus_client import Counter, Gauge, Histogram

from app.db import CATEGORIES, STATUSES, close_db, init_db

TRAFFIC = Counter(
    "zelabairro_http_requests_total", "Requisicoes HTTP processadas",
    ["method", "endpoint", "status"],
)
LATENCY = Histogram(
    "zelabairro_http_request_duration_seconds", "Tempo das requisicoes HTTP em segundos",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
)
ERRORS = Counter(
    "zelabairro_http_server_errors_total", "Respostas HTTP 5xx",
    ["endpoint"],
)
IN_FLIGHT = Gauge(
    "zelabairro_http_in_flight_requests", "Requisicoes em processamento no momento"
)


def create_app(test_config=None):
    app = Flask(__name__)
    data_path = os.environ.get("DATABASE_PATH") or str(Path(app.instance_path) / "zelabairro.sqlite3")
    app.config.update(
        DATABASE_PATH=data_path,
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),
        ADMIN_PASSWORD=os.environ.get("ADMIN_PASSWORD", ""),
        METRICS_TOKEN=os.environ.get("METRICS_TOKEN", ""),
        APP_ENV=os.environ.get("APP_ENV", "development"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("APP_ENV") == "production",
        MAX_CONTENT_LENGTH=64 * 1024,
    )
    if test_config:
        app.config.update(test_config)
    if app.config["APP_ENV"] == "production":
        if (not app.config["SECRET_KEY"] or app.config["SECRET_KEY"] == "dev-only-change-me" or str(app.config["SECRET_KEY"]).startswith("SUBSTITUA_")):
            raise RuntimeError("Defina SECRET_KEY forte antes de publicar.")
        if not app.config["ADMIN_PASSWORD"] or str(app.config["ADMIN_PASSWORD"]).startswith("SUBSTITUA_"):
            raise RuntimeError("Defina ADMIN_PASSWORD antes de publicar.")
        if not app.config["METRICS_TOKEN"] or len(str(app.config["METRICS_TOKEN"])) < 24:
            raise RuntimeError("Defina METRICS_TOKEN aleatorio e longo antes de publicar.")

    app.jinja_env.globals.update(categories=CATEGORIES, statuses=STATUSES)
    app.teardown_appcontext(close_db)
    from app.routes import bp
    app.register_blueprint(bp)

    @app.before_request
    def measure_start():
        if request.endpoint == "site.metrics":
            return
        g.metrics_start = time.monotonic()
        IN_FLIGHT.inc()

    @app.after_request
    def measure_end(response):
        if hasattr(g, "metrics_start"):
            elapsed = time.monotonic() - g.metrics_start
            endpoint = request.endpoint or "unknown"
            TRAFFIC.labels(request.method, endpoint, str(response.status_code)).inc()
            LATENCY.labels(request.method, endpoint).observe(elapsed)
            if response.status_code >= 500:
                ERRORS.labels(endpoint).inc()
            IN_FLIGHT.dec()
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    with app.app_context():
        init_db()
    return app
