"""
flow_explainer.py — SafetyDocs V3
──────────────────────────────────
Gera explicações em Markdown para a wiki do SafetyDocs V3.

PÚBLICO-ALVO: colaboradores de suporte e comercial sem conhecimento técnico.

O formato responde perguntas práticas:
  • O que é esta tela / funcionalidade?
  • Para que serve?
  • Quais são os campos e o que cada um significa?
  • O que acontece quando clico em cada botão/ação?
  • Quem recebe notificações?
  • Qual o fluxo de aprovação?
  • Quais os possíveis status e o que significam?
  • Perguntas frequentes

NÃO expõe: nomes de classes PHP, SQL, rotas técnicas,
namespaces, arquivos do sistema.
"""
from __future__ import annotations

import re
from typing import Any


# ─── Mapeamentos legíveis ─────────────────────────────────────────────────────

# Traduz prefixos de módulo para nome amigável
_MODULE_NAMES: dict[str, str] = {
    "permits":      "Permits — Licenças e Permissões Ambientais",
    "shopping":     "Shopping — Documentos de Lojas",
    "contrato":     "Contratos",
    "ged":          "GED — Gestão de Documentos",
    "imobiliario":  "Imobiliário — Contratos de Locação",
    "engenharia":   "Engenharia — Gestão de Obras",
    "fornecedor":   "Fornecedor — Gestão de Prestadores",
    "prospeccao":   "Prospecção — Pesquisa de Imóveis",
}

# Traduz status numéricos para texto legível por módulo
_STATUS_MAP: dict[str, dict[int, str]] = {
    "aprovacao": {1: "Pendente", 2: "Aprovado", 3: "Reprovado"},
    "documento": {
        1: "Sem arquivo",
        2: "Pendente de assinatura",
        3: "Vigente",
        4: "Vencido",
        5: "Cancelado",
        6: "Encerrado",
        7: "Em revisão",
    },
    "tarefa": {
        1: "Pendente",
        2: "Atrasado",
        3: "Concluído",
        4: "Em andamento",
        5: "Não iniciado",
        6: "Em negociação",
    },
    "loja": {
        1: "Ativo",
        2: "Encerrado",
        3: "Operacional",
        4: "Não operacional",
        5: "Em implantação",
    },
    "imovel": {
        1: "Para análise",
        2: "Descartado",
        3: "Locado",
        4: "EV Aprovado",
        5: "FAP Locação",
    },
    "contrato_imob": {
        1: "Vigente",
        2: "Rescindido",
        3: "Vencido",
    },
    "etapa": {
        1: "Não iniciado",
        2: "Em andamento",
        3: "Atrasado",
        4: "Concluído",
        5: "Condicionante",
    },
    "chamado": {1: "Aberto", 2: "Em andamento", 3: "Concluído"},
}

# Traduz nomes técnicos de tabela para português
_TABLE_FRIENDLY: dict[str, str] = {
    "per_documentos":           "Documentos de licença",
    "per_unidades":             "Unidades / Sites",
    "per_frentes":              "Frentes de trabalho",
    "sho_documentos":           "Documentos de loja",
    "sho_lojas":                "Lojas",
    "sho_condominios":          "Shoppings / Condomínios",
    "con_documentos":           "Contratos",
    "con_tarefas":              "Tarefas de contrato",
    "ged_diretorios":           "Diretórios do GED",
    "ged_documentos":           "Arquivos do GED",
    "imo_contratos":            "Contratos imobiliários",
    "imo_negociacoes":          "Negociações",
    "imo_despesas":             "Despesas",
    "eng_etapas":               "Etapas de obra",
    "eng_revisoes":             "Revisões",
    "for_fornecedores":         "Fornecedores",
    "for_funcionarios":         "Funcionários do fornecedor",
    "for_documentos":           "Documentos do fornecedor",
    "for_chamados":             "Chamados",
    "pro_projetos":             "Projetos de prospecção",
    "pro_imoveis":              "Imóveis prospectados",
}

