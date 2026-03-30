# CLAUDE.md — Módulo Fornecedor

## Tabelas: for_fornecedores, for_funcionarios, for_documentos, for_atividades, for_chamados, for_solicitacoes, for_grupos
## Hierarquia: Unidade->Ambiente->Atividade->AtividadeFornecedor->AtividadeFornecedorFuncionario | Fornecedor->Funcionario->Documento | Chamado->Solicitacao

## Tipos de documento: TIPO_EQUIPAMENTO='E', TIPO_FUNCIONARIO='U', TIPO_FORNECEDOR='F'
## DocumentoAprovacaoStatus: PENDENTE=1, APROVADO=2, REPROVADO=3
## AtividadeStatus: NAO_INICIADO=1, ANDAMENTO=2, ATRASADO=3, CONCLUIDO=4
## ChamadoStatus: ABERTO=1, EM_ANDAMENTO=2, CONCLUIDO=3
## Status calculado doc: Regular, Vencido, Sem Arquivo, Em Andamento, A Vencer

## Funcionalidades especiais
- ChamadoPublicoCtrl: abertura sem autenticação
- Hash de acesso externo (documentos e atividades)
- Checklists: AtividadeChecklist
- Grupos: Grupo + GrupoExterno + GrupoUsuario
- Lista Mestra: ListaMestra + ListaTipo

## Permissões: UsuarioUnidade (for_usuarios_unidades)
