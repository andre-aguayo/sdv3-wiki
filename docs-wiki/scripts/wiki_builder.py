#!/usr/bin/env python3
"""
wiki_builder.py — SafetyDocs V3 (central de ajuda para usuário final)
"""
from __future__ import annotations
import argparse, sys, time
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("pip install requests"); sys.exit(1)

SDV3_PAGES = [
    # (url_template, query_humana, doc_path, titulo)
    ("/{t}/permits/documentos",           "como visualizar e gerenciar documentos de licença ambiental",    "permits/documentos/visao-geral",             "Permits — Documentos de licença"),
    ("/{t}/permits/documentos/aprovacao", "como aprovar ou reprovar um documento de licença ambiental",     "permits/documentos/aprovacao",               "Permits — Aprovação de documentos"),
    ("/{t}/permits/documentos/upload",    "como enviar o arquivo de uma licença ambiental",                 "permits/documentos/envio-de-arquivo",        "Permits — Envio de arquivos"),
    ("/{t}/permits/unidades",             "como gerenciar unidades e sites no módulo de licenças",          "permits/unidades",                           "Permits — Unidades e Sites"),
    ("/{t}/permits/frentes",              "o que são frentes de trabalho no módulo permits",                "permits/frentes",                            "Permits — Frentes de trabalho"),
    ("/{t}/shopping/documentos",          "como gerenciar documentos de lojas no shopping center",          "shopping/documentos/visao-geral",            "Shopping — Documentos de lojas"),
    ("/{t}/shopping/documentos/aprovacao","como aprovar documentos enviados pelas lojas",                   "shopping/documentos/aprovacao",              "Shopping — Aprovação de documentos"),
    ("/{t}/shopping/lojas",               "como cadastrar e gerenciar lojas de um shopping",                "shopping/lojas",                             "Shopping — Lojas"),
    ("/{t}/shopping/condominios",         "como cadastrar shoppings e condomínios no sistema",              "shopping/condominios",                       "Shopping — Shoppings e Condomínios"),
    ("/{t}/shopping/lojistas",            "como funciona o acesso do lojista ao portal de documentos",      "shopping/lojistas",                          "Shopping — Acesso do lojista"),
    ("/{t}/contrato/documentos",          "como visualizar e gerenciar contratos no sistema",               "contrato/contratos/visao-geral",             "Contratos — Visão geral"),
    ("/{t}/contrato/documentos/aprovacao","como aprovar ou reprovar um contrato",                           "contrato/contratos/aprovacao",               "Contratos — Aprovação de contratos"),
    ("/{t}/contrato/tarefas",             "como gerenciar tarefas e obrigações de um contrato",             "contrato/tarefas",                           "Contratos — Tarefas e obrigações"),
    ("/{t}/contrato/indices",             "como funcionam os índices de reajuste dos contratos",            "contrato/indices",                           "Contratos — Índices de reajuste"),
    ("/{t}/ged/diretorios",               "como navegar na árvore de documentos do GED",                   "ged/diretorios",                             "GED — Pastas e diretórios"),
    ("/{t}/ged/diretorios/documentos",    "como enviar e gerenciar arquivos no GED",                        "ged/documentos",                             "GED — Arquivos e documentos"),
    ("/{t}/ged/tarefas",                  "como criar e acompanhar tarefas vinculadas ao GED",              "ged/tarefas",                                "GED — Tarefas"),
    ("/{t}/imobiliario/contratos",        "como visualizar e gerenciar contratos de locação imobiliária",   "imobiliario/contratos/visao-geral",          "Imobiliário — Contratos de locação"),
    ("/{t}/imobiliario/negociacoes",      "como registrar negociações de contratos imobiliários",           "imobiliario/negociacoes",                    "Imobiliário — Negociações"),
    ("/{t}/imobiliario/despesas",         "como registrar despesas de aluguel e taxas de imóveis",          "imobiliario/despesas",                       "Imobiliário — Despesas"),
    ("/{t}/engenharia/unidades",          "como cadastrar e acompanhar obras e empreendimentos",            "engenharia/unidades",                        "Engenharia — Obras e unidades"),
    ("/{t}/engenharia/etapas",            "como gerenciar etapas de obra por disciplina",                   "engenharia/etapas",                          "Engenharia — Etapas de obra"),
    ("/{t}/engenharia/revisoes",          "como enviar e aprovar revisões de etapas de obra",               "engenharia/revisoes",                        "Engenharia — Revisões"),
    ("/{t}/fornecedor/fornecedores",      "como cadastrar e gerenciar fornecedores e prestadores",          "fornecedor/fornecedores",                    "Fornecedor — Cadastro"),
    ("/{t}/fornecedor/documentos",        "como gerenciar documentos de fornecedores",                      "fornecedor/documentos/visao-geral",          "Fornecedor — Documentos"),
    ("/{t}/fornecedor/documentos/aprovacao","como aprovar documentos enviados por fornecedores",            "fornecedor/documentos/aprovacao",            "Fornecedor — Aprovação"),
    ("/{t}/fornecedor/chamados",          "como abrir e acompanhar chamados de fornecedores",               "fornecedor/chamados",                        "Fornecedor — Chamados"),
    ("/{t}/fornecedor/atividades",        "como registrar e acompanhar atividades de fornecedores",         "fornecedor/atividades",                      "Fornecedor — Atividades"),
    ("/{t}/prospeccao/projetos",          "como criar e gerenciar projetos de prospecção de imóveis",       "prospeccao/projetos",                        "Prospecção — Projetos"),
    ("/{t}/prospeccao/imoveis",           "como pesquisar e registrar imóveis em prospecção",               "prospeccao/imoveis",                         "Prospecção — Imóveis"),
    ("/{t}/prospeccao/tarefas",           "como gerenciar tarefas de imóveis prospectados",                 "prospeccao/tarefas",                         "Prospecção — Tarefas"),
]