# Traduz nomes de colunas para português legível
_COLUMN_FRIENDLY: dict[str, str] = {
    "id":                       "Código interno",
    "descricao":                "Descrição",
    "status_id":                "Status",
    "aprovacao_id":             "Situação de aprovação",
    "ativo":                    "Registro ativo?",
    "dtcriacao":                "Data de criação",
    "dtalteracao":              "Data da última alteração",
    "usuario_criacao_id":       "Criado por",
    "usuario_alteracao_id":     "Alterado por",
    "dtvencimento":             "Data de vencimento",
    "dtemissao":                "Data de emissão",
    "diaspreaviso":             "Dias de aviso antecipado",
    "vencimento_indefinido":    "Vencimento indefinido",
    "motivo":                   "Motivo (reprovação)",
    "dtaprovacao":              "Data de aprovação",
    "arquivo_id":               "Arquivo anexado",
    "unidade_id":               "Unidade / Site",
    "marca_id":                 "Empresa / Marca",
    "loja_id":                  "Loja",
    "condominio_id":            "Condomínio / Shopping",
    "fornecedor_id":            "Fornecedor",
    "contrato_id":              "Contrato",
    "projeto_id":               "Projeto",
    "imovel_id":                "Imóvel",
    "valor":                    "Valor (R$)",
    "observacao":               "Observações",
    "titulo":                   "Título",
    "nome":                     "Nome",
    "email":                    "E-mail",
    "telefone":                 "Telefone",
    "cpf":                      "CPF",
    "cnpj":                     "CNPJ",
    "dtinicio":                 "Data de início",
    "dtfim":                    "Data de término",
    "area_total":               "Área total (m²)",
    "area_construida":          "Área construída (m²)",
    "aluguel":                  "Valor do aluguel (R$)",
    "iptu":                     "IPTU (R$)",
    "condominio":               "Condomínio (R$)",
}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _friendly_table(table: str) -> str:
    return _TABLE_FRIENDLY.get(table, table.replace("_", " ").title())


def _friendly_column(col: str) -> str:
    return _COLUMN_FRIENDLY.get(col, col.replace("_", " ").capitalize())


def _detect_module(url: str) -> str:
    url_lower = url.lower()
    for key, name in _MODULE_NAMES.items():
        if key in url_lower:
            return name
    return "SafetyDocs V3"


def _detect_module_key(url: str) -> str:
    url_lower = url.lower()
    for key in _MODULE_NAMES:
        if key in url_lower:
            return key
    return ""


def _detect_feature(url: str, query: str) -> str:
    """Infere o nome da funcionalidade a partir da URL e query."""
    combined = (url + " " + query).lower()
    features = [
        ("aprovação", ["aprovacao", "aprovac", "aprovar", "aprovar"]),
        ("upload de arquivo", ["upload", "arquivo", "file"]),
        ("listagem", ["list", "listagem", "index"]),
        ("exportação PDF", ["pdf", "exportar"]),
        ("exportação Excel", ["excel", "exportacao"]),
        ("tarefas", ["tarefa", "task"]),
        ("documentos", ["documento", "document"]),
        ("contratos", ["contrato"]),
        ("chamados", ["chamado"]),
        ("negociação", ["negociacao", "negociação"]),
        ("revisão", ["revisao", "revisão"]),
        ("diretórios", ["diretorio", "diretório"]),
        ("etapas", ["etapa"]),
        ("fornecedores", ["fornecedor"]),
        ("imóveis", ["imovel", "imóvel"]),
    ]
    for name, keywords in features:
        if any(kw in combined for kw in keywords):
            return name
    return "funcionalidade"


def _columns_table(columns: list[dict]) -> str:
    """Gera tabela de campos legível."""
    if not columns:
        return ""
    rows = ["| Campo | Tipo | Obrigatório |", "|-------|------|-------------|"]
    for col in columns:
        name = col.get("name", "")
        if name in ("id", "dtcriacao", "dtalteracao", "usuario_criacao_id",
                    "usuario_alteracao_id", "ativo"):
            continue  # oculta campos puramente técnicos
        friendly = _friendly_column(name)
        col_type = col.get("type", "")
        # Simplifica tipos SQL para o leitor
        if any(t in col_type for t in ("int", "bigint")):
            readable_type = "Número"
        elif any(t in col_type for t in ("varchar", "text", "char")):
            readable_type = "Texto"
        elif any(t in col_type for t in ("datetime", "timestamp", "date")):
            readable_type = "Data"
        elif "tinyint(1)" in col_type or "boolean" in col_type:
            readable_type = "Sim / Não"
        elif "decimal" in col_type or "float" in col_type:
            readable_type = "Valor monetário"
        elif "json" in col_type:
            readable_type = "Lista"
        else:
            readable_type = col_type
        required = "✅ Sim" if not col.get("nullable") else "❌ Não"
        rows.append(f"| {friendly} | {readable_type} | {required} |")
    return "\n".join(rows)


