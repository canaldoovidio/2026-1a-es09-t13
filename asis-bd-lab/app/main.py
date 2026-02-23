"""
ASIS TaxTech Lab — FastAPI Application
=======================================
API com bugs INTENCIONAIS para exercício de Business Drivers.

Cada endpoint possui uma versão "quebrada" (v1) e uma versão "corrigida" (v2).
Os alunos devem identificar os problemas e entender como os testes os capturam.

Business Drivers exercitados:
  1. Volumetria      — /v1/notas vs /v2/notas
  2. Rastreabilidade — middleware de correlation ID
  3. Concorrência    — /v1/produtos/{id}/estoque vs /v2/produtos/{id}/estoque
  4. Segurança       — /v1/notas/busca vs /v2/notas/busca
"""
import os
import uuid
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text
from jose import jwt

from app.database import engine, get_db, Base
from app.models import Produto, NotaFiscal, ItemNota
from app.schemas import (
    ProdutoResponse, ProdutoCreate, ProdutoUpdate,
    NotaFiscalResponse, NotaFiscalCreate,
    Token, LoginRequest,
)

# ─── Config ─────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "asis-lab-secret-key-2026")
ALGORITHM = "HS256"

logger = logging.getLogger("asis_taxtech")
logging.basicConfig(level=logging.INFO)


# ─── Lifespan: seed do banco ────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Cria tabelas e popula dados de exemplo no startup."""
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield


