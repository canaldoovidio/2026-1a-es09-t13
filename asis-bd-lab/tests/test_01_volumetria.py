"""
Driver 1 — VOLUMETRIA
=====================
Testes que verificam se a API respeita limites de paginação
e não retorna datasets inteiros sem controle.

Business Driver: A API ASIS precisa suportar 50k+ notas fiscais.
Sem paginação, um único GET pode derrubar o serviço.
"""
import pytest


class TestVolumetriaBugV1:
    """Testes que EXPÕEM o bug da versão v1 (sem paginação)."""

    def test_v1_retorna_todos_registros_sem_limite(self, client, seed_notas):
        """
        BUG: GET /v1/notas retorna TODAS as 50 notas de uma vez.
        Em produção com 50k registros, isso causaria timeout.
        """
        response = client.get("/v1/notas")
        assert response.status_code == 200

        data = response.json()
        # O bug é evidente: retorna TODOS os registros
        assert len(data) == 50, (
            f"v1 retornou {len(data)} notas — DEVERIA ter paginação!"
        )

    def test_v1_nao_aceita_parametro_limit(self, client, seed_notas):
        """Bug: v1 ignora query params de paginação."""
        response = client.get("/v1/notas?limit=5")
        data = response.json()
        # Mesmo passando limit=5, retorna tudo
        assert len(data) > 5, "v1 não implementa paginação"


class TestVolumetriaFixV2:
    """Testes que VALIDAM a correção na versão v2."""

    def test_v2_paginacao_padrao_20(self, client, seed_notas):
        """v2 deve retornar no máximo 20 registros por padrão."""
        response = client.get("/v2/notas")
        assert response.status_code == 200

        data = response.json()
        assert len(data) <= 20, (
            f"Paginação padrão deveria limitar a 20, retornou {len(data)}"
        )

    def test_v2_paginacao_com_limit(self, client, seed_notas):
        """v2 deve respeitar o parâmetro limit."""
        response = client.get("/v2/notas?limit=5")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 5

    def test_v2_paginacao_com_offset(self, client, seed_notas):
        """v2 deve suportar offset para navegação entre páginas."""
        page1 = client.get("/v2/notas?limit=10&offset=0").json()
        page2 = client.get("/v2/notas?limit=10&offset=10").json()

        # Páginas não devem ter sobreposição
        ids_page1 = {n["id"] for n in page1}
        ids_page2 = {n["id"] for n in page2}
        assert ids_page1.isdisjoint(ids_page2), "Páginas não devem sobrepor"

    def test_v2_limite_maximo_100(self, client, seed_notas):
        """v2 deve rejeitar limit > 100 para proteger a API."""
        response = client.get("/v2/notas?limit=500")
        assert response.status_code == 422, (
            "Deveria rejeitar limit > 100 com erro de validação"
        )

    def test_v2_limit_minimo_1(self, client, seed_notas):
        """v2 deve rejeitar limit < 1."""
        response = client.get("/v2/notas?limit=0")
        assert response.status_code == 422