def _relations_text(relations: list[dict]) -> str:
    """Descreve os relacionamentos em linguagem natural."""
    if not relations:
        return ""
    lines = []
    for rel in relations:
        rel_type = rel.get("type", "")
        related  = rel.get("related_model") or rel.get("related", "")
        method   = rel.get("method", "")
        # Traduz tipo de relação
        if rel_type in ("hasMany", "morphMany"):
            verb = f"pode ter vários **{related}**"
        elif rel_type in ("hasOne", "morphOne"):
            verb = f"possui um **{related}**"
        elif rel_type in ("belongsTo", "morphTo"):
            verb = f"pertence a um **{related}**"
        elif rel_type == "belongsToMany":
            verb = f"pode estar vinculado a vários **{related}**"
        else:
            verb = f"relacionado com **{related}**"
        lines.append(f"- {verb}")
    return "\n".join(lines)


def _infer_actions_from_flow(flow: dict, query: str) -> list[dict]:
    """
    Infere ações disponíveis ao usuário a partir do fluxo técnico.
    Retorna lista de {acao, descricao, resultado}.
    """
    query_lower = query.lower()
    actions = []

    laravel = flow.get("laravel") or {}
    if isinstance(laravel, list) and laravel:
        laravel = laravel[0]

    methods = []
    if isinstance(laravel, dict):
        ctrl_methods = laravel.get("controller_methods", [])
        methods.extend(ctrl_methods)

    vue = flow.get("vue") or {}
    vue_methods = vue.get("methods", [])

    # Infere ações a partir dos nomes de métodos
    action_keywords = {
        "list":      ("Visualizar lista",   "Exibe todos os registros com filtros e paginação"),
        "index":     ("Ver detalhes",        "Exibe as informações completas de um registro"),
        "insert":    ("Cadastrar",           "Abre o formulário para criar um novo registro"),
        "update":    ("Editar",              "Permite alterar as informações de um registro existente"),
        "remove":    ("Excluir / Inativar",  "Remove ou inativa um registro do sistema"),
        "aprovar":   ("Aprovar",             "Aprova o documento e atualiza o status para Vigente"),
        "reprovar":  ("Reprovar",            "Reprova o documento e solicita correção"),
        "upload":    ("Anexar arquivo",      "Permite enviar um arquivo ao registro"),
        "download":  ("Baixar arquivo",      "Faz o download do arquivo anexado"),
        "pdf":       ("Exportar PDF",        "Gera um relatório em PDF"),
        "excel":     ("Exportar Excel",      "Exporta os dados para uma planilha"),
        "email":     ("Enviar por e-mail",   "Envia as informações por e-mail"),
        "option":    ("Filtros / Opções",    "Carrega as opções disponíveis para os filtros"),
    }
    seen = set()
    for method in (methods + vue_methods):
        method_lower = method.lower()
        for keyword, (label, desc) in action_keywords.items():
            if keyword in method_lower and label not in seen:
                seen.add(label)
                actions.append({"acao": label, "descricao": desc})

    # Garante ações mínimas se não detectou nada
    if not actions:
        actions = [
            {"acao": "Visualizar",   "descricao": "Exibe os registros disponíveis"},
            {"acao": "Cadastrar",    "descricao": "Cria um novo registro"},
            {"acao": "Editar",       "descricao": "Atualiza as informações de um registro"},
            {"acao": "Excluir",      "descricao": "Remove um registro do sistema"},
        ]
    return actions


def _infer_notifications(flow: dict, query: str) -> list[str]:
    """Infere quem recebe notificações com base no fluxo."""
    query_lower = query.lower()
    notifications = []
    if "aprovacao" in query_lower or "aprovar" in query_lower:
        notifications += [
            "O responsável pelo documento recebe um e-mail ao ser **aprovado**",
            "O responsável recebe um e-mail ao ser **reprovado**, com o motivo",
            "Os administradores da unidade são notificados sobre pendências de aprovação",
        ]
    if "vencimento" in query_lower or "dtvencimento" in query_lower:
        notifications += [
            "O sistema envia alertas quando o documento está próximo do vencimento (conforme prazo configurado)",
            "Documentos vencidos aparecem em destaque na listagem",
        ]
    if "tarefa" in query_lower:
        notifications += [
            "Os responsáveis pelas tarefas recebem e-mail quando uma tarefa é atribuída ou alterada",
            "Tarefas atrasadas geram alertas automáticos",
        ]
    return notifications


