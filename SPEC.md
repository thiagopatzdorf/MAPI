# MAPI v0.1 — especificação (rascunho de desenho, 2026-10-20)

> **MAPI** = contrato de uma *capacidade* com garantia. Um arquivo, três
> leitores: o programa (via OpenAPI), o agente (via MCP) e o auditor (via a
> suíte de conformidade gerada). Não compete com OpenAPI/MCP/Arazzo: **compila
> para os três** e **importa** dos dois primeiros.

## 1. Formato: YAML validado por JSON Schema 2020-12

Decisão medida, não de gosto:

| critério | YAML + JSON Schema | TypeSpec-like (linguagem própria) |
|---|---|---|
| validação pronta | JSON Schema 2020-12 é o que o MCP usa em `inputSchema`/`outputSchema` e o que OpenAPI 3.1+ usa; validadores em toda linguagem [li: spec do MCP, research §1.1] | precisa de parser, LSP e compilador próprios antes do primeiro usuário |
| edição | VS Code valida YAML por JSON Schema (`yaml.schemas`) sem plugin novo [memória, não conferido] | plugin novo |
| geração | OpenAPI, Arazzo e Overlay já são YAML/JSON; `x-mapi-*` entra por Overlay sem tocar no original [li: research §1.2] | tradução extra |
| diff/review | linha a linha, como qualquer `openapi.yaml` | idem, mas sintaxe que ninguém conhece |

**Regra:** a *forma canônica* é `<nome>.mapi.yaml`. Um documento OpenAPI 3.1/3.2
com os campos `x-mapi-*` definidos em §7 **é fonte MAPI equivalente** (o
importador os lê; o exportador os escreve). Assim ninguém precisa de arquivo
novo para começar — só de um overlay.

Nomes de campo em **inglês** (os três alvos são em inglês; o esboço inicial
em português está mapeado em §9). Texto livre (`when_to_use`, `reason`) em
qualquer língua.

## 2. Modelo de dados

