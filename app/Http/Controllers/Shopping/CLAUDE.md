# CLAUDE.md — Módulo Shopping

## Entidades e tabelas

| Model                  | Tabela                     |
|------------------------|----------------------------|
| `Condominio`           | `sho_condominios`          |
| `Loja`                 | `sho_lojas`                |
| `Documento`            | `sho_documentos`           |
| `Tarefa`               | `sho_tarefas`              |
| `Condicionante`        | `sho_condicionantes`       |
| `Notificacao`          | `sho_notificacoes`         |
| `Kit`                  | `sho_kits`                 |
| `Lojista`              | `sho_lojistas`             |

## Hierarquia

```
Condominio → Loja → Documento → Tarefa / Condicionante / Notificacao
                                    └→ Subtarefa, Anexo, Atividade, CC
```

## Constantes de status

```php
// DocumentoAprovacao
const PENDENTE = 1; const APROVADO = 2; const REPROVADO = 3;

// TarefaStatus / NotificacaoStatus
const NAO_INICIADO = 1; const ANDAMENTO = 2; const ATRASADO = 3;
const CONCLUIDO = 4; const CONDICIONANTE = 5;

// CondicionanteStatus
const INICIAR = 1; const VIGENCIA_LICENCA = 2; const ATRASADO = 3;
const CONCLUIDO = 4; const CONDICIONANTE = 5;

// LojaStatus
const ATIVO = 1; const ENCERRADO = 2; const OPERACIONAL = 3;
const NAO_OPERACIONAL = 4; const EM_IMPLANTACAO = 5;

// DocumentoImportancia
const NAO_CONTABILIZADO_ID = 1; const CONTABILIZADO_ID = 2;
```

## Status calculado do documento

`Regular` · `Vencido` · `Sem Arquivo` · `Em Andamento` · `Obtenção` · `Irregular` · `A Vencer`
- **Irregular** = arquivo presente mas reprovado na aprovação

## Permissões (dois tipos)

- **Por Frente**: `UsuarioFrentePermissao` + `FrentePermissao`
- **Por Loja**: `UsuarioLojaPermissao` + `LojaPermissao`
- **Lojistas**: `LojistaPermissao` → `LojistaLoja` (autenticação própria)

## Recorrência (Tarefas/Notificações)

```php
const RECORRENCIA_NUNCA = 'nunca';
const RECORRENCIA_DATA  = 'data';
const RECORRENCIA_QTD   = 'qtd';
```

## Solicitações de exclusão

Sistema de aprovação para remoção: `PENDENTE → APROVADO / REPROVADO`
