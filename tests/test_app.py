"""Testes reais usando Flask test_client e banco temporário."""
import re
import tempfile
import unittest
from pathlib import Path

from app import create_app


class ZelaBairroTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app({
            "TESTING": True,
            "DATABASE_PATH": str(Path(self.tmp.name) / "test.sqlite3"),
            "SECRET_KEY": "test-secret-key-only",
            "ADMIN_PASSWORD": "senha_teste_forte",
            "APP_ENV": "testing",
            "SESSION_COOKIE_SECURE": False,
        })
        self.client = self.app.test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def csrf(self):
        with self.client.session_transaction() as session:
            return session["csrf_token"]

    def create_occurrence(self):
        self.client.get("/registrar")
        result = self.client.post("/registrar", data={
            "csrf_token": self.csrf(),
            "categoria": "sinalizacao",
            "local": "Praça das Árvores",
            "descricao": "Placa com suporte danificado no acesso principal.",
        }, follow_redirects=False)
        self.assertEqual(result.status_code, 302)
        path = result.headers["Location"]
        match = re.search(r"(OC-[A-F0-9]{12})", path)
        self.assertIsNotNone(match)
        return match.group(1)

    def test_home_and_health(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/health").json, {"status": "ok"})

    def test_create_persist_consult_api(self):
        protocol = self.create_occurrence()
        html = self.client.get(f"/ocorrencia/{protocol}")
        self.assertEqual(html.status_code, 200)
        self.assertIn(b"Pra", html.data)
        api = self.client.get(f"/api/ocorrencias/{protocol}")
        self.assertEqual(api.status_code, 200)
        self.assertEqual(api.json["id"], protocol)
        self.assertEqual(api.json["status"], "pendente")
        self.assertEqual(self.client.get("/consulta?protocolo=" + protocol).status_code, 302)
        # Novo app com mesmo arquivo SQLite comprova persistência entre sessões.
        new_app = create_app({
            "TESTING": True,
            "DATABASE_PATH": self.app.config["DATABASE_PATH"],
            "SECRET_KEY": "test-2", "ADMIN_PASSWORD": "secret-2", "APP_ENV": "testing",
        })
        self.assertEqual(new_app.test_client().get(f"/api/ocorrencias/{protocol}").json["status"], "pendente")

    def test_validation(self):
        self.client.get("/registrar")
        result = self.client.post("/registrar", data={
            "csrf_token": self.csrf(), "categoria": "invalida", "local": "x", "descricao": "curta"
        })
        self.assertEqual(result.status_code, 200)
        self.assertIn("Selecione uma categoria".encode(), result.data)

    def test_csrf_blocks_creation(self):
        self.assertEqual(self.client.post("/registrar", data={
            "categoria": "calcada", "local": "Praça Teste",
            "descricao": "Um buraco na calçada da praça."
        }).status_code, 400)

    def test_admin_is_protected_and_updates_status(self):
        protocol = self.create_occurrence()
        fresh = self.app.test_client()
        self.assertEqual(fresh.get("/admin").status_code, 302)
        self.assertEqual(fresh.get("/admin/export.csv").status_code, 302)
        self.client.get("/admin/login")
        result = self.client.post("/admin/login", data={
            "csrf_token": self.csrf(), "password": "senha_teste_forte"
        }, follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(protocol.encode(), result.data)
        updated = self.client.post(f"/admin/ocorrencias/{protocol}/status", data={
            "csrf_token": self.csrf(), "status": "em_analise"
        })
        self.assertEqual(updated.status_code, 302)
        self.assertEqual(self.client.get(f"/api/ocorrencias/{protocol}").json["status"], "em_analise")
        self.assertEqual(self.client.get("/admin/export.csv").status_code, 200)

    def test_prevents_html_injection(self):
        self.client.get("/registrar")
        resp = self.client.post("/registrar", data={
            "csrf_token": self.csrf(),
            "categoria": "outros", "local": "<script>alert(1)</script>",
            "descricao": "Descrição usada para validar escape de HTML."
        })
        self.assertEqual(resp.status_code, 302)
        page = self.client.get(resp.headers["Location"])
        self.assertNotIn(b"<script>alert(1)</script>", page.data)
        self.assertIn(b"&lt;script&gt;", page.data)

    def test_metrics(self):
        self.client.get("/health")
        result = self.client.get("/metrics")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"zelabairro_http_requests_total", result.data)
        self.assertIn(b"zelabairro_http_request_duration_seconds", result.data)
        self.assertIn(b"zelabairro_http_in_flight_requests", result.data)


if __name__ == "__main__":
    unittest.main()