# ─── Gerador principal ────────────────────────────────────────────────────────

def explain_flow(
    response: dict[str, Any],
    search_query: str | None = None,
    title: str | None = None,
) -> str:
    """
    Gera uma página de wiki em Markdown voltada para usuários não técnicos.

    Seções:
      1. O que é esta funcionalidade?
      2. Para que serve?
      3. Campos disponíveis
      4. Ações disponíveis (o que o usuário pode fazer)
      5. Fluxo de aprovação (se aplicável)
      6. Notificações automáticas
      7. Status possíveis
      8. Perguntas frequentes
      9. [colapsado] Informações técnicas (para suporte avançado)
    """
    parts: list[str] = []
    chain = response.get("chain") or {}
    flow  = response.get("flow") or {}
    vue   = response.get("vue") or flow.get("vue") or {}

    url     = flow.get("query") or flow.get("url_matched") or ""
    query   = search_query or ""

    module_name  = _detect_module(url)
    module_key   = _detect_module_key(url)
    feature_name = _detect_feature(url, query)

    # ── Título ────────────────────────────────────────────────────────────────
    page_title = title or f"{module_name} — {feature_name.capitalize()}"
    parts.append(f"# {page_title}\n")

    # Breadcrumb amigável
    if module_key:
        parts.append(f"> **Módulo:** {module_name}\n")

    # ── 1. O que é ────────────────────────────────────────────────────────────
    parts.append("## O que é esta funcionalidade?\n")

    # Descrição baseada na query e no módulo detectado
    feature_descriptions: dict[str, dict[str, str]] = {
        "permits": {
            "aprovação":         "Esta tela permite que o usuário responsável **aprove ou reprove documentos de licença ambiental**, como alvarás, licenças de operação e autorizações. Documentos aprovados ficam com status **Vigente**; documentos reprovados voltam para **Revisão** com o motivo registrado.",
            "upload de arquivo": "Aqui o usuário pode **enviar o arquivo** de um documento de licença ambiental. Após o upload, o documento aguarda aprovação de um responsável antes de ficar ativo.",
            "listagem":          "Esta é a **tela principal de documentos de licença** do módulo Permits. Permite visualizar, filtrar e pesquisar todos os documentos de licença ambiental cadastrados na unidade, com indicação do status de cada um.",
            "tarefas":           "Tela de gerenciamento das **tarefas e condicionantes** vinculadas aos documentos de licença. Cada tarefa representa uma obrigação que precisa ser cumprida como parte da licença.",
        },
        "shopping": {
            "aprovação":         "Permite aprovar ou reprovar documentos enviados pelas lojas. Documentos aprovados ficam **regulares**; documentos com problema ficam **irregulares** e precisam de correção.",
            "listagem":          "Tela principal de documentos de loja. Exibe todos os documentos cadastrados com seus respectivos status (Regular, Vencido, Sem arquivo, etc.).",
        },
        "contrato": {
            "aprovação":         "Permite que um aprovador revise e assine contratos. Após aprovação, o contrato fica com status **Vigente**. Em caso de reprovação, o contrato retorna para **Revisão**.",
            "listagem":          "Exibe todos os contratos cadastrados com seus status e datas de vigência.",
            "tarefas":           "Gerencia as obrigações e compromissos vinculados a cada contrato.",
        },
        "ged": {
            "listagem":          "Esta é a **árvore de documentos** do GED (Gestão Eletrônica de Documentos). Permite navegar pelas pastas e visualizar os arquivos armazenados.",
            "aprovação":         "Permite aprovar documentos que foram enviados para revisão no GED.",
        },
        "imobiliario": {
            "listagem":          "Exibe todos os contratos de locação imobiliária com seus status (Vigente, Rescindido, Vencido) e alertas de vencimento próximo.",
            "negociação":        "Registra e acompanha o histórico de negociações de um contrato imobiliário.",
        },
        "engenharia": {
            "listagem":          "Exibe as obras e unidades cadastradas com suas disciplinas e etapas de trabalho.",
            "revisão":           "Permite enviar e acompanhar revisões de etapas de obra para aprovação.",
        },
        "fornecedor": {
            "listagem":          "Exibe todos os fornecedores cadastrados com a situação dos seus documentos.",
            "chamados":          "Permite abrir e acompanhar chamados relacionados aos fornecedores.",
            "aprovação":         "Permite aprovar ou reprovar documentos enviados pelos fornecedores.",
        },
        "prospeccao": {
            "listagem":          "Exibe os projetos de prospecção e os imóveis pesquisados em cada projeto.",
            "tarefas":           "Gerencia as tarefas e atividades vinculadas a imóveis prospectados.",
        },
    }

    description = ""
    if module_key in feature_descriptions:
        for feat_key, feat_desc in feature_descriptions[module_key].items():
            if feat_key in feature_name.lower() or feat_key in query.lower():
                description = feat_desc
                break

    if not description:
        description = (
            f"Esta funcionalidade faz parte do módulo **{module_name}** "
            f"e permite gerenciar **{feature_name}** do sistema SafetyDocs V3."
        )

    parts.append(description + "\n")

    # ── 2. Para que serve ─────────────────────────────────────────────────────
    parts.append("## Para que serve?\n")

    use_cases: list[str] = []
    if "aprovacao" in query.lower() or "aprovar" in (url + query).lower():
        use_cases += [
            "Controlar o ciclo de vida dos documentos, garantindo que apenas documentos válidos fiquem ativos",
            "Registrar quem aprovou e quando, criando um histórico de auditoria",
            "Notificar automaticamente os responsáveis sobre aprovações e reprovações",
        ]
    elif "upload" in query.lower():
        use_cases += [
            "Manter os arquivos dos documentos sempre atualizados",
            "Garantir que toda atualização de arquivo passe pelo processo de aprovação",
            "Registrar o histórico de versões do arquivo",
        ]
    elif "list" in query.lower() or "listagem" in query.lower():
        use_cases += [
            "Ter uma visão geral de todos os registros com seus status atuais",
            "Filtrar e pesquisar registros por diferentes critérios",
            "Identificar rapidamente documentos vencidos ou pendentes de ação",
        ]
    else:
        use_cases += [
            "Manter as informações atualizadas e acessíveis para toda a equipe",
            "Garantir o controle e rastreabilidade das ações realizadas",
            "Facilitar a gestão e o monitoramento das atividades do módulo",
        ]

    for uc in use_cases:
        parts.append(f"- {uc}")
    parts.append("")

    # ── 3. Campos disponíveis ─────────────────────────────────────────────────
    db = flow.get("database") or {}
    columns = db.get("columns", [])
    if columns:
        parts.append("## Campos disponíveis\n")
        parts.append("Os campos abaixo estão disponíveis nesta tela:\n")
        col_table = _columns_table(columns)
        if col_table:
            parts.append(col_table)
            parts.append("")

    # ── 4. Ações disponíveis ──────────────────────────────────────────────────
    parts.append("## O que você pode fazer nesta tela?\n")
    actions = _infer_actions_from_flow(flow, query)
    if actions:
        parts.append("| Ação | O que acontece |")
        parts.append("|------|----------------|")
        for action in actions:
            parts.append(f"| **{action['acao']}** | {action['descricao']} |")
        parts.append("")
    else:
        parts.append("- Visualizar, cadastrar, editar e excluir registros\n")

    # ── 5. Fluxo de aprovação ─────────────────────────────────────────────────
    if any(w in (url + query).lower() for w in ["aprovacao", "aprovar", "aprovação"]):
        parts.append("## Fluxo de aprovação\n")
        parts.append("```")
        parts.append("Usuário envia o documento")
        parts.append("       ↓")
        parts.append("Status: Pendente de aprovação")
        parts.append("       ↓")
        parts.append("Aprovador revisa")
        parts.append("       ↓")
        parts.append("┌──────────────┬─────────────────┐")
        parts.append("│   Aprovado   │    Reprovado    │")
        parts.append("│              │                 │")
        parts.append("│   Vigente ✅  │   Em Revisão ❌ │")
        parts.append("│              │  (com motivo)   │")
        parts.append("└──────────────┴─────────────────┘")
        parts.append("```\n")
        parts.append("> 💡 **Dica:** Quando um documento é reprovado, o responsável recebe um e-mail com o motivo da reprovação e precisa corrigir e reenviar o documento.\n")

    # ── 6. Status possíveis ───────────────────────────────────────────────────
    # Detecta qual mapa de status é mais relevante
    status_maps_to_show: list[tuple[str, dict]] = []

    module_to_status = {
        "permits":     [("documento", _STATUS_MAP["documento"]), ("aprovacao", _STATUS_MAP["aprovacao"])],
        "shopping":    [("documento", _STATUS_MAP["aprovacao"]), ("loja", _STATUS_MAP["loja"])],
        "contrato":    [("documento", _STATUS_MAP["documento"]), ("tarefa", _STATUS_MAP["tarefa"])],
        "ged":         [("aprovacao", _STATUS_MAP["aprovacao"])],
        "imobiliario": [("contrato", _STATUS_MAP["contrato_imob"])],
        "engenharia":  [("etapa", _STATUS_MAP["etapa"]), ("aprovacao", _STATUS_MAP["aprovacao"])],
        "fornecedor":  [("aprovacao", _STATUS_MAP["aprovacao"]), ("chamado", _STATUS_MAP["chamado"])],
        "prospeccao":  [("imovel", _STATUS_MAP["imovel"]), ("tarefa", _STATUS_MAP["tarefa"])],
    }

    if module_key in module_to_status:
        status_maps_to_show = module_to_status[module_key]

    if status_maps_to_show:
        parts.append("## Status possíveis\n")
        for status_label, status_map in status_maps_to_show[:2]:
            parts.append(f"**{status_label.capitalize()}:**\n")
            for code, label in status_map.items():
                emoji = "✅" if "Vigente" in label or "Aprovado" in label or "Concluído" in label else \
                        "⏳" if "Pendente" in label or "Andamento" in label or "Iniciado" in label else \
                        "❌" if "Vencido" in label or "Reprovado" in label or "Cancelado" in label or "Atrasado" in label else \
                        "🔵"
                parts.append(f"- {emoji} **{label}**")
            parts.append("")

    # ── 7. Notificações automáticas ───────────────────────────────────────────
    notifications = _infer_notifications(flow, query)
    if notifications:
        parts.append("## Notificações automáticas\n")
        parts.append("O sistema envia notificações automáticas nas seguintes situações:\n")
        for n in notifications:
            parts.append(f"- {n}")
        parts.append("")

    # ── 8. Relacionamentos (amigável) ─────────────────────────────────────────
    relations = db.get("relations", [])
    rel_text = _relations_text(relations)
    if rel_text:
        parts.append("## Relações com outras áreas\n")
        parts.append("Este registro se conecta com outros dados do sistema:\n")
        parts.append(rel_text)
        parts.append("")

    # ── 9. Perguntas frequentes ───────────────────────────────────────────────
    parts.append("## Perguntas frequentes\n")

    faqs = _build_faqs(module_key, feature_name, query)
    for faq in faqs:
        parts.append(f"**{faq['pergunta']}**")
        parts.append(f"{faq['resposta']}\n")

    # ── 10. Seção técnica colapsada ───────────────────────────────────────────
    tech_info = _build_tech_section(flow, chain, vue)
    if tech_info:
        parts.append("---")
        parts.append("<details>")
        parts.append("<summary>🔧 Informações técnicas (para suporte avançado)</summary>\n")
        parts.append(tech_info)
        parts.append("</details>")

    return "\n".join(parts).strip()


