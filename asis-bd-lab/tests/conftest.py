"""
Fixtures compartilhadas para os testes do lab ASIS.
Configura TestClient do FastAPI apontando para banco de teste.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


# Banco SQLite em memória para testes (sem precisar do PostgreSQL)
SQLALCHEMY_TEST_URL = "sqlite:///./test.db"

engine_test = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Cria tabelas antes de cada teste e limpa depois."""
    Base.metadata.create_all(bind=engine_test)
    db = TestSession()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture(scope="function")
def client(db_session):
    """TestClient com banco de teste injetado."""
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine_test)

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture
def seed_produtos(db_session):
    """Popula 10 produtos no banco de teste."""
    from app.models import Produto
    produtos = []
    for i in range(1, 11):
        p = Produto(
            codigo=f"TEST-{i:04d}",
            descricao=f"Produto Teste {i}",
            ncm=f"{20000000 + i}",
            preco_unitario=round(25.0 + i * 5.0, 2),
            estoque=100,
        )
        db_session.add(p)
        produtos.append(p)
    db_session.commit()
    return produtos


@pytest.fixture
def seed_notas(db_session, seed_produtos):
    """Popula 50 notas fiscais com itens."""
    from app.models import NotaFiscal, ItemNota
    from datetime import datetime, timedelta

    notas = []
    for i in range(1, 51):
        nf = NotaFiscal(
            numero=f"TST-{i:06d}",
            emitente_cnpj=f"{11222333000100 + (i % 3):014d}",
            destinatario_cnpj=f"{44555666000100 + (i % 5):014d}",
            valor_total=round(50.0 + i * 3.0, 2),
            status="emitida",
            data_emissao=datetime(2026, 1, 1) + timedelta(hours=i),
        )
        db_session.add(nf)
        db_session.flush()

        item = ItemNota(
            nota_id=nf.id,
            produto_id=seed_produtos[i % len(seed_produtos)].id,
            quantidade=2,
            valor_unitario=seed_produtos[i % len(seed_produtos)].preco_unitario,
            valor_total=seed_produtos[i % len(seed_produtos)].preco_unitario * 2,
        )
        db_session.add(item)
        notas.append(nf)

    db_session.commit()
    return notas
