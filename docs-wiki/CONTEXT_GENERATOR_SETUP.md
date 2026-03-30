# CONTEXT_GENERATOR_SETUP.md — Build inicial da wiki

> O `context-generator` escaneia o repositório inteiro e gera documentação Markdown
> estruturada de uma só vez, sem precisar de LLM ou API externa.
> Use-o para criar o build inicial da wiki antes de ativar o pipeline incremental.

---

## O que é o context-generator

Repositório: https://github.com/ContextLab/context-generator

Ferramenta que:
1. Escaneia arquivos PHP, Vue e JS do projeto
2. Extrai classes, métodos, constantes, relacionamentos
3. Gera arquivos `.md` estruturados prontos para LaRecipe
4. Entende estrutura de namespaces Laravel e componentes Vue

---

## Setup — passo a passo

### 1. Instalar o context-generator

```bash
# Clonar em uma pasta fora do projeto SafetyDocs
git clone https://github.com/ContextLab/context-generator.git ~/tools/context-generator
cd ~/tools/context-generator
pip install -r requirements.txt
```

### 2. Criar o arquivo de configuração

Salve como `docs-wiki/context-generator.yml` na raiz do SafetyDocs:

```yaml
project:
  name: "SafetyDocs V3"
  root: "./"                          # raiz do projeto
  language: php                       # backend principal
  framework: laravel

output:
  path: "resources/docs/1.0"          # destino LaRecipe
  format: markdown
  overwrite: false                    # não sobrescrever edições manuais

scan:
  include:
    - "app/Http/Controllers/**/*.php"
    - "app/Models/Tenant/**/*.php"
    - "app/Models/Padrao/**/*.php"
    - "app/Jobs/Tenant/**/*.php"
    - "app/Traits/**/*.php"
    - "resources/js/pages/**/*.vue"
    - "resources/js/service/tenant/**/*.js"
    - "resources/js/components/**/*.vue"
    - "database/migrations/**/*.php"
  exclude:
    - "vendor/**"
    - "node_modules/**"
    - "**/*.test.*"
    - "**/*.spec.*"

# Mapeamento de diretório de código -> seção da wiki
sections:
  - source: "app/Http/Controllers/Permits"
    target: "permits/controllers"
    label: "Permits — Controllers"
  - source: "app/Http/Controllers/Shopping"
    target: "shopping/controllers"
    label: "Shopping — Controllers"
  - source: "app/Http/Controllers/Contrato"
    target: "contrato/controllers"
    label: "Contratos — Controllers"
  - source: "app/Http/Controllers/Ged"
    target: "ged/controllers"
    label: "GED — Controllers"
  - source: "app/Http/Controllers/Imobiliario"
    target: "imobiliario/controllers"
    label: "Imobiliário — Controllers"
  - source: "app/Http/Controllers/Engenharia"
    target: "engenharia/controllers"
    label: "Engenharia — Controllers"
  - source: "app/Http/Controllers/Fornecedor"
    target: "fornecedor/controllers"
    label: "Fornecedor — Controllers"
  - source: "app/Http/Controllers/Prospeccao"
    target: "prospeccao/controllers"
    label: "Prospecção — Controllers"
  - source: "app/Models/Tenant"
    target: "models"
    label: "Models Tenant"
  - source: "app/Traits"
    target: "compartilhado/traits"
    label: "Traits compartilhadas"
  - source: "resources/js/pages"
    target: "frontend/pages"
    label: "Frontend — Pages Vue"
  - source: "resources/js/service/tenant"
    target: "frontend/services"
    label: "Frontend — Services"
  - source: "database/migrations"
    target: "database"
    label: "Migrations"

# Opções de enriquecimento com LLM (Fase 2)
llm:
  enabled: false          # ativar após build inicial
  provider: gemini        # usar Gemini free tier
  model: gemini-1.5-flash
  # api_key: via GEMINI_API_KEY env var
  prompt_template: "docs-wiki/dify-prompt.md"
```

### 3. Rodar o build inicial

```bash
cd /caminho/para/safetydocs-v3

python3 ~/tools/context-generator/generate.py \
  --config docs-wiki/context-generator.yml \
  --verbose
```

Saída esperada:
```
Scanning: app/Http/Controllers/Permits/ ... 12 files
Scanning: app/Models/Tenant/ ............. 47 files
Scanning: resources/js/pages/ ............ 89 files
...
Generated: resources/docs/1.0/permits/controllers/DocumentoCtrl.md
Generated: resources/docs/1.0/permits/controllers/ArquivoCtrl.md
...
Total: 187 markdown files generated
```

### 4. Enriquecer com Gemini (opcional — após build base)

Ativa o LLM no config e roda novamente para adicionar descrições, exemplos e contexto:

```bash
export GEMINI_API_KEY="sua-chave-aqui"

python3 ~/tools/context-generator/generate.py \
  --config docs-wiki/context-generator.yml \
  --enrich-only \        # só enriquece, não regenera estrutura
  --rate-limit 10        # 10 req/min para respeitar free tier
```

### 5. Commitar os docs gerados

```bash
git add resources/docs/
git commit -m "[sdv3-wiki] Build inicial da wiki via context-generator"
git push
```

A partir daqui o **pipeline incremental** (Dify + Gemini) assume as atualizações automáticas por push.

---

## Alternativa: repomix para gerar contexto único

Se o context-generator não tiver suporte completo para o SafetyDocs,
use o `repomix` para gerar um arquivo de contexto gigante e alimentar o Gemini:

```bash
# Instalar
npm install -g repomix

# Gerar contexto de todo o projeto
repomix \
  --include "app/Http/Controllers/**,app/Models/Tenant/**,resources/js/**" \
  --exclude "vendor,node_modules,*.min.js" \
  --output docs-wiki/project-context.md

# O arquivo gerado pode ser enviado ao Gemini 1.5 Pro (1M tokens)
# com o prompt de docs-wiki/dify-prompt.md para gerar a wiki completa
```

---

## Dica: índice LaRecipe

Após o build, edite `resources/docs/1.0/index.md` para criar o índice:

```markdown
---
title: SafetyDocs V3 — Documentação
---

## Módulos

- [Permits](/docs/1.0/permits/controllers/DocumentoCtrl)
- [Shopping](/docs/1.0/shopping/controllers/DocumentoCtrl)
- [Contratos](/docs/1.0/contrato/controllers/DocumentoCtrl)
- [GED](/docs/1.0/ged/controllers/DiretorioCtrl)
- [Imobiliário](/docs/1.0/imobiliario/controllers/ContratoCtrl)
- [Engenharia](/docs/1.0/engenharia/controllers/EtapaCtrl)
- [Fornecedor](/docs/1.0/fornecedor/controllers/FornecedorCtrl)
- [Prospecção](/docs/1.0/prospeccao/controllers/ProjetoCtrl)

## Compartilhado

- [Traits](/docs/1.0/compartilhado/traits)
- [Multi-Tenant](/docs/1.0/arquitetura/multi-tenant)
- [Migrations](/docs/1.0/database)
```