SDV3_CONCEPTS = [
    ("aprovacao",   "como funciona o processo de aprovação de documentos no SafetyDocs",  "guia/aprovacao",             "Guia — Aprovação de documentos"),
    ("vencimento",  "o que fazer quando um documento vence no SafetyDocs",                "guia/documentos-vencidos",   "Guia — Documentos vencidos"),
    ("upload",      "como enviar e atualizar arquivos no SafetyDocs",                      "guia/envio-de-arquivos",     "Guia — Envio de arquivos"),
    ("notificacao", "quando e quem recebe notificações automáticas no SafetyDocs",         "guia/notificacoes",          "Guia — Notificações e e-mails"),
    ("permissao",   "como funcionam os perfis de acesso no SafetyDocs",                   "guia/perfis-de-acesso",      "Guia — Perfis de acesso"),
    ("relatorio",   "como exportar relatórios e planilhas no SafetyDocs",                 "guia/exportacao-relatorios", "Guia — Relatórios e exportações"),
]

INDEX_CONTENT = """---
title: SafetyDocs V3 — Central de Ajuda
---

## Bem-vindo à Central de Ajuda do SafetyDocs

Aqui você encontra respostas sobre todas as telas e funcionalidades do sistema.
Use o menu lateral ou a busca para encontrar o que precisa.

## 📘 Guias gerais

- [Como funciona a aprovação de documentos](/docs/1.0/guia/aprovacao)
- [O que fazer quando um documento vence](/docs/1.0/guia/documentos-vencidos)
- [Como enviar arquivos](/docs/1.0/guia/envio-de-arquivos)
- [Notificações e e-mails automáticos](/docs/1.0/guia/notificacoes)
- [Perfis de acesso e permissões](/docs/1.0/guia/perfis-de-acesso)
- [Como exportar relatórios](/docs/1.0/guia/exportacao-relatorios)

## 📂 Módulos do sistema

### Permits — Licenças Ambientais
- [Documentos de licença](/docs/1.0/permits/documentos/visao-geral)
- [Aprovação de documentos](/docs/1.0/permits/documentos/aprovacao)
- [Envio de arquivos](/docs/1.0/permits/documentos/envio-de-arquivo)
- [Unidades e Sites](/docs/1.0/permits/unidades)
- [Frentes de trabalho](/docs/1.0/permits/frentes)

### Shopping — Documentos de Lojas
- [Documentos de lojas](/docs/1.0/shopping/documentos/visao-geral)
- [Aprovação de documentos](/docs/1.0/shopping/documentos/aprovacao)
- [Lojas](/docs/1.0/shopping/lojas)
- [Shoppings e Condomínios](/docs/1.0/shopping/condominios)
- [Acesso do lojista](/docs/1.0/shopping/lojistas)

### Contratos
- [Visão geral](/docs/1.0/contrato/contratos/visao-geral)
- [Aprovação de contratos](/docs/1.0/contrato/contratos/aprovacao)
- [Tarefas e obrigações](/docs/1.0/contrato/tarefas)
- [Índices de reajuste](/docs/1.0/contrato/indices)

### GED — Gestão de Documentos
- [Pastas e diretórios](/docs/1.0/ged/diretorios)
- [Arquivos e documentos](/docs/1.0/ged/documentos)
- [Tarefas](/docs/1.0/ged/tarefas)

### Imobiliário
- [Contratos de locação](/docs/1.0/imobiliario/contratos/visao-geral)
- [Negociações](/docs/1.0/imobiliario/negociacoes)
- [Despesas](/docs/1.0/imobiliario/despesas)

### Engenharia
- [Obras e unidades](/docs/1.0/engenharia/unidades)
- [Etapas de obra](/docs/1.0/engenharia/etapas)
- [Revisões e aprovações](/docs/1.0/engenharia/revisoes)

### Fornecedor
- [Cadastro de fornecedores](/docs/1.0/fornecedor/fornecedores)
- [Documentos](/docs/1.0/fornecedor/documentos/visao-geral)
- [Aprovação de documentos](/docs/1.0/fornecedor/documentos/aprovacao)
- [Chamados](/docs/1.0/fornecedor/chamados)
- [Atividades](/docs/1.0/fornecedor/atividades)

### Prospecção
- [Projetos](/docs/1.0/prospeccao/projetos)
- [Imóveis](/docs/1.0/prospeccao/imoveis)
- [Tarefas](/docs/1.0/prospeccao/tarefas)
"""


