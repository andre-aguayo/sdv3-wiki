# CLAUDE.md — SafetyDocs V3

> Contexto raiz lido automaticamente pelo Claude Code em toda sessão.
> Consolida todos os `.mdc` do Cursor. Sub-contextos nos subdiretórios.
> **Responder SEMPRE em Português do Brasil.**

---

## Stack

| Camada       | Tecnologia                                                       |
|--------------|------------------------------------------------------------------|
| Backend      | Laravel 8 · PHP 8.x · Laravel Sanctum · MySQL                   |
| Frontend     | Vue 3 (Composition API) · PrimeVue 3 · PrimeFlex 3 · Vue Router 4 |
| Build        | Vite 6 (Laravel Vite Plugin)                                     |
| i18n         | vue-i18n (pt_br / en_us)                                        |
| Multi-tenant | Database-per-tenant · banco MySQL separado por cliente           |

---

## Módulos

`permits` · `shopping` · `fornecedor` · `ged` · `imobiliario` · `contrato` · `engenharia` · `prospeccao`

Estrutura padrão de cada módulo:

```
app/Http/Controllers/<Modulo>/        ← Controllers (sufixo Ctrl)
app/Models/Tenant/<Modulo>/           ← Eloquent Models (conexão tenant)
app/Jobs/Tenant/<Modulo>/             ← Jobs assíncronos
app/Mail/Tenant/<Modulo>/             ← Mails
resources/js/pages/<modulo>/          ← Pages Vue
resources/js/service/tenant/<modulo>/ ← Services API (axios)
resources/js/router/modules/<modulo>.js
```

---

## Convenções de nomenclatura — CRÍTICO

| Item               | Padrão                                                      | ❌ NÃO usar              |
|--------------------|-------------------------------------------------------------|--------------------------|
| Controller         | Sufixo `Ctrl` (ex: `DocumentoCtrl.php`)                     | `DocumentoController`    |
| Timestamp criação  | `dtcriacao` · `usuario_criacao_id`                          | `created_at`             |
| Timestamp alteração| `dtalteracao` · `usuario_alteracao_id`                      | `updated_at`             |
| Soft delete        | Campo `ativo` (booleano)                                    | `SoftDeletes` do Laravel |
| Migrations         | Classes **anônimas** (`return new class extends Migration`) | Classes nomeadas         |

**Prefixos de tabela por módulo:**

| Módulo       | Prefixo | Exemplo              |
|--------------|---------|----------------------|
| permits      | `per_`  | `per_documentos`     |
| shopping     | `sho_`  | `sho_lojas`          |
| contratos    | `con_`  | `con_documentos`     |
| imobiliário  | `imo_`  | `imo_contratos`      |
| engenharia   | `eng_`  | `eng_unidades`       |
| fornecedor   | `for_`  | `for_fornecedores`   |
| prospecção   | `pro_`  | `pro_projetos`       |
| compartilhado| —       | `usuarios` `arquivos`|

---

## Multi-Tenant

- Conexão admin/catálogo: `padrao` → `App\Models\Padrao\`
- Conexão do cliente: `tenant` (dinâmica por request) → `App\Models\Tenant\`
- Resolução: `{tenant}` na URL → `TenantMiddleware` → `Tenant\Connection`
- Cache: chave `tenant:{domain}`, TTL 1 hora
- Tenant acessível via `config('tenant.current')` após middleware
- **NUNCA** hardcodar nome de banco — sempre usar a conexão configurada

```php
Route::group(['prefix' => '{tenant}', 'middleware' => ['tenant:api']], function () {
    // rotas do módulo
});
```

---

## Padrão de Controller

```php
// app/Http/Controllers/Permits/DocumentoCtrl.php
class DocumentoCtrl extends Controller
{
    public function list(Request $request) {
        $DB = Documento::busca();
        Documento::setFilter($DB, $request);  // FilterTrait
        Documento::setOrder($DB, $request);   // OrderTrait
        return response()->json($DB->paginate($request->input('perPage', 15)), Response::HTTP_OK);
    }