```yaml
mapi: "0.1"                     # versão do formato (obrigatório)
capability: cloudflare.rest.write   # id: ^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$ (obrigatório)
version: 1                      # inteiro, sobe quando input/effect/inverse/proof mudam (obrigatório)
title: Escrever na API v4 do Cloudflare           # ≤ 80 chars (obrigatório)
when_to_use: >-                 # para o modelo; ≤ 300 chars (obrigatório; limite medido: GPT corta em 300)
  POST/PUT/PATCH em qualquer endpoint da API v4 sem tool própria. Seco por padrão.
when_not_to_use: >-             # opcional, ≤ 300
  DELETE (use cloudflare.apagar) e qualquer coisa que uma tool específica já faça.

effect: write                   # read | write | destroy (obrigatório)
idempotent: false               # obrigatório se effect != read; read ⇒ true implícito
open_world: false               # opcional; default: false (MCP openWorldHint default é true — invertido de propósito)

input:  { JSON Schema 2020-12, type: object }   # obrigatório
output: { JSON Schema 2020-12 }                 # obrigatório (o compilador envolve no envelope §4)

consent:                        # obrigatório se effect != read
  dry_run: default              # default | supported | none  (write/destroy ⇒ só `default`)
  confirm:
    parameter: confirm          # nome do booleano injetado no input (default: confirm)
  refuses:                      # lista fechada de recusas, cada uma testável
    - id: delete_sem_prova
      when: "$.input.method == 'DELETE'"      # Arazzo Criterion `simple`
      reason: "destruir exige prova de reconstrução (cloudflare.apagar)"

reversible:                     # obrigatório se effect != read  (um dos dois ramos)
  inverse:                      # ramo A: há inversa
    capability: cloudflare.rest.write
    args: { method: "PUT", path: "$.input.path", body: "$.state_before" }   # expressões sobre input/output/state_before
    captures_state_before: true # a capacidade devolve `state_before` para a inversa usar
  # irreversible:               # ramo B: não há inversa (ex.: enviar e-mail, comprar número)
  #   reason: "..."             # obriga consent.dry_run=default e proof presente

precondition:                   # obrigatório se effect == destroy
  evidence:
    - id: backup
      read: { capability: gcp.snapshot.get, args: { name: "$.input.proof" } }
      expect: { condition: "$.status == 'READY' && $.sourceDisk endsWith $.input.name", type: simple }
      max_age_s: 86400

proof:                          # obrigatório se effect != read
  read: { capability: cloudflare.rest.get, args: { path: "$.input.path" } }   # SEMPRE uma capacidade effect: read
  expect:                       # Arazzo Criterion Object (context/condition/type) — reuso exato
    - { context: "$.response.body", condition: "$.result == $.input.body", type: jsonpath }
  within_s: 60                  # janela de polling; default 0 (uma leitura só)
  interval_s: 5

budget:                         # obrigatório (pode ser zero)
  cost: { amount: 0, unit: "USD" }      # por chamada; unit livre (USD, BRL, credits, tokens)
  max_output_bytes: 65536                # obrigatório; o compilador corta/pagina acima disso
  max_duration_s: 120                    # opcional
  rate: { per: "day", max: 100000 }      # opcional

bindings:                       # como a capacidade é alcançada; ≥ 1 (obrigatório)
  http:
    method: POST                # read ⇒ GET|HEAD|QUERY; write ⇒ POST|PUT|PATCH; destroy ⇒ DELETE|POST
    url: "https://api.cloudflare.com/client/v4{path}"
    auth: bearer                # nome do securityScheme emitido
  mcp:
    tool: cloudflare_rest       # nome da tool emitida (default: capability com `.`→`_`)
  python:
    callable: factory_cauteloso.cloudflare:rest   # para o servidor de referência

examples:                       # ≥ 1 (obrigatório): viram casos da suíte
  - name: patch_registro_dns
    input: { method: PATCH, path: "/zones/x/dns_records/y", body: { ttl: 300 } }
    dry_run_expected: { would_do: "PATCH /zones/x/dns_records/y" }

x-anything: ...                 # extensões: qualquer chave `x-` é aceita e ignorada pelo núcleo
```

### 2.1 Semântica de cada campo (o que o leitor pode assumir)

- **`effect`**
  - `read`: não muda estado observável; repetível; cliente pode chamar sem
    consentimento. ⇒ MCP `readOnlyHint: true`; OpenAPI GET; `x-openai-isConsequential: false`.
  - `write`: muda estado, **aditiva ou substitutiva, com volta** (`reversible.inverse`)
    ou declaradamente sem volta (`reversible.irreversible`). ⇒ `readOnlyHint:false, destructiveHint:false`.
  - `destroy`: remove algo. Exige `precondition.evidence` (a prova de que dá
    para levantar vem **antes**) e `proof` (o recurso sumiu). ⇒ `destructiveHint: true`.
- **`idempotent`**: repetir com os mesmos args não altera o estado além da
  primeira vez. Se `true` e `bindings.http` existe, o compilador emite o
  parâmetro `Idempotency-Key` (draft IETF) **ou** exige que `input` tenha um
  campo marcado `x-mapi-idempotency-token: true` (Smithy `idempotencyToken`).
- **`consent.dry_run: default`**: toda chamada sem `confirm: true` **não executa**
  e devolve o envelope seco (§4) com `would_do`. Travas (`refuses`,
  `precondition`) rodam **antes** do seco, para o agente saber já no ensaio que
  a chamada vai ser recusada (regra da casa, `receitas.py`).
- **`consent.confirm`**: o booleano injetado no `input`; no MCP, o compilador
  também sabe responder `input_required` (MRTR) pedindo a confirmação por
  `elicitation/create` quando o cliente declara suporte — **o mesmo contrato,
  dois mecanismos**.