def _build_faqs(module_key: str, feature_name: str, query: str) -> list[dict]:
    """Gera perguntas frequentes baseadas no módulo e feature."""
    faqs: list[dict] = []
    combined = (module_key + " " + feature_name + " " + query).lower()

    # FAQs genéricas de aprovação
    if "aprovac" in combined:
        faqs += [
            {
                "pergunta": "Quem pode aprovar documentos?",
                "resposta": "Apenas usuários com perfil de **aprovador** na unidade têm acesso ao botão de aprovação. Se não visualiza este botão, entre em contato com o administrador do sistema.",
            },
            {
                "pergunta": "O que acontece se eu reprovar um documento?",
                "resposta": "O documento volta para o status **Em Revisão** e o responsável pelo cadastro recebe um e-mail com o motivo informado. É obrigatório preencher o motivo da reprovação.",
            },
            {
                "pergunta": "Posso desfazer uma aprovação?",
                "resposta": "Não é possível desfazer uma aprovação diretamente. Caso necessário, entre em contato com o administrador do sistema.",
            },
        ]

    # FAQs de documentos vencidos
    if any(w in combined for w in ["documento", "licenca", "permits", "vencimento"]):
        faqs += [
            {
                "pergunta": "O que significa um documento com status 'Vencido'?",
                "resposta": "Significa que a data de validade do documento já passou. É necessário renovar o documento e fazer o upload da nova versão para regularizar a situação.",
            },
            {
                "pergunta": "Como aparece um documento 'Sem arquivo'?",
                "resposta": "Quando o documento foi cadastrado mas ainda não teve seu arquivo enviado. Acesse o documento e use a opção **Enviar arquivo** para regularizar.",
            },
        ]

    # FAQs de upload
    if "upload" in combined or "arquivo" in combined:
        faqs += [
            {
                "pergunta": "Quais formatos de arquivo são aceitos?",
                "resposta": "O sistema aceita os formatos mais comuns: PDF, JPG, PNG, DOC, DOCX, XLS, XLSX. Para saber o tamanho máximo permitido, consulte o administrador.",
            },
            {
                "pergunta": "O que acontece ao enviar um novo arquivo?",
                "resposta": "O arquivo anterior fica salvo no histórico de versões. O novo arquivo fica com status **Pendente de aprovação** até ser aprovado por um responsável.",
            },
        ]

    # FAQs de listagem/filtros
    if "list" in combined or "listagem" in combined:
        faqs += [
            {
                "pergunta": "Como filtrar os registros exibidos?",
                "resposta": "Use os campos de filtro no topo da tela. Você pode filtrar por status, data, unidade e outros critérios. Clique em **Pesquisar** para aplicar os filtros.",
            },
            {
                "pergunta": "Como exportar os dados da listagem?",
                "resposta": "Procure o botão **Exportar Excel** ou **Exportar PDF** no canto superior da tela para baixar os dados exibidos na listagem.",
            },
        ]

    # FAQs de fornecedor
    if "fornecedor" in combined:
        faqs += [
            {
                "pergunta": "Como cadastrar um novo fornecedor?",
                "resposta": "Clique em **Novo fornecedor**, preencha os dados da empresa e dos funcionários e salve. Em seguida, cadastre os documentos exigidos pela unidade.",
            },
        ]

    # Se não gerou FAQs suficientes, adiciona FAQ genérica
    if len(faqs) < 2:
        faqs.append({
            "pergunta": "Não encontrei o registro que preciso. O que fazer?",
            "resposta": "Verifique se os filtros aplicados estão corretos e se você tem acesso à unidade onde o registro foi cadastrado. Em caso de dúvida, contate o suporte.",
        })

    return faqs[:5]  # máximo 5 FAQs por página