app = FastAPI(
    title="ASIS TaxTech Lab",
    description="Lab de Business Drivers — ES09 Inteli",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════
# MIDDLEWARE — RASTREABILIDADE (Driver 2)
# ═══════════════════════════════════════════════════════════

@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    """
    VERSÃO CORRIGIDA (v2): Injeta X-Correlation-ID em cada request.

    A versão v1 dos endpoints NÃO usa este middleware — os logs
    ficam sem contexto, impossibilitando rastreabilidade.
    """
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id

    # Log estruturado com contexto
    logger.info(
        "request_started",
        extra={
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    start = time.time()
    response: Response = await call_next(request)
    duration = time.time() - start

    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Response-Time"] = f"{duration:.4f}s"

    logger.info(
        "request_completed",
        extra={
            "correlation_id": correlation_id,
            "status_code": response.status_code,
            "duration_seconds": round(duration, 4),
        }
    )

    return response


# ═══════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "asis-taxtech-lab"}


# ═══════════════════════════════════════════════════════════
# DRIVER 1 — VOLUMETRIA
# ═══════════════════════════════════════════════════════════

@app.get("/v1/notas", response_model=list[NotaFiscalResponse])
def listar_notas_v1(db: Session = Depends(get_db)):
    """
    BUG INTENCIONAL: Retorna TODAS as notas sem paginação.
    Em produção com 50k+ registros, isso causa:
      - Timeout na API
      - Consumo excessivo de memória
      - N+1 queries (cada nota carrega itens separadamente)
    """
    notas = db.query(NotaFiscal).all()

    # Bug N+1: acessar itens de cada nota dispara query individual
    for nota in notas:
        _ = nota.itens  # força lazy loading — N+1!

    return notas


@app.get("/v2/notas", response_model=list[NotaFiscalResponse])
def listar_notas_v2(
    limit: int = Query(default=20, le=100, ge=1),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """
    VERSÃO CORRIGIDA:
      - Paginação com limit/offset
      - Eager loading com joinedload (elimina N+1)
      - Limite máximo de 100 registros por página
    """
    notas = (
        db.query(NotaFiscal)
        .options(joinedload(NotaFiscal.itens))
        .order_by(NotaFiscal.id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    return notas


# ═══════════════════════════════════════════════════════════
# DRIVER 2 — RASTREABILIDADE (endpoints de demonstração)
# ═══════════════════════════════════════════════════════════

@app.get("/v1/notas/{nota_id}")
def obter_nota_v1(nota_id: int, db: Session = Depends(get_db)):
    """
    BUG INTENCIONAL: Log sem contexto — impossível rastrear.
    Quando dá erro, o log diz apenas "Erro ao buscar nota".
    """
    # Log SEM correlation ID, SEM contexto
    print(f"Buscando nota {nota_id}")  # print() em vez de logger!

    nota = db.query(NotaFiscal).filter(NotaFiscal.id == nota_id).first()
    if not nota:
        print("Erro: nota não encontrada")  # Sem saber QUAL request falhou
        raise HTTPException(status_code=404, detail="Nota não encontrada")

    return {
        "id": nota.id,
        "numero": nota.numero,
        "valor_total": nota.valor_total,
        "status": nota.status,
    }


@app.get("/v2/notas/{nota_id}")
def obter_nota_v2(nota_id: int, request: Request, db: Session = Depends(get_db)):
    """
    VERSÃO CORRIGIDA: Log estruturado COM correlation ID.
    Cada log entry pode ser rastreada até o request original.
    """
    cid = getattr(request.state, "correlation_id", "N/A")

    logger.info(
        "buscar_nota",
        extra={"correlation_id": cid, "nota_id": nota_id}
    )

    nota = db.query(NotaFiscal).filter(NotaFiscal.id == nota_id).first()
    if not nota:
        logger.warning(
            "nota_nao_encontrada",
            extra={"correlation_id": cid, "nota_id": nota_id}
        )
        raise HTTPException(status_code=404, detail="Nota não encontrada")

    logger.info(
        "nota_encontrada",
        extra={
            "correlation_id": cid,
            "nota_id": nota_id,
            "numero": nota.numero,
        }
    )

    return {
        "id": nota.id,
        "numero": nota.numero,
        "valor_total": nota.valor_total,
        "status": nota.status,
        "correlation_id": cid,
    }


# ═══════════════════════════════════════════════════════════
# DRIVER 3 — ACESSO SIMULTÂNEO (CONCORRÊNCIA)
# ═══════════════════════════════════════════════════════════

@app.put("/v1/produtos/{produto_id}/estoque")
def atualizar_estoque_v1(
    produto_id: int,
    quantidade: int = Query(...),
    db: Session = Depends(get_db),
):
    """
    BUG INTENCIONAL: Race condition — lost update.
    Dois requests simultâneos podem sobrescrever um ao outro:
      1. Request A lê estoque = 100
      2. Request B lê estoque = 100
      3. Request A escreve estoque = 100 - 5 = 95
      4. Request B escreve estoque = 100 - 3 = 97  ← PERDEU o -5 de A!
    """
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Simula processamento lento (aumenta janela de race condition)
    time.sleep(0.1)

    # Atualização SEM lock — vulnerável a lost update
    produto.estoque = produto.estoque + quantidade
    db.commit()
    db.refresh(produto)

    return {"id": produto.id, "estoque": produto.estoque}


@app.put("/v2/produtos/{produto_id}/estoque")
def atualizar_estoque_v2(
    produto_id: int,
    quantidade: int = Query(...),
    version: int = Query(..., description="Versão atual do produto"),
    db: Session = Depends(get_db),
):
    """
    VERSÃO CORRIGIDA: Optimistic locking.
    Usa coluna `version` para detectar conflitos:
      1. Client envia version que ele leu
      2. UPDATE só executa WHERE version = version_enviada
      3. Se outro request já atualizou, rows_affected = 0 → 409 Conflict
    """
    result = db.execute(
        text("""
            UPDATE produtos
            SET estoque = estoque + :quantidade,
                version = version + 1
            WHERE id = :id AND version = :version
        """),
        {"quantidade": quantidade, "id": produto_id, "version": version}
    )
    db.commit()

    if result.rowcount == 0:
        raise HTTPException(
            status_code=409,
            detail="Conflito de concorrência — o registro foi alterado por outro usuário. Recarregue e tente novamente."
        )

    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    return {"id": produto.id, "estoque": produto.estoque, "version": produto.version}


# ═══════════════════════════════════════════════════════════
# DRIVER 4 — SEGURANÇA
# ═══════════════════════════════════════════════════════════

@app.get("/v1/notas/busca")
def buscar_notas_v1(
    cnpj: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    BUG INTENCIONAL: SQL Injection!
    A query é montada com f-string, permitindo injeção:
      GET /v1/notas/busca?cnpj=' OR '1'='1
    """
    if cnpj:
        # VULNERÁVEL: f-string na query SQL
        query = f"SELECT * FROM notas_fiscais WHERE emitente_cnpj = '{cnpj}'"
        result = db.execute(text(query))
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]

    return []


@app.get("/v2/notas/busca")
def buscar_notas_v2(
    cnpj: Optional[str] = Query(None, min_length=14, max_length=14, pattern=r"^\d{14}$"),
    db: Session = Depends(get_db),
):
    """
    VERSÃO CORRIGIDA:
      1. Validação de input via Query params (regex CNPJ)
      2. Query parametrizada (sem f-string)
      3. Usa ORM em vez de raw SQL
    """
    if cnpj:
        notas = (
            db.query(NotaFiscal)
            .filter(NotaFiscal.emitente_cnpj == cnpj)
            .all()
        )
        return [
            {
                "id": n.id,
                "numero": n.numero,
                "emitente_cnpj": n.emitente_cnpj,
                "valor_total": n.valor_total,
                "status": n.status,
            }
            for n in notas
        ]
    return []


# ─── Autenticação simples (para demonstrar o driver) ────

USERS_DB = {
    "admin": "$2b$12$LJ3m4ys3Lg4UebCyIS3GYOaV6BXwsMH1Pu8GMchfGjvLHqZYwVmKy",  # senha: admin123
}


@app.post("/v2/auth/token", response_model=Token)
def login(credentials: LoginRequest):
    """Gera JWT token para endpoints protegidos."""
    from passlib.context import CryptContext
    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    hashed = USERS_DB.get(credentials.username)
    if not hashed or not pwd_ctx.verify(credentials.password, hashed):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = jwt.encode(
        {"sub": credentials.username, "exp": datetime.utcnow() + timedelta(hours=1)},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return Token(access_token=token)


@app.get("/v2/notas/protegido")
def endpoint_protegido(request: Request, db: Session = Depends(get_db)):
    """Endpoint que requer JWT válido no header Authorization."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token não fornecido")

    token = auth.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    return {
        "message": "Acesso autorizado",
        "user": payload.get("sub"),
        "notas_count": db.query(NotaFiscal).count(),
    }


# ═══════════════════════════════════════════════════════════
# CRUD Básico de Produtos (auxiliar)
# ═══════════════════════════════════════════════════════════

@app.get("/v2/produtos", response_model=list[ProdutoResponse])
def listar_produtos(
    limit: int = Query(default=20, le=100, ge=1),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    return db.query(Produto).offset(offset).limit(limit).all()


@app.get("/v2/produtos/{produto_id}", response_model=ProdutoResponse)
def obter_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@app.post("/v2/produtos", response_model=ProdutoResponse, status_code=201)
def criar_produto(produto: ProdutoCreate, db: Session = Depends(get_db)):
    db_produto = Produto(**produto.model_dump())
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto


# ═══════════════════════════════════════════════════════════
# SEED — Dados iniciais
# ═══════════════════════════════════════════════════════════

def seed_database():
    """Popula o banco com dados fictícios para os exercícios."""
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        if db.query(Produto).count() > 0:
            return  # Já populado

        # Criar produtos
        produtos = []
        for i in range(1, 11):
            p = Produto(
                codigo=f"PROD-{i:04d}",
                descricao=f"Produto Fiscal {i}",
                ncm=f"{10000000 + i}",
                preco_unitario=round(50.0 + i * 12.5, 2),
                estoque=100 + i * 10,
            )
            db.add(p)
            produtos.append(p)
        db.flush()

        # Criar 200 notas fiscais (para testar volumetria)
        for i in range(1, 201):
            cnpj_emit = f"{11222333000100 + (i % 5):014d}"
            cnpj_dest = f"{44555666000100 + (i % 8):014d}"
            nf = NotaFiscal(
                numero=f"NF-{i:06d}",
                emitente_cnpj=cnpj_emit,
                destinatario_cnpj=cnpj_dest,
                valor_total=round(100.0 + i * 7.5, 2),
                status=["emitida", "autorizada", "cancelada"][i % 3],
                data_emissao=datetime(2026, 1, 1) + timedelta(hours=i),
            )
            db.add(nf)
            db.flush()

            # Adicionar 2-3 itens por nota
            for j in range(1, (i % 3) + 2):
                prod = produtos[(i + j) % len(produtos)]
                item = ItemNota(
                    nota_id=nf.id,
                    produto_id=prod.id,
                    quantidade=j * 2,
                    valor_unitario=prod.preco_unitario,
                    valor_total=prod.preco_unitario * j * 2,
                )
                db.add(item)

        db.commit()
        logger.info(f"Seed concluído: 10 produtos, 200 notas fiscais")

    except Exception as e:
        db.rollback()
        logger.error(f"Erro no seed: {e}")
    finally:
        db.close()
