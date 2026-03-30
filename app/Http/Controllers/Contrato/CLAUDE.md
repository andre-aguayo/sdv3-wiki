# CLAUDE.md — Módulo Contratos

## Tabelas: con_documentos, con_tarefas, con_tarefas_subtarefas, con_indices, con_unidades, con_marcas
## Hierarquia: Marca -> Unidade -> Documento -> Tarefa -> TarefaSubtarefa -> Anexo/Aditivo/Comentário

## Status DocumentoStatus: SEM_ARQUIVO=1, PENDENTE_ASSINATURA=2, VIGENTE=3, VENCIDO=4, CANCELADO=5, ENCERRADO=6, REVISAO=7
## Status DocumentoAprovacao: PENDENTE=1, APROVADO=2, REPROVADO=3
## Status TarefaStatus: PENDENTE=1, ATRASADO=2, CONCLUIDO=3, ANDAMENTO=4, NAO_INICIADO=5, EM_NEGOCIACAO=6

## Fluxo aprovação
- Aprovação: aprovacao_id=APROVADO + status_id=VIGENTE
- Reprovação: aprovacao_id=REPROVADO + status_id=REVISAO (motivo obrigatório)
- Job: SendEmailDocumentoAprovacao

## Índices: Indice::contratoReajuste() com regra max/min/med. Many-to-many via con_documentos_indices

## Solicitações de exclusão
Tipos: Documento, Anexo, Aditivo, Tarefa, TarefaAnexo, Subtarefa, Comentário, Índice, IndiceValor
Ao aprovar exclusão: chama remover() do model correspondente.

## Permissões: UsuarioUnidade. CON_DOCUMENTO_REMOVER para remoção.
