# CLAUDE.md — Sistema de Wiki (docs-wiki/)

> Lido ao trabalhar em qualquer arquivo desta pasta ou em `resources/docs/`.
> NUNCA editar `resources/docs/` manualmente — gerido pelo pipeline.

---

## Estratégia em duas fases

### Fase 1 — Build inicial com `context-generator`

Roda uma única vez para escanear todo o repositório e gerar os Markdowns base.
Ver `docs-wiki/CONTEXT_GENERATOR_SETUP.md`.

### Fase 2 — Incremento automático por push

GitHub Actions → diff → Dify webhook → Gemini → commit em `resources/docs/`
Ver `.github/workflows/wiki-update.yml` e `dify-prompt.md`.

---

## Estrutura dos docs gerados (LaRecipe)

```
resources/docs/1.0/
├── index.md
├── arquitetura/
│   ├── stack.md
│   ├── multi-tenant.md
│   └── modulos.md
├── permits/
│   ├── controllers/
│   ├── models/
│   └── frontend/
├── shopping/      ← idem
├── contrato/      ← idem
├── ged/           ← idem
├── imobiliario/   ← idem
├── engenharia/    ← idem
├── fornecedor/    ← idem
├── prospeccao/    ← idem
└── compartilhado/
    ├── traits.md
    ├── migrations.md
    └── permissoes.md
```
