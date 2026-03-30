#!/usr/bin/env python3
"""
gemini_incrementer.py — SafetyDocs V3 (wiki para usuário não técnico)
Prompt adaptado para gerar páginas de wiki em linguagem humana,
no mesmo formato do flow_explainer.py reescrito.
"""
from __future__ import annotations
import argparse, json, os, re, subprocess, sys, time
from datetime import date as _date
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("pip install requests")
    sys.exit(1)

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# ── Mapeamento file → seção + nome amigável ───────────────────────────────────
FILE_MAP = [
    ("Controllers/Permits",     "permits/controllers",     "Funcionalidade do módulo Permits"),
    ("Controllers/Shopping",    "shopping/controllers",    "Funcionalidade do módulo Shopping"),
    ("Controllers/Contrato",    "contrato/controllers",    "Funcionalidade do módulo Contratos"),
    ("Controllers/Ged",         "ged/controllers",         "Funcionalidade do módulo GED"),
    ("Controllers/Imobiliario", "imobiliario/controllers", "Funcionalidade do módulo Imobiliário"),
    ("Controllers/Engenharia",  "engenharia/controllers",  "Funcionalidade do módulo Engenharia"),
    ("Controllers/Fornecedor",  "fornecedor/controllers",  "Funcionalidade do módulo Fornecedor"),
    ("Controllers/Prospeccao",  "prospeccao/controllers",  "Funcionalidade do módulo Prospecção"),
    ("Models/Tenant/Permits",   "permits/modelos",         "Dados do módulo Permits"),
    ("Models/Tenant/Shopping",  "shopping/modelos",        "Dados do módulo Shopping"),
    ("Models/Tenant/Contrato",  "contrato/modelos",        "Dados do módulo Contratos"),
    ("Models/Tenant/Ged",       "ged/modelos",             "Dados do módulo GED"),
    ("Models/Tenant/Imobiliario","imobiliario/modelos",    "Dados do módulo Imobiliário"),
    ("Models/Tenant/Engenharia","engenharia/modelos",      "Dados do módulo Engenharia"),
    ("Models/Tenant/Fornecedor","fornecedor/modelos",      "Dados do módulo Fornecedor"),
    ("Models/Tenant/Prospeccao","prospeccao/modelos",      "Dados do módulo Prospecção"),
    ("Jobs/Tenant",             "jobs",                    "Processo automático do sistema"),
    ("pages/permits",           "permits/telas",           "Tela do módulo Permits"),
    ("pages/shopping",          "shopping/telas",          "Tela do módulo Shopping"),
    ("pages/contrato",          "contrato/telas",          "Tela do módulo Contratos"),
    ("pages/ged",               "ged/telas",               "Tela do módulo GED"),
    ("pages/imobiliario",       "imobiliario/telas",       "Tela do módulo Imobiliário"),
    ("pages/engenharia",        "engenharia/telas",        "Tela do módulo Engenharia"),
    ("pages/fornecedor",        "fornecedor/telas",        "Tela do módulo Fornecedor"),
    ("pages/prospeccao",        "prospeccao/telas",        "Tela do módulo Prospecção"),
    ("database/migrations",     "banco-de-dados",          "Estrutura de dados"),
]

SYSTEM_PROMPT = """Você é um redator de documentação do sistema SafetyDocs V3.

SEU PÚBLICO: colaboradores de suporte e comercial SEM conhecimento técnico.
Eles precisam entender O QUE a funcionalidade faz, COMO usar e O QUE esperar.

REGRAS ABSOLUTAS:
1. Responda APENAS com o Markdown — sem introdução, sem explicação extra.
2. Se a mudança não afeta o comportamento visível ao usuário, responda: SKIP
3. NUNCA use: nomes de classes PHP, SQL, rotas técnicas, namespaces, termos de código.
4. SEMPRE use: português brasileiro claro, exemplos práticos, linguagem do negócio.
5. Bullets e tabelas são bem-vindos — evite parágrafos longos.

TRADUÇÕES OBRIGATÓRIAS (nunca use a versão técnica):
- DocumentoCtrl / DocumentoService → "funcionalidade de documentos"
- per_documentos / con_documentos → "documentos" (sem prefixo)
- dtcriacao / dtalteracao → "data de criação / data de alteração"
- ativo = 0 → "registro inativo / excluído"
- aprovacao_id = 1 → "Pendente", = 2 → "Aprovado", = 3 → "Reprovado"
- status_id = 3 → "Vigente", = 4 → "Vencido", = 7 → "Em Revisão"
- FilterTrait / OrderTrait → não mencionar
- hasMany / belongsTo → "vinculado a" / "possui vários"
"""

DOC_TEMPLATE = """
## Template de saída obrigatório para a wiki:

```markdown
---
title: [Nome amigável da funcionalidade — ex: "Aprovação de documentos"]
---

## O que é esta funcionalidade?

[2-3 frases explicando o que o usuário pode fazer nesta tela/funcionalidade,
em linguagem de negócio. Ex: "Esta tela permite que o usuário aprove ou reprove
documentos enviados pelos fornecedores."]

## Para que serve?

- [Benefício 1 em linguagem de negócio]
- [Benefício 2]
- [Benefício 3]

## O que você pode fazer aqui?

| Ação | O que acontece |
|------|----------------|
| **[Ação 1]** | [Resultado em português claro] |
| **[Ação 2]** | [Resultado em português claro] |

## Campos disponíveis

[Tabela com os campos que o usuário vê na tela, em português, sem nomes técnicos.
Omitir campos puramente internos como id, dtcriacao, usuario_criacao_id.]

| Campo | O que é | Obrigatório |
|-------|---------|-------------|
| Nome do campo em pt | Explicação do que o usuário preenche | Sim / Não |

## Status possíveis

[Apenas se a funcionalidade tem status. Use emojis: ✅ ativo/ok, ⏳ pendente, ❌ problema/vencido]

- ✅ **Vigente** — Documento válido e ativo
- ⏳ **Pendente de aprovação** — Aguardando revisão
- ❌ **Vencido** — Prazo expirado, precisa de renovação

## Notificações automáticas

[Apenas se há e-mails ou alertas automáticos envolvidos.]

- O responsável recebe um e-mail quando [condição]

## Perguntas frequentes

**[Pergunta que um usuário de suporte faria]**
[Resposta direta e prática]

**[Pergunta 2]**
[Resposta 2]

---

<details>
<summary>🔧 Para o time de suporte técnico</summary>

[Aqui sim pode mencionar termos técnicos — nome do controller, tabela, arquivo Vue.
Esta seção é colapsada e invisível para o usuário final.]

</details>
```

Data de hoje: {date}
Se já existe documentação, mantenha-a e adicione apenas o que mudou na seção relevante.
Adicione a data de hoje no histórico dentro da seção técnica colapsada.
"""