def _build_tech_section(flow: dict, chain: dict, vue: dict) -> str:
    """Seção técnica colapsada — para uso do time de suporte avançado."""
    lines: list[str] = []

    laravel = flow.get("laravel") or {}
    if isinstance(laravel, list) and laravel:
        laravel = laravel[0]

    if isinstance(laravel, dict) and laravel:
        lines.append("**Backend Laravel:**")
        if laravel.get("route"):
            lines.append(f"- Rota: `{laravel.get('http_method', 'GET')} {laravel['route']}`")
        if laravel.get("controller"):
            lines.append(f"- Controller: `{laravel['controller']}`")
        if laravel.get("method"):
            lines.append(f"- Método: `{laravel['method']}`")
        if laravel.get("service"):
            lines.append(f"- Service: `{laravel['service']}`")
        if laravel.get("model"):
            lines.append(f"- Model: `{laravel['model']}`")

    db = flow.get("database") or {}
    if db.get("table"):
        lines.append(f"\n**Banco de dados:**")
        lines.append(f"- Tabela: `{db['table']}`")
        lines.append(f"- Origem do schema: `{db.get('source', 'N/A')}`")

    vue_file = (vue or {}).get("component_file", "")
    if vue_file:
        lines.append(f"\n**Frontend Vue:**")
        lines.append(f"- Componente: `{vue_file}`")

    files = flow.get("files", [])
    if files:
        lines.append(f"\n**Arquivos do sistema envolvidos:**")
        for f in files[:8]:
            if f:
                lines.append(f"- `{f}`")

    return "\n".join(lines) if lines else ""
