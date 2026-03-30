# CLAUDE.md — Módulo Permits

## Entidades e tabelas

| Model                  | Tabela                        |
|------------------------|-------------------------------|
| `Documento`            | `per_documentos`              |
| `DocumentoAprovacao`   | `per_documentos_aprovacoes`   |
| `DocumentoVersao`      | `per_documentos_versoes`      |
| `Unidade`              | `per_unidades`                |
| `Frente`               | `per_frentes`                 |

## Hierarquia

```
Marca → Unidade → Frente → Documento → Tarefa/Condicionante
                              └→ Versão, Aprovação, Arquivo
```

## Constantes de status

```php
// DocumentoAprovacao
const PENDENTE = 1;
const APROVADO = 2;
const REPROVADO = 3;
```

## Status calculado do documento

`Regular` · `Pré-vencimento` · `Vencido` · `Sem arquivo`
Calculado via `selectStatus()` no Model.

## Campos de data importantes

```php
$documento->dtvencimento           // data de vencimento
$documento->dtvencimento_anterior  // versão anterior (salvar via isDirty)
$documento->dtemissao              // data de emissão
$documento->vencimento_indefinido  // booleano (0/1)
$documento->diaspreaviso           // dias de antecedência para alerta
```

## Fluxo de aprovação — CRÍTICO

Quando status muda para PENDENTE, **sempre** limpar todos os campos:

```php
$documento->aprovacao_id         = DocumentoAprovacao::PENDENTE;
$documento->dtaprovacao          = null;
$documento->motivo               = null;
$documento->admin_aprovacao      = false;
$documento->usuario_aprovacao_id = null;
```

Dispara reset em dois cenários:
1. Upload de novo arquivo → `ArquivoCtrl::uploadPerDocumento()`
2. Alteração de `dtvencimento` → `DocumentoCtrl::save()` via `isDirty('dtvencimento')`

## Upload de arquivos

- Controller: `ArquivoCtrl::uploadPerDocumento()`
- Suporta upload normal e **chunked** (`ChunkedFileUpload`)
- Ao completar: cria versão anterior + atualiza `arquivo_id` + reseta aprovação
- IA opcional: análise automática do arquivo se habilitado no tenant