- **`reversible.inverse`**: outra capacidade (ou a mesma, se `idempotent`) que,
  com os `args` calculados a partir de `input`, `output` e `state_before`,
  devolve o estado anterior. `captures_state_before: true` obriga a capacidade
  a devolver `state_before` no envelope (é como o `trafego_antes` do
  `cloud_run_trafego` hoje, só que tipado).
- **`reversible.irreversible.reason`**: existe porque fingir inversa é pior que
  não ter (enviar e-mail, publicar, comprar). O compilador aceita, mas força
  `consent.dry_run: default`, `proof` e marca no OpenAPI/MCP
  (`x-mapi-irreversible`, e no `description` do MCP a frase "SEM VOLTA").
- **`precondition.evidence`**: leituras que têm de passar antes de executar
  (e antes do seco). É o `_conferir_prova` da `receita_apagar` generalizado.
- **`proof`**: `read` é obrigatoriamente uma capacidade `effect: read`;
  `expect` é lista de `Criterion` do Arazzo 1.1 (context/condition/type);
  `within_s`/`interval_s` dão a janela (VM leva segundos para virar RUNNING).
  O resultado da chamada só é `ok: true` se **todos** os critérios passarem na
  releitura; `202/200` sem prova é `ok: false, delivered: unknown`.
- **`budget`**: `cost` por chamada (somável em fluxos), `max_output_bytes`
  (o servidor de referência trunca com `truncated: true` e `next` quando
  possível), `max_duration_s`, `rate`.
- **`examples`**: cada um vira caso de conformidade (seco, confirmado com fake,
  prova, inversa).

## 3. Regras que o compilador recusa (lista fechada, cada uma com teste)

| # | recusa | por quê (defeito que impede) |
|---|---|---|
| R1 | `effect` ausente ou fora de `read|write|destroy` | tool sem efeito vira `destructiveHint: true` por padrão no MCP — ruído que ensina o cliente a ignorar o hint |
| R2 | `write`/`destroy` sem `reversible.inverse` **nem** `reversible.irreversible.reason` | "destruir e criar custam o mesmo e os dois têm volta"; sem inversa escrita, ninguém limpa |
| R3 | `inverse.capability` inexistente no conjunto compilado, ou com `effect: read`, ou igual à própria sem `idempotent: true` | inversa que não escreve não desfaz nada |
| R4 | `write`/`destroy` sem `proof` | "enviado não é entregue" |
| R5 | `proof.read.capability` com `effect != read` | prova que escreve contamina o estado que mede |
| R6 | `destroy` sem `precondition.evidence` | só se destrói o que se sabe reconstruir, e a prova vem antes |
| R7 | `write`/`destroy` com `consent.dry_run != default` | seco por padrão é a regra, não opção |
| R8 | `read` com `consent` ou `reversible` | contrato mente sobre o efeito (ou o efeito está errado) |
| R9 | `budget.max_output_bytes` ausente | saída sem teto estoura a janela do modelo (medido: worker lendo arquivo inteiro) |
| R10 | `when_to_use` > 300 chars ou vazio | o construtor de GPT corta em 300; descrição vaga = tool errada escolhida (Speakeasy) |
| R11 | `bindings.http.method` incompatível com `effect` (ex.: `read` com POST sem `x-mapi-method-override`) | o programa leria GET como seguro |
| R12 | `examples` vazio | sem exemplo não há caso de conformidade; sem caso, "MAPI" é só um rótulo |
| R13 | chave desconhecida no topo sem prefixo `x-` | erro de digitação vira campo ignorado em silêncio (qwen-code v1→v2, medido na casa) |
| R14 | `idempotent: true` sem token nem binding que o garanta | idempotência declarada e não implementada |
| R15 | em **fluxo** (Arazzo): passo que chama `write`/`destroy` cujo `reversible` é `irreversible` sem `consent` explícito no fluxo; soma de `budget.cost` > `flow.budget`; passo `destroy` sem `precondition` satisfeita por passo anterior | composição determinística: o avaliador recusa o plano, não o modelo |

