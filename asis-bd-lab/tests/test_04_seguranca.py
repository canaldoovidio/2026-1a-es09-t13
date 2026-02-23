"""
Driver 4 — SEGURANÇA
=====================
Testes que verificam se a API está protegida contra
ataques comuns (OWASP Top 10).

Business Driver: Um sistema fiscal lida com dados sensíveis.
SQL Injection pode expor TODAS as notas fiscais de TODOS os clientes.
"""
import pytest


class TestSegurancaBugV1:
    """Testes que EXPÕEM vulnerabilidades da versão v1."""

    def test_v1_sql_injection_retorna_tudo(self, client, seed_notas):
        """
        BUG CRÍTICO: SQL Injection permite acessar TODOS os dados!
        Payload: ' OR '1'='1
        Query resultante: WHERE emitente_cnpj = '' OR '1'='1'
        → Retorna TODAS as notas do banco.
        """
        # Ataque SQL Injection
        payload = "' OR '1'='1"
        response = client.get(f"/v1/notas/busca?cnpj={payload}")

        # Se o bug existe, retorna todas as notas (não apenas as do CNPJ)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 0:
                print(
                    f"SQL INJECTION bem-sucedido! "
                    f"Retornou {len(data)} notas com payload malicioso."
                )

    def test_v1_aceita_cnpj_invalido(self, client):
        """
        BUG: v1 aceita qualquer string como CNPJ — sem validação.
        """
        response = client.get("/v1/notas/busca?cnpj=abc')--")
        # v1 não valida, então pode retornar 200 ou 500 (SQL error)
        # Ambos são problemáticos!
        assert response.status_code in [200, 500], (
            "v1 deveria ter validação, não aceitar strings arbitrárias"
        )


class TestSegurancaFixV2:
    """Testes que VALIDAM as proteções da versão v2."""

    def test_v2_sql_injection_bloqueado(self, client, seed_notas):
        """v2 deve rejeitar payloads de SQL injection."""
        payload = "' OR '1'='1"
        response = client.get(f"/v2/notas/busca?cnpj={payload}")

        # Deve ser rejeitado pela validação (422) — CNPJ deve ter 14 dígitos
        assert response.status_code == 422, (
            f"Deveria rejeitar SQL injection com 422, retornou {response.status_code}"
        )

    def test_v2_valida_formato_cnpj(self, client):
        """v2 deve aceitar apenas CNPJ com 14 dígitos numéricos."""
        # CNPJ válido (formato)
        response = client.get("/v2/notas/busca?cnpj=11222333000100")
        assert response.status_code == 200

        # CNPJ inválido — letras
        response = client.get("/v2/notas/busca?cnpj=abcdefghijklmn")
        assert response.status_code == 422

        # CNPJ inválido — curto demais
        response = client.get("/v2/notas/busca?cnpj=1122233")
        assert response.status_code == 422

        # CNPJ inválido — caracteres especiais
        response = client.get("/v2/notas/busca?cnpj=11.222.333/0001")
        assert response.status_code == 422

    def test_v2_busca_retorna_apenas_cnpj_especifico(self, client, seed_notas):
        """v2 deve retornar apenas notas do CNPJ informado."""
        cnpj = seed_notas[0].emitente_cnpj
        response = client.get(f"/v2/notas/busca?cnpj={cnpj}")
        assert response.status_code == 200

        data = response.json()
        for nota in data:
            assert nota["emitente_cnpj"] == cnpj, (
                f"Retornou nota de outro CNPJ: {nota['emitente_cnpj']}"
            )

    def test_v2_autenticacao_sem_token(self, client):
        """Endpoint protegido deve rejeitar requests sem token."""
        response = client.get("/v2/notas/protegido")
        assert response.status_code == 401

    def test_v2_autenticacao_token_invalido(self, client):
        """Endpoint protegido deve rejeitar tokens inválidos."""
        response = client.get(
            "/v2/notas/protegido",
            headers={"Authorization": "Bearer token-invalido-123"}
        )
        assert response.status_code == 401

    def test_v2_autenticacao_token_valido(self, client):
        """Login com credenciais válidas deve gerar token funcional."""
        # 1. Login
        login_response = client.post(
            "/v2/auth/token",
            json={"username": "admin", "password": "admin123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # 2. Acessar endpoint protegido
        response = client.get(
            "/v2/notas/protegido",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["user"] == "admin"

    def test_v2_login_credenciais_invalidas(self, client):
        """Login com senha errada deve retornar 401."""
        response = client.post(
            "/v2/auth/token",
            json={"username": "admin", "password": "senha-errada"}
        )
        assert response.status_code == 401
