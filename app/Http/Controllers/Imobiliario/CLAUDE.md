# CLAUDE.md — Módulo Imobiliário

## Tabelas: imo_contratos, imo_negociacoes, imo_despesas, imo_tarefas, imo_unidades, imo_proprietarios, imo_indices, imo_alugueis
## Hierarquia: Unidade -> Contrato -> Negociação / Tarefa / Despesa -> Proprietários, Aditivos, IPTU, SPU, Taxas

## ContratoStatus: VIGENTE=1, RESCINDIDO=2, VENCIDO=3
## Status calculados: STATUS_REGULAR, STATUS_JURIDICO(<45d), STATUS_RENOVATORIO(<180d,>120d), STATUS_RENOVATORIO_VENCIDO(<120d), STATUS_VENCIDO
## Limites: PRE_AVISO_RENOVATORIO=120, LIMITE_RENOVATORIO=180, LIMITE_JURIDICO=45 (dias)

## NegociacaoStatus: NAO_INICIADO=1, NEGOCIACAO=2, DISTRATO=3, CONCLUIDO=4, RENOVATORIA=5, EXPECTATIVA_DISTRATO=6, DISTRATO_CONCLUIDO=7, ASSUNCAO_RISCO=8
## TarefaStatus: NAO_INICIADO=1, ANDAMENTO=2, ATRASADO=3, CONCLUIDO=4, CONDICIONANTE=5

## Reajuste: Indice::contratoReajuste($ano, $mes). Regras: REGRA_MED, REGRA_MAX, REGRA_MIN. Many-to-many via imo_contratos_indices