Recusa é `exit 2` com `{rule: "R2", capability, path, message}` — JSON, para o
importador marcar o que precisa de decisão humana (§6).

## 4. Envelope de resposta (o que os três leitores recebem)

```jsonc
// seco (sem confirm)
{ "ok": true, "dry_run": true, "would_do": "PATCH /zones/x/dns_records/y",
  "refused": null, "precondition": {"backup": "ok"}, "to_execute": "repeat with confirm=true",
  "inverse": {"capability": "cloudflare.rest.write", "args": {...}} }

// recusado (antes do seco)
{ "ok": false, "refused": {"id": "delete_sem_prova", "reason": "..."} }

// executado
{ "ok": true, "dry_run": false, "result": {...}, "state_before": {...},
  "proof": {"checked": true, "passed": true, "read_at": "2026-10-20T12:00:00Z", "attempts": 2},
  "inverse": {"capability": "...", "args": {...}},
  "budget": {"cost": {"amount": 0, "unit": "USD"}, "output_bytes": 1832, "truncated": false} }

// enviado mas não provado
{ "ok": false, "dry_run": false, "result": {...}, "proof": {"checked": true, "passed": false, ...},
  "error": "accepted by the server, but the re-read does not show the requested state" }
```

É o `{ok, seco, faria, para_executar, volta, confirmado_pelo_estado}` da casa,
com nome fixo e `outputSchema` gerado. Compatibilidade: o compilador pode emitir
aliases em português (`seco`, `faria`, `volta`) por `x-mapi-aliases` enquanto
os clientes da casa migram.

## 5. Versionamento e extensões

- `mapi` = versão do formato (semver menor; v0.x pode quebrar).
- `version` da capacidade sobe em mudança de `input`, `effect`, `reversible`,
  `proof` ou `budget` (mudança de `when_to_use` não sobe). No MCP vira
  `title: "<title> (v2)"`? **Não**: vira `x-mapi-version` no OpenAPI e sufixo
  no `_meta` do MCP; nome da tool não muda (clientes cacheiam `tools/list`).
- Extensões: chave `x-*` em qualquer nível, ignorada pelo núcleo, preservada
  nos emissores (OpenAPI já aceita `x-`; no MCP vai para `_meta` se confirmado,
  senão é descartada com aviso).
- Perfis (futuro): `profile: strict` = R1–R15; `profile: lenient` = só R1, R9,
  R10, R12 (para importação em massa).

## 6. Importador OpenAPI → MAPI (pré-preenchimento + marcação)

Entrada: OpenAPI 3.0/3.1/3.2 (+ Overlay opcional). Para cada operação:

| campo MAPI | heurística (determinística) | marca `TODO` quando |
|---|---|---|
| `capability` | `tags[0].operationId` → `tag.op` em snake_case | sem `operationId` (gera `path_method` e marca) |
| `effect` | GET/HEAD/QUERY ⇒ `read`; DELETE ⇒ `destroy`; POST/PUT/PATCH ⇒ `write`; override se `x-openai-isConsequential: false` em não-GET ⇒ marca conflito; path com `purge|destroy|reset|truncate|revoke` ⇒ `destroy` | POST em path que termina em verbo de leitura (`:search`, `/query`) ⇒ `read?` |
| `idempotent` | PUT/DELETE/GET ⇒ true; POST/PATCH ⇒ false; `Idempotency-Key` em parameters ⇒ true | sempre que POST |
| `when_to_use` | `summary` (≤ 300), senão `description` cortada, senão `x-speakeasy-mcp.description` | > 300 ou vago (regex de "get|fetch|returns" sem objeto) — marca para reescrever |
| `input`/`output` | parâmetros + requestBody ⇒ objeto; `responses.2xx.content.application/json.schema` | sem schema de resposta |
| `reversible.inverse` | pares no mesmo `tag`: `create*`↔`delete*`, `enable`↔`disable`, PUT ↔ PUT com `state_before`, PATCH ↔ PATCH com `state_before` | **sempre marca** (inversa é decisão humana: o importador só propõe) |
| `proof.read` | GET no mesmo path (ou path sem o último segmento) com `expect` = igualdade dos campos do body | sem GET correspondente ⇒ `TODO proof` |
| `precondition` | nunca inferido | sempre em `destroy` |
| `budget` | `max_output_bytes: 65536`; `cost: 0`; `rate` de `x-ratelimit-*`/`RateLimit-Policy` se documentado | custo monetário |
| `consent` | `dry_run: default` para `write/destroy` | nunca |
| `examples` | `example`/`examples` da operação | ausentes ⇒ `TODO example` |

