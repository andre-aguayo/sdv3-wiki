# CLAUDE.md — Módulo Engenharia

## Tabelas: eng_unidades, eng_disciplinas, eng_unidades_disciplinas, eng_etapas, eng_revisoes
## Hierarquia: Marca -> Unidade -> UnidadeDisciplina -> Etapa -> Revisão -> Anexo/Comentário/CC

## EtapaStatus: NAO_INICIADO=1, EM_ANDAMENTO=2, ATRASADO=3, CONCLUIDO=4, CONDICIONANTE=5
## Status calculados: STATUS_REGULAR='regular', STATUS_IRREGULAR='irregular' (última revisão reprovada)
## RevisaoStatus: PENDENTE=1, APROVADO=2, REPROVADO=3

## Fluxo: NAO_INICIADO -> Revisão PENDENTE -> APROVADO(regular) ou REPROVADO(irregular)

## Comentários: CC interno, emails externos, grupos. Hash externo: EtapaComentarioHash
## Permissões: UsuarioUnidade (eng_usuarios_unidades), PerfilUnidade
