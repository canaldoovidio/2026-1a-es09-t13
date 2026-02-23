# ASIS TaxTech Lab — Business Drivers como Código

Lab prático do módulo ES09 (Inteli, Turma T13) para exercitar os 4 Business Drivers do projeto ASIS TaxTech.

## Pré-requisitos

- Docker e Docker Compose instalados
- Python 3.11+ (para rodar testes localmente)
- JMeter (opcional, para testes de carga)

## Como Rodar

```bash
# 1. Subir a aplicação + banco de dados
docker compose up --build

# 2. Acessar a API
# http://localhost:8000
# http://localhost:8000/docs  (Swagger UI)

# 3. Rodar os testes (em outro terminal)
pip install -r requirements.txt
pytest tests/ -v
```

## Estrutura do Lab

```
asis-bd-lab/
├── app/
│   ├── main.py        ← API com endpoints v1 (bugados) e v2 (corrigidos)
│   ├── models.py      ← Modelos: Produto, NotaFiscal, ItemNota
│   ├── schemas.py     ← Validação Pydantic
│   └── database.py    ← Conexão PostgreSQL
├── tests/
│   ├── test_01_volumetria.py      ← Driver 1: paginação, N+1
│   ├── test_02_rastreabilidade.py ← Driver 2: correlation ID, logging
│   ├── test_03_concorrencia.py    ← Driver 3: race condition, locking
│   └── test_04_seguranca.py       ← Driver 4: SQL injection, auth
└── jmeter/
    └── load_test.jmx  ← Plano JMeter para teste de carga
```

## Os 4 Business Drivers

| Driver | Bug (v1) | Fix (v2) | Teste |
|--------|----------|----------|-------|
| **Volumetria** | Retorna todos os registros sem paginação | Paginação com limit/offset + eager loading | `test_01_volumetria.py` |
| **Rastreabilidade** | Logs com `print()`, sem correlation ID | Middleware com X-Correlation-ID + structured logging | `test_02_rastreabilidade.py` |
| **Acesso Simultâneo** | Race condition no update de estoque | Optimistic locking com coluna `version` | `test_03_concorrencia.py` |
| **Segurança** | SQL Injection via f-string | Query parametrizada + validação Pydantic + JWT | `test_04_seguranca.py` |

## Endpoints

### Versão v1 (com bugs intencionais)
- `GET /v1/notas` — Lista notas SEM paginação
- `GET /v1/notas/{id}` — Busca nota SEM log estruturado
- `PUT /v1/produtos/{id}/estoque` — Atualiza estoque SEM lock
- `GET /v1/notas/busca?cnpj=` — Busca notas COM SQL Injection

### Versão v2 (corrigida)
- `GET /v2/notas?limit=20&offset=0` — Lista notas COM paginação
- `GET /v2/notas/{id}` — Busca nota COM correlation ID
- `PUT /v2/produtos/{id}/estoque?version=` — Atualiza COM optimistic locking
- `GET /v2/notas/busca?cnpj=` — Busca COM validação e query segura
- `POST /v2/auth/token` — Autenticação JWT
- `GET /v2/notas/protegido` — Endpoint que requer JWT

## Credenciais de Teste

- **Usuário:** admin
- **Senha:** admin123