Saída: `<api>.mapi.yaml` com comentários `# TODO(R2): ...` e um relatório JSON
`{total, auto, todo_por_regra}` — o número que o experimento 1 de `adocao.md` mede.
Alternativa sem arquivo novo: emitir um **Overlay** que acrescenta os `x-mapi-*`
ao OpenAPI original.

## 7. Mapeamento exato para OpenAPI 3.1/3.2

| MAPI | OpenAPI (nativo quando existe; `x-mapi-*` quando não) |
|---|---|
| `capability` | `operationId` (com `.`→`_`); `tags: [prefixo]` |
| `title` / `when_to_use` / `when_not_to_use` | `summary` / `description` (+ `x-mapi-when-not-to-use`) |
| `effect: read` | método GET/HEAD/QUERY; `x-openai-isConsequential: false`; `x-speakeasy-mcp.scopes: [read]`; `x-mapi-effect: read` |
| `effect: write` | POST/PUT/PATCH; `x-openai-isConsequential: true`; scopes `[write]`; `x-mapi-effect: write` |
| `effect: destroy` | DELETE (ou POST em `:destroy`); `x-openai-isConsequential: true`; scopes `[write, destroy]`; `x-mapi-effect: destroy` |
| `idempotent` | PUT/DELETE/GET implicam; POST/PATCH ⇒ parâmetro `Idempotency-Key` (header, required) + `x-mapi-idempotent: true` |
| `input` | `parameters` (path/query) + `requestBody` (application/json); `confirm` vira **query param `confirm=true`** (não body) para ser visível em log/WAF |
| `output` | `responses.200` = envelope §4 (`components.schemas.MapiEnvelope_<cap>`); `202` para seco; `409` para `refused` |
| `consent` | `x-mapi-consent: {dry_run, confirm, refuses}`; também `responses.202.description: "dry run"` |
| `reversible` | `x-mapi-reversible: {inverse: {operationId, args}}` ou `{irreversible: {reason}}`; **link nativo**: `responses.200.links.inverse` (OpenAPI Link Object apontando para a operação inversa com `parameters` = expressões) |
| `precondition` | `x-mapi-precondition`; e `description` ganha a frase "Requires: …" |
| `proof` | `x-mapi-proof`; **link nativo**: `responses.200.links.proof` para a operação de leitura |
| `budget` | `x-mapi-budget`; `rate` ⇒ `RateLimit-Policy` documentado em `responses.*.headers` |
| `bindings.http.auth` | `security` + `components.securitySchemes` |
| `examples` | `requestBody.content.*.examples` + `responses.*.examples` |
| `version` | `x-mapi-version`; `info.version` do documento = max das capacidades |

Links Objects são o único mecanismo nativo do OpenAPI que relaciona operações
(resposta de A → parâmetros de B); o MAPI os usa para `inverse` e `proof`, e
duplica em `x-mapi-*` porque ferramentas comuns ignoram `links` [memória,
não medido].

## 8. Mapeamento exato para MCP (revisão 2026-07-28 e legada)

