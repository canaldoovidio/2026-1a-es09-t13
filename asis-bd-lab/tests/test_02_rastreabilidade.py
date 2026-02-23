"""
Driver 2 — RASTREABILIDADE
===========================
Testes que verificam se cada request pode ser rastreado
através de Correlation ID e logging estruturado.

Business Driver: Em um sistema fiscal, cada operação precisa ser
auditável. Um "Erro 500" sem contexto é inaceitável.
"""
import pytest
import uuid


class TestRastreabilidadeBugV1:
    """Testes que EXPÕEM os problemas da versão v1."""

    def test_v1_nao_retorna_correlation_id(self, client, seed_notas):
        """
        BUG: GET /v1/notas/{id} não retorna X-Correlation-ID no response.
        Sem isso, é impossível correlacionar logs com requests.
        """
        nota_id = seed_notas[0].id
        response = client.get(f"/v1/notas/{nota_id}")
        assert response.status_code == 200

        # v1 não inclui correlation_id no body
        data = response.json()
        assert "correlation_id" not in data, (
            "v1 não deveria ter correlation_id — é o bug!"
        )

    def test_v1_erro_sem_contexto(self, client):
        """
        BUG: Quando nota não existe, v1 retorna erro genérico
        sem informação de rastreabilidade.
        """
        response = client.get("/v1/notas/99999")
        assert response.status_code == 404
        # O log vai ser apenas "Erro: nota não encontrada" — SEM saber qual request


class TestRastreabilidadeFixV2:
    """Testes que VALIDAM a correção na versão v2."""

    def test_v2_retorna_correlation_id_no_header(self, client, seed_notas):
        """v2 deve retornar X-Correlation-ID em TODOS os responses."""
        nota_id = seed_notas[0].id
        response = client.get(f"/v2/notas/{nota_id}")
        assert response.status_code == 200

        assert "x-correlation-id" in response.headers, (
            "Response deve conter header X-Correlation-ID"
        )
        # Deve ser um UUID válido
        cid = response.headers["x-correlation-id"]
        uuid.UUID(cid)  # Valida formato UUID — levanta exceção se inválido

    def test_v2_propaga_correlation_id_do_client(self, client, seed_notas):
        """v2 deve usar o Correlation ID enviado pelo client."""
        meu_id = str(uuid.uuid4())
        nota_id = seed_notas[0].id

        response = client.get(
            f"/v2/notas/{nota_id}",
            headers={"X-Correlation-ID": meu_id}
        )

        assert response.headers["x-correlation-id"] == meu_id, (
            "Deve propagar o Correlation ID fornecido pelo client"
        )

    def test_v2_correlation_id_no_body(self, client, seed_notas):
        """v2 deve incluir correlation_id no body do response."""
        nota_id = seed_notas[0].id
        response = client.get(f"/v2/notas/{nota_id}")
        data = response.json()

        assert "correlation_id" in data, (
            "Body do response deve incluir correlation_id para facilitar debug"
        )

    def test_v2_retorna_response_time(self, client, seed_notas):
        """v2 deve incluir tempo de resposta no header."""
        nota_id = seed_notas[0].id
        response = client.get(f"/v2/notas/{nota_id}")

        assert "x-response-time" in response.headers, (
            "Header X-Response-Time é essencial para monitoramento"
        )

    def test_v2_cada_request_tem_id_unico(self, client, seed_notas):
        """Cada request sem header explícito deve gerar ID único."""
        nota_id = seed_notas[0].id

        r1 = client.get(f"/v2/notas/{nota_id}")
        r2 = client.get(f"/v2/notas/{nota_id}")

        cid1 = r1.headers["x-correlation-id"]
        cid2 = r2.headers["x-correlation-id"]

        assert cid1 != cid2, "Cada request deve ter um Correlation ID único"