def _frontmatter(title): return f"---\ntitle: {title}\n---\n\n"

def call_wiki_flow(api, url, query, db, timeout=90):
    payload = {"url": url, "search_query": query, "include_flow_explanation": True}
    if db: payload["db_connection"] = db
    try:
        r = requests.post(f"{api}/wiki/flow", json=payload, timeout=timeout)
        r.raise_for_status()
        d = r.json()
        exp = d.get("flow_explanation", "")
        if not exp or len(exp.strip()) < 100:
            # fallback minimo
            flow = d.get("flow") or {}
            db_d = flow.get("database") or {}
            exp = f"# {query.capitalize()}\n\nEsta funcionalidade faz parte do SafetyDocs V3.\n"
            if db_d.get("table"):
                exp += f"\n**Tabela de dados:** `{db_d['table']}`\n"
        return exp
    except Exception as e:
        print(f"  ❌ {e}")
        return None

def call_feature(api, feature, timeout=60):
    try:
        r = requests.post(f"{api}/feature", json={"feature": feature, "include_semantic": True}, timeout=timeout)
        r.raise_for_status()
        d = r.json()
        summary = d.get("summary", {})
        mods = set()
        for cls in (d.get("backend") or {}).get("classes", []):
            for m in ["permits","shopping","contrato","ged","imobiliario","engenharia","fornecedor","prospeccao"]:
                if m in cls.get("file","").lower(): mods.add(m.capitalize())
        lines = [f"# Guia — {feature.capitalize()}\n",
                 f"Esta funcionalidade está presente em {summary.get('total_files',0)} área(s) do sistema.\n"]
        if mods:
            lines.append("## Módulos onde aparece\n")
            for m in sorted(mods): lines.append(f"- {m}")
        return "\n".join(lines)
    except Exception as e:
        print(f"  ❌ {e}")
        return None

def save_doc(output, doc_path, title, content):
    out = Path(output) / f"{doc_path}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_frontmatter(title) + content, encoding="utf-8")
    return out

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--api",           default="http://localhost:8765")
    p.add_argument("--output",        default="resources/docs/1.0")
    p.add_argument("--tenant",        default="sdv3_teste")
    p.add_argument("--db",            default=None)
    p.add_argument("--delay",         type=float, default=1.5)
    p.add_argument("--only-module",   default=None)
    p.add_argument("--skip-concepts", action="store_true")
    args = p.parse_args()

    try:
        r = requests.get(f"{args.api}/health", timeout=10)
        r.raise_for_status()
        sr = requests.get(f"{args.api}/stats", timeout=10)
        vectors = sr.json().get("vectors_count", 0) if sr.ok else 0
        print(f"✅ Context Engine OK  |  Vetores: {vectors}")
        if vectors < 100:
            print("⚠️  Rode primeiro: docker exec context-indexer-worker python src/indexer/updater.py --mode build")
            sys.exit(1)
    except Exception as e:
        print(f"❌ API inacessível: {e}"); sys.exit(1)

    generated, errors = [], []

    print(f"\n{'─'*55}\nGerando páginas dos módulos...\n{'─'*55}")
    for url_tpl, query, doc_path, title in SDV3_PAGES:
        if args.only_module and not doc_path.startswith(args.only_module): continue
        url = url_tpl.replace("{t}", args.tenant)
        print(f"\n→ {title}")
        content = call_wiki_flow(args.api, url, query, args.db or args.tenant)
        if content:
            save_doc(args.output, doc_path, title, content)
            print(f"  ✅ {doc_path}.md")
            generated.append(doc_path)
        else:
            errors.append(doc_path)
        time.sleep(args.delay)

    if not args.skip_concepts:
        print(f"\n{'─'*55}\nGerando guias gerais...\n{'─'*55}")
        for feature, query, doc_path, title in SDV3_CONCEPTS:
            print(f"\n→ {title}")
            content = call_feature(args.api, feature)
            if content:
                save_doc(args.output, doc_path, title, content)
                print(f"  ✅ {doc_path}.md")
                generated.append(doc_path)
            else:
                errors.append(doc_path)
            time.sleep(args.delay)

    # Index
    out_index = Path(args.output) / "index.md"
    out_index.write_text(INDEX_CONTENT, encoding="utf-8")
    print(f"\n✅ Index: {out_index}")
    print(f"\n{'═'*55}")
    print(f"✅ Gerados: {len(generated)}  ❌ Erros: {len(errors)}")
    print("git add resources/docs/ && git commit -m '[sdv3-wiki] Build inicial'")

if __name__ == "__main__":
    main()