| MAPI | MCP `Tool` |
|---|---|
| `bindings.mcp.tool` | `name` |
| `title` | `title` e `annotations.title` |
| `when_to_use` + frases geradas | `description` = `when_to_use` + " Dry run by default: pass confirm=true to execute." (write/destroy) + " NO UNDO: <reason>." (irreversible) + " Requires: <evidence>." (destroy) + `when_not_to_use` |
| `effect: read` | `annotations.readOnlyHint: true`, `destructiveHint: false`, `idempotentHint: true` |
| `effect: write` | `readOnlyHint: false`, `destructiveHint: false`, `idempotentHint: <idempotent>` |
| `effect: destroy` | `readOnlyHint: false`, `destructiveHint: true`, `idempotentHint: <idempotent>` |
| `open_world` | `annotations.openWorldHint` (explícito sempre, porque o default do MCP é `true`) |
| `input` (+ `confirm` injetado como `boolean`, default `false`, com `description` que explica o seco) | `inputSchema` |
| envelope §4 | `outputSchema` + `structuredContent`; `content[0].text` com o JSON serializado (compat.) |
| `refused` | resultado com `isError: true` e `structuredContent.refused` (erro de execução, não de protocolo — o modelo pode se corrigir) |
| `consent.confirm` com cliente que suporta elicitation | `resultType: "input_required"` + `inputRequests.confirm = elicitation/create {mode: form, requestedSchema: {confirm: boolean}}`; na repetição, `inputResponses.confirm.content.confirm == true` executa |
| `budget.max_duration_s` > 60 ou binding assíncrono | handle da extensão `io.modelcontextprotocol/tasks` (polling `tasks/get`) |
| contrato inteiro | `_meta["io.mapi/contract"]` **se** `Tool._meta` for confirmado na spec; senão omitido (ver research §6) |
| `tools/list` | ordem alfabética por `capability` (determinística, cache de prompt); `ttlMs` = 300000; `cacheScope: private` quando há `auth` |
| era legada (2025-03-26…2025-11-25) | mesmo `Tool`; `initialize` servido pelo servidor de referência |

## 9. Mapeamento do esboço inicial

| esboço | MAPI v0.1 |
|---|---|
| `capacidade` | `capability` |
| `efeito` | `effect` (+ `idempotent`, `open_world`) |
| `inversa` | `reversible.inverse` / `reversible.irreversible.reason` |
| `seca_por_padrao` | `consent.dry_run: default` (+ `confirm.parameter`) |
| `custo` | `budget.cost` (+ `max_output_bytes`, `max_duration_s`, `rate`) |
| `quando_usar` | `when_to_use` (+ `when_not_to_use`) |
| `prova{ler, espera}` | `proof{read, expect, within_s}` |
| — (novo) | `precondition.evidence` (a prova **antes** de destruir — a `receita_apagar` mostrou que falta no esboço) |
| — (novo) | `examples` (sem exemplo não há conformidade) |

## 10. Fluxos (campo 6): MAPI não define formato próprio

Um fluxo MAPI **é** um Arazzo 1.1 `workflow` cujos `steps` referenciam
capacidades (`operationId` do OpenAPI gerado). O verificador acrescenta, sem
sintaxe nova:

1. `successCriteria` de cada passo = `proof.expect` da capacidade (se o autor
   não escreveu outro).
2. `onFailure` padrão = `goto` para um workflow `compensate_<id>` **gerado**: as
   inversas dos passos já executados, em ordem reversa (Saga, 1987).
3. `x-mapi-budget` do workflow = soma dos `budget.cost`; passo cujo custo
   acumulado estoura o teto é recusado em tempo de validação (R15).
4. "Agente propõe, avaliador verifica": o modelo gera o Arazzo; `mapi check
   flow.arazzo.yaml` é o avaliador barato e exato — só fluxo que passa roda.
