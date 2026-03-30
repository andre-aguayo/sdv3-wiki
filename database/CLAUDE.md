# CLAUDE.md — Database (database/)

> Lido ao trabalhar em migrations ou seeders.

## Regra absoluta: classes anônimas

```php
<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::table('tabela', function (Blueprint $table) {
            $table->string('campo')->nullable();
        });
    }

    public function down()
    {
        Schema::table('tabela', function (Blueprint $table) {
            $table->dropColumn('campo');
        });
    }
};
```

## Campos padrão obrigatórios em tabelas novas

```php
$table->unsignedBigInteger('usuario_criacao_id')->nullable();
$table->datetime('dtcriacao')->nullable();
$table->unsignedBigInteger('usuario_alteracao_id')->nullable();
$table->datetime('dtalteracao')->nullable();
$table->boolean('ativo')->default(true);
// NÃO usar $table->timestamps() — projeto usa dtcriacao/dtalteracao
```

## Prefixos de tabela por módulo (ver CLAUDE.md raiz)

per_ · sho_ · con_ · imo_ · eng_ · for_ · pro_

## Regras

- Migrations sempre reversíveis: método `down()` implementado
- Usar `->nullable()` defensivamente em novas colunas de tabelas existentes
- Índices obrigatórios em FKs e colunas usadas em `where()` frequente