def resolve_section(fp: str):
    for pattern, section, label in FILE_MAP:
        if pattern in fp:
            return section, label
    return "misc", "Funcionalidade do sistema"


def file_to_doc_path(fp: str, section: str) -> str:
    base = Path(fp).stem
    slug = re.sub(r"([A-Z])", r"-\1", base).lower().lstrip("-")
    return f"{section}/{slug}"


def get_changed_files(root: str, diff_range: str) -> list[str]:
    try:
        r = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACMRT", diff_range],
            cwd=root, capture_output=True, text=True, timeout=30,
        )
        return [
            f.strip() for f in r.stdout.splitlines()
            if f.strip()
            and Path(f.strip()).suffix.lower() in {".php", ".vue", ".js", ".ts"}
            and not any(s in f for s in ["vendor/", "node_modules/", ".test.", ".spec.", ".min."])
        ]
    except Exception as e:
        print(f"❌ git diff: {e}")
        return []


def get_diff(root: str, fp: str, diff_range: str) -> str:
    try:
        r = subprocess.run(
            ["git", "diff", diff_range, "--", fp],
            cwd=root, capture_output=True, text=True, timeout=15,
        )
        diff = r.stdout.strip()
        if not diff:
            full = (Path(root) / fp)
            if full.exists():
                return full.read_text(encoding="utf-8", errors="ignore")[:5000]
        return diff[:5000]
    except Exception:
        return ""


def call_gemini(api_key: str, fp: str, label: str, diff: str, existing: str, today: str) -> Optional[str]:
    prompt = (
        SYSTEM_PROMPT
        + DOC_TEMPLATE.replace("{date}", today)
        + f"\n\n## Arquivo alterado\nCaminho: `{fp}`\nTipo: {label}\n\n"
        + f"## Código / Diff\n```\n{diff[:4000]}\n```\n\n"
        + f"## Documentação existente\n```markdown\n{existing or '(nenhuma)'}\n```"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2500},
    }
    try:
        r = requests.post(f"{GEMINI_URL}?key={api_key}", json=payload, timeout=60)
        r.raise_for_status()
        parts = r.json().get("candidates", [{}])[0].get("content", {}).get("parts", [])
        text = (parts[0].get("text", "") if parts else "").strip()
        if text == "SKIP":
            return None
        if text.startswith("```markdown"):
            text = text[len("```markdown"):].strip()
        if text.endswith("```"):
            text = text[:-3].strip()
        return text
    except requests.HTTPError as e:
        if e.response.status_code == 429:
            print("  ⚠️  Rate limit — aguardando 60s...")
            time.sleep(60)
            return call_gemini(api_key, fp, label, diff, existing, today)
        print(f"  ❌ Gemini HTTP {e.response.status_code}")
        return None
    except Exception as e:
        print(f"  ❌ Gemini: {e}")
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file",         default=None)
    parser.add_argument("--diff",         default=None)
    parser.add_argument("--output",       default="resources/docs/1.0")
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY não definida")
        sys.exit(1)

    today = _date.today().isoformat()
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    files = [args.file] if args.file else (get_changed_files(args.project_root, args.diff) if args.diff else [])
    if not files:
        print("ℹ️  Nenhum arquivo para processar.")
        sys.exit(0)

    print(f"📄 {len(files)} arquivo(s)\n")
    ok = skip = err = 0

    for fp in files:
        print(f"→ {fp}")
        section, label = resolve_section(fp)
        doc_path = file_to_doc_path(fp, section)
        doc_file = output_dir / f"{doc_path}.md"
        existing = doc_file.read_text(encoding="utf-8") if doc_file.exists() else ""

        diff = get_diff(args.project_root, fp, args.diff) if args.diff else \
               (Path(args.project_root) / fp).read_text(encoding="utf-8", errors="ignore")[:5000]

        if not diff:
            print("  ⚠️  Sem conteúdo")
            skip += 1
            continue

        print(f"  🤖 Gerando ({label})...")
        content = call_gemini(api_key, fp, label, diff, existing, today)

        if content is None:
            print("  ⏭️  SKIP")
            skip += 1
        else:
            title = Path(fp).stem.replace("Ctrl", "").replace("Service", "")
            if not content.startswith("---"):
                content = f"---\ntitle: {title}\n---\n\n{content}"
            doc_file.parent.mkdir(parents=True, exist_ok=True)
            doc_file.write_text(content, encoding="utf-8")
            print(f"  ✅ {doc_file}")
            ok += 1

        time.sleep(4)  # rate limit Gemini free: 15 req/min

    print(f"\n✅ {ok}  ⏭️  {skip}  ❌ {err}")


if __name__ == "__main__":
    main()
