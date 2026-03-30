# WIKI_BUILD_GUIDE.md — SafetyDocs V3 + Context Engine v4

> Guia completo para gerar a wiki inicial via Context Engine e depois
> incrementar automaticamente com Gemini (free tier).

---

## Arquitetura da solução

```
┌─────────────────────────────────────────────────────────────┐
│  FASE 1 — Build inicial (roda UMA vez)                      │
│                                                             │
│  sdv3/ (código Laravel+Vue)                                 │
│    ↓ montado como volume                                    │
│  context-engine/ (Docker)                                   │
│    ├── indexer-worker  → escaneia e indexa tudo no Qdrant   │
│    └── indexer-api     → serve endpoints REST               │
│          ↓                                                  │
│  wiki_builder.py  →  GET /wiki/flow por módulo/URL          │
│          ↓                                                  │
│  resources/docs/1.0/**/*.md  (LaRecipe)                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  FASE 2 — Incremento automático (a cada push)               │
│                                                             │
│  git push → GitHub Actions                                  │
│    ↓                                                        │
│  Opção A: context-engine /update → diff → Gemini API        │
│  Opção B: diff direto → Gemini API (sem context-engine)     │
│    ↓                                                        │
│  resources/docs/1.0/**/*.md  atualizado                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Pré-requisitos

```bash
# Sistema
docker >= 24.0
docker compose >= 2.24
python >= 3.10 (para rodar os scripts fora do container)

# GPU (opcional mas recomendado para o build)
# NVIDIA com CUDA 12.1+ → build ~5x mais rápido
# Sem GPU → usa CPU, build demora mais (20-40 min para SDV3)
```

---

## Parte 1 — Setup do Context Engine

### 1.1 Clonar e configurar

```bash
# Clone o context-engine (já tem seu código em context-engine/)
cd ~/projects  # ou onde preferir, FORA do SDV3

# Configure o .env (já existe um exemplo)
cd context-engine/
cp .env.example .env
```

Edite o `.env` com os valores corretos para o SDV3:

```bash
# .env — valores para SafetyDocs V3
PROJECT_PATH=/home/iurru/projects/SafetyDocs/safetydocs/sdv3

API_PORT=8765
COLLECTION_NAME=code_context
COLLECTION_FUNCTIONS=code_functions

# Modelo de embedding — all-MiniLM-L6-v2 é rápido e funciona bem
LOCAL_MODEL_NAME=all-MiniLM-L6-v2
EMBEDDING_PROVIDER=local

# Modelo para funções (3 vetores) — melhor recall
FUNCTIONS_EMBEDDING_MODEL=BAAI/bge-base-en-v1.5
EMBEDDING_BATCH_SIZE=256           # GPU. Use 32 sem GPU
FUNCTIONS_EMBEDDING_BATCH_SIZE=32  # reduz se der CUDA OOM

# PHPStan
PHPSTAN_LEVEL=6
PHPSTAN_MEMORY=2G

# ESLint
ESLINT_ENABLED=true

# Banco do SDV3 (opcional mas melhora muito o schema das tabelas)
DB_DEFAULT_HOST=host.docker.internal
DB_DEFAULT_PORT=3306
DB_DEFAULT_DATABASE=sdv3_teste
DB_DEFAULT_USERNAME=root
DB_DEFAULT_PASSWORD=root

# Tenants (adicione seus tenants reais)
DB_TENANTS=[{"name":"sdv3_teste","host":"host.docker.internal","port":3306,"database":"sdv3_teste","username":"root","password":"root"}]
```

### 1.2 Subir os containers

```bash
cd context-engine/

# Com GPU NVIDIA (recomendado)
docker compose up -d

# Sem GPU — comente o bloco 'deploy.resources' no docker-compose.yml antes
docker compose up -d

# Verificar se subiu ok
docker compose ps
curl http://localhost:8765/health
```

Saída esperada do `/health`:
```json
{
  "status": "ok",
  "qdrant": "connected",
  "project_path": "/project",
  "project_exists": true,
  "phpstan_available": true,
  "eslint_available": true
}
```

---

## Parte 2 — Build inicial da wiki

### 2.1 Indexar o projeto (etapa pesada — roda uma vez)

```bash
# Dentro do container worker — indexa TUDO no Qdrant
docker exec context-indexer-worker \
  python src/indexer/updater.py --mode build
```

Acompanhe os logs:
```bash
docker logs context-indexer-worker -f
```

Duração esperada para o SDV3:
- Com GPU: ~5-10 min
- Sem GPU: ~25-40 min

Verifique ao terminar:
```bash
curl http://localhost:8765/stats
# Deve retornar vectors_count > 10000
```

### 2.2 Gerar os arquivos Markdown da wiki

Com o Qdrant indexado, rode o script `wiki_builder.py` que consulta
`/wiki/flow` para cada URL/módulo do SDV3 e gera os `.md`:

```bash
cd /home/iurru/projects/SafetyDocs/safetydocs/sdv3

pip install requests  # se não tiver

python docs-wiki/scripts/wiki_builder.py \
  --api http://localhost:8765 \
  --output resources/docs/1.0 \
  --tenant sdv3_teste
```

Isso gera todos os arquivos em `resources/docs/1.0/`.

### 2.3 Commitar os docs gerados

```bash
git add resources/docs/
git commit -m "[sdv3-wiki] Build inicial da wiki via context-engine"
git push
```

---

## Parte 3 — Incremento com Gemini (free tier)

A cada push, o GitHub Actions detecta os arquivos alterados,
extrai o diff e chama a Gemini API para atualizar os docs afetados.

### 3.1 Obter a Gemini API Key (gratuita)

1. Acesse https://aistudio.google.com
2. Crie uma API Key
3. Adicione no GitHub Secrets como `GEMINI_API_KEY`

### 3.2 Configurar o workflow

O arquivo `.github/workflows/wiki-update.yml` já está configurado.
Apenas adicione os secrets no GitHub:

| Secret         | Valor                        |
|----------------|------------------------------|
| `GEMINI_API_KEY` | Chave do Google AI Studio   |
| `GH_TOKEN`     | GitHub PAT com `contents:write` |

### 3.3 Testar o incremento manualmente

```bash
# Simula o que o GitHub Actions faz
python docs-wiki/scripts/gemini_incrementer.py \
  --file app/Http/Controllers/Permits/DocumentoCtrl.php \
  --api http://localhost:8765 \
  --output resources/docs/1.0
```

---

## Troubleshooting

```bash
# Ver logs do worker
docker logs context-indexer-worker -f

# Diagnosticar problemas com rotas
docker exec -it context-indexer-worker \
  python /app/src/indexer/diagnose.py

# Inspecionar o Qdrant
docker exec -it context-indexer-api \
  python /app/src/indexer/qdrant_inspect.py

# Rebuild do zero (limpa o Qdrant)
docker compose down -v && docker compose up -d
docker exec context-indexer-worker \
  python src/indexer/updater.py --mode build

# Testar um flow específico
curl -X POST http://localhost:8765/wiki/flow \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/sdv3_teste/permits/documentos",
    "search_query": "listagem de documentos"
  }'
```
