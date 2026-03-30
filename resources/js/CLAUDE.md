# CLAUDE.md — Frontend Vue (resources/js/)

> Lido automaticamente ao trabalhar em qualquer arquivo de `resources/js/`

## Stack frontend

- Vue 3 (Composition API) + Vue Router 4
- PrimeVue 3 (componentes UI) + PrimeFlex 3 (CSS utilities) + PrimeIcons
- Chart.js 3 + Highcharts 10 para gráficos
- Vite 6 com Laravel Vite Plugin
- vue-i18n (pt_br / en_us)

## Estrutura de arquivos

```
resources/js/
├── pages/<modulo>/              ← Views por módulo (ex: pages/permits/documento/)
├── components/                  ← Componentes compartilhados
│   └── <modulo>/               ← Componentes específicos do módulo
├── service/tenant/<modulo>/    ← Camada de API (axios)
├── router/modules/<modulo>.js  ← Rotas por módulo
└── admin/pages/                ← Área administrativa
```

## Padrão de Service (camada API)

```javascript
const BASE_URL = import.meta.env.VITE_APP_URL + `/api/${TENANT}`;
const ENTITY   = 'permits/documentos';
const CONFIG   = { headers: { Authorization: `Bearer ${TOKEN}` } };

export default {
    list:   (params)     => axios.get(`${BASE_URL}/${ENTITY}/list`, { ...CONFIG, params }),
    index:  (id)         => axios.get(`${BASE_URL}/${ENTITY}/${id}`, CONFIG),
    store:  (data)       => axios.post(`${BASE_URL}/${ENTITY}`, data, CONFIG),
    update: (id, data)   => axios.put(`${BASE_URL}/${ENTITY}/${id}`, data, CONFIG),
    remove: (id)         => axios.delete(`${BASE_URL}/${ENTITY}/${id}`, CONFIG),
};
```

## Variáveis de ambiente

Prefixo `VITE_*` no `.env`:
- `VITE_APP_URL` — URL base da aplicação
- `VITE_PER_PAGE` — paginação padrão

## Compilação

```bash
npm run dev    # Vite HMR em http://localhost:5174
npm run build  # Build produção
```

Lazy loading de módulos via `utils/module-loader.js`.

## Referência circular em árvore recursiva

Quando um componente Vue importa a si mesmo:
- Usar `markRaw()` + carregamento dinâmico em vez de auto-import direto
- Ver `documentacao/originais/SOLUCAO_REFERENCIA_CIRCULAR.md`

## Regras

- Composition API sempre — sem Options API
- Comunicação com backend APENAS via services (`service/tenant/`)
- Nunca `fetch()` direto em componente
- Usar PrimeVue para componentes de UI — sem instalar outras libs de UI sem alinhamento
