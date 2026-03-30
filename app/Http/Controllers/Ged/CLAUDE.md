# CLAUDE.md — Módulo GED

## Tabelas: ged_diretorios, ged_documentos, ged_diretorios_comentarios, ged_tarefas, ged_backups
## Hierarquia: Diretorio (raiz) -> Diretorio (filho, via diretorio_id) -> Documento / Comentario / Tarefa
## Caminho completo: func_gedGetPath(id)

## Status Diretorio: PENDENTE=1, APROVADO=2, REPROVADO=3, EM_ANALISE=4
## Status TarefaStatus: NAO_INICIADO=1, ANDAMENTO=2, ATRASADO=3, CONCLUIDO=4

## Permissões globais (tabela permissoes)
GED_DIRETORIO_VISUALIZAR_TODAS, GED_DIRETORIO_RAIZ, GED_DIRETORIO_CLONE, GED_DOCUMENTO_APROVACAO

## Permissões por diretório (ged_diretorios_permissoes)
Dirs: GED_DIRETORIO_INCLUIR, _REMOVER, _EDITAR, _ZIP
Docs: GED_DOCUMENTO_VISUALIZAR, _INCLUIR, _REMOVER
Cache: UsuarioDiretorio via updateUsuarioAcesso(). Estados: CHECKED=1, CHECKED_PARCIAL=2, UNCHECKED=0

## Compartilhamento externo
DiretorioHash: UUID + senha bcrypt + expiração (+7 dias)
URL: /{tenant}/ged/diretorios/documentos/{hash}
DiretorioComentarioHash: resposta externa via email

## Remoção recursiva: valida permissão em cada nível, remove recursivo, Arquivo::remove()
