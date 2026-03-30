# CLAUDE.md — Módulo Prospecção

## Tabelas: pro_projetos, pro_imoveis, pro_tarefas, pro_documentos, pro_marcadores, pro_unidades
## Hierarquia: Marca -> Projeto -> Imóvel -> Tarefa(Subtarefa,Anexo,Comentário) | Documento | Marcador(lat/lng)

## ProjetoStatus: EM_ANDAMENTO=1, CONCLUIDO=2
## ImovelStatus: P_ANALISE=1, DESCARTADO=2, LOCADO=3, EV_APROVADO=4, FAP_LOCACAO=5
## TarefaStatus: NAO_INICIADO=1, ANDAMENTO=2, ATRASADO=3, CONCLUIDO=4, CONDICIONANTE=5
## Recorrência: RECORRENCIA_NUNCA='nunca', RECORRENCIA_DATA='data', RECORRENCIA_QTD='qtd'

## Imóvel — campos específicos
Financeiros: aluguel, iptu, condominio, ponto_comercial
Área: area_total, area_construida, area_utilizada, area_disponivel
Geo: Marcador com lat/lng

## Documentos: DocumentoTipo + DocumentoTipoGrupo. Limites: MAX_SIZE=1000, MAX_SIZE_DESCRICAO=500
## Permissões: UsuarioUnidade (pro_usuarios_unidades)
