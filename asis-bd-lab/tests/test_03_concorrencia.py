"""
Driver 3 — ACESSO SIMULTÂNEO (CONCORRÊNCIA)
=============================================
Testes que verificam se a API trata corretamente acessos
simultâneos ao mesmo recurso.

Business Driver: Em um sistema fiscal com múltiplos operadores,
duas pessoas podem tentar atualizar o mesmo produto ao mesmo tempo.
Sem controle de concorrência, dados são perdidos (lost update).
"""
import pytest
from concurrent.futures import ThreadPoolExecutor


class TestConcorrenciaBugV1:
    """Testes que EXPÕEM a race condition da versão v1."""

    def test_v1_lost_update(self, client, seed_produtos):
        """
        BUG: Dois updates simultâneos causam lost update.
        Produto começa com estoque=100.
        Request A: +10 (deveria ficar 110)
        Request B: +20 (deveria ficar 130 considerando A)
        Sem lock, resultado pode ser 120 (perdeu o +10 de A).
        """
        produto = seed_produtos[0]
        estoque_inicial = produto.estoque  # 100

        # Simular dois requests "quase simultâneos" via ThreadPool
        def update_estoque(qtd):
            return client.put(
                f"/v1/produtos/{produto.id}/estoque?quantidade={qtd}"
            )

        with ThreadPoolExecutor(max_workers=2) as executor:
            f1 = executor.submit(update_estoque, 10)
            f2 = executor.submit(update_estoque, 20)

            r1 = f1.result()
            r2 = f2.result()

        # Ambos devem retornar 200
        assert r1.status_code == 200
        assert r2.status_code == 200

        # Verificar resultado final
        final = client.get(f"/v2/produtos/{produto.id}").json()
        esperado = estoque_inicial + 10 + 20  # 130

        # NOTA: Este teste pode PASSAR ou FALHAR dependendo do timing
        # Isso demonstra a natureza não-determinística de race conditions
        if final["estoque"] != esperado:
            print(
                f"LOST UPDATE detectado! "
                f"Esperado: {esperado}, Obtido: {final['estoque']}"
            )


class TestConcorrenciaFixV2:
    """Testes que VALIDAM o optimistic locking da versão v2."""

    def test_v2_update_com_version_correta(self, client, seed_produtos):
        """Update com version correta deve funcionar."""
        produto = seed_produtos[0]
        response = client.put(
            f"/v2/produtos/{produto.id}/estoque"
            f"?quantidade=10&version={produto.version}"
        )
        assert response.status_code == 200

        data = response.json()
        assert data["estoque"] == produto.estoque + 10
        assert data["version"] == produto.version + 1

    def test_v2_conflito_com_version_errada(self, client, seed_produtos):
        """Update com version desatualizada deve retornar 409 Conflict."""
        produto = seed_produtos[0]

        # Primeiro update: sucesso (version 1 → 2)
        r1 = client.put(
            f"/v2/produtos/{produto.id}/estoque"
            f"?quantidade=5&version={produto.version}"
        )
        assert r1.status_code == 200

        # Segundo update com version antiga: deve falhar
        r2 = client.put(
            f"/v2/produtos/{produto.id}/estoque"
            f"?quantidade=10&version={produto.version}"  # version antiga!
        )
        assert r2.status_code == 409, (
            "Deveria retornar 409 Conflict quando version está desatualizada"
        )

    def test_v2_conflito_mensagem_clara(self, client, seed_produtos):
        """Mensagem de erro deve orientar o usuário a recarregar."""
        produto = seed_produtos[0]

        # Atualiza para incrementar version
        client.put(
            f"/v2/produtos/{produto.id}/estoque"
            f"?quantidade=1&version={produto.version}"
        )

        # Tenta com version antiga
        r = client.put(
            f"/v2/produtos/{produto.id}/estoque"
            f"?quantidade=1&version={produto.version}"
        )

        assert r.status_code == 409
        assert "concorrência" in r.json()["detail"].lower() or \
               "conflito" in r.json()["detail"].lower(), \
            "Mensagem de erro deve mencionar concorrência ou conflito"

    def test_v2_updates_sequenciais_corretos(self, client, seed_produtos):
        """Updates sequenciais com version correta devem somar corretamente."""
        produto = seed_produtos[0]
        estoque_inicial = produto.estoque
        version_atual = produto.version

        # Update 1: +10
        r1 = client.put(
            f"/v2/produtos/{produto.id}/estoque"
            f"?quantidade=10&version={version_atual}"
        )
        assert r1.status_code == 200
        version_atual = r1.json()["version"]

        # Update 2: +20
        r2 = client.put(
            f"/v2/produtos/{produto.id}/estoque"
            f"?quantidade=20&version={version_atual}"
        )
        assert r2.status_code == 200

        assert r2.json()["estoque"] == estoque_inicial + 30