    public function index($id) {
        return response()->json(Documento::find($id), Response::HTTP_OK);
    }

    public function insert(Request $request) { return $this->save($request, new Documento()); }

    public function update(Request $request, $id) {
        $doc = Documento::find($id);
        if (!$doc) return response()->json(['errors' => ['descricao' => ['Dados não encontrados']]], 422);
        return $this->save($request, $doc);
    }

    public function remove($id) {
        $doc = Documento::find($id);
        $doc->ativo = false;   // soft delete via campo ativo
        $doc->save();
        return response()->json(null, Response::HTTP_NO_CONTENT);
    }

    protected function save(Request $request, Documento $doc) {
        try {
            DB::beginTransaction();
            $doc->fill($request->input());
            $doc->save();
            DB::commit();
            return response()->json($doc, Response::HTTP_OK);
        } catch (\Exception $e) {
            DB::rollback();
            throw $e;
        }
    }
}
```

---

## Padrão de Model (Tenant)

```php
namespace App\Models\Tenant\Permits;

use App\Traits\FilterTrait, OrderTrait, NameTrait, LoggableTrait;
use Illuminate\Database\Eloquent\Model;

class Documento extends Model
{
    use FilterTrait, OrderTrait, NameTrait, LoggableTrait;

    protected $connection = 'tenant';      // OBRIGATÓRIO para models tenant
    protected $alias      = 'd';
    protected $table      = 'per_documentos';
    public    $timestamps = false;         // Usa dtcriacao/dtalteracao

    protected $fillable      = ['descricao', 'status_id', 'ativo'];
    protected $like_fields   = ['descricao'];
    protected $custom_fields = ['status' => 'statusFilter'];

    const STATUS_PENDENTE = 1;
    const STATUS_APROVADO = 2;
}
```

**Traits por caso de uso:**

| Trait         | Quando usar                                    |
|---------------|------------------------------------------------|
| `FilterTrait` | Filtros dinâmicos via query string (toda listagem) |
| `OrderTrait`  | Ordenação dinâmica (toda listagem)             |
| `NameTrait`   | `tableName()`, `tableNameComplete()`           |
| `LoggableTrait` | Log automático em `logs_operacoes`           |
| `ExcelTrait`  | Exportação via PhpSpreadsheet                  |

---

## Padrões de resposta HTTP

```php
return response()->json($data, Response::HTTP_OK);                       // 200
return response()->json(['errors' => ['campo' => ['msg']]], 422);        // validação
return response()->json(null, Response::HTTP_NO_CONTENT);                // 204
```

---

## Segurança e rotas

- Toda rota protegida **DEVE** ter `->name('rota.nome')` — sem name = bypass de autorização
- Middleware `authorization` verifica permissão pelo nome da rota
- `routes/api.php` → rotas tenant · `routes/api-admin.php` → rotas admin

---

## Padrão de commit

```
[sdv3-xxx] Breve resumo das alterações em português
```

1. `git branch --show-current` → prefixo entre colchetes
2. Analisar `git diff --staged` para o resumo

---

## Wiki automática

> Detalhes em `docs-wiki/WIKI_ARCHITECTURE.md`

**Fase 1 — Build inicial com `context-generator`:**
Roda uma única vez para escanear o repositório e gerar todos os `.md` base.
Ver `docs-wiki/CONTEXT_GENERATOR_SETUP.md`.

**Fase 2 — Incremento por push via Dify + Gemini:**
GitHub Actions → extrai diff → Dify webhook → Gemini gera Markdown → commit em `resources/docs/`.

---

## Proibido

- ❌ `created_at` / `updated_at` — usar `dtcriacao` / `dtalteracao`
- ❌ `SoftDeletes` do Laravel — usar campo `ativo`
- ❌ Rota protegida sem `->name()`
- ❌ Nome de banco hardcoded
- ❌ Lógica de negócio em Model (só scopes, casts, relacionamentos)
- ❌ Editar `resources/docs/` manualmente (gerido pelo pipeline)
- ❌ Classes nomeadas em migrations
