# MAPI — pesquisa: estado da arte medido (2026-10-20)

> Convenção deste documento: **[li]** = lido na fonte citada; **[medi]** = contado
> no repo ou na saída de um comando; **[deduzi]** = inferência minha, sem fonte.
> Fatos de memória sem fonte estão marcados **[memória, não conferido]**.

## 0. Veredito antes dos detalhes

A tese tem duas metades, e elas têm destinos diferentes:

1. **O vocabulário** (efeito, idempotência, consentimento) **já existe** em 4 a 6
   padrões vivos, e desde 2025-03 está no próprio MCP como `annotations`
   (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`) [li,
   §1.1]. Um padrão novo que só renomeie isso é o quadro 5 do xkcd 927.
2. **A garantia** — inversa obrigatória, prova pelo estado relido, orçamento no
   contrato, seco por padrão como camada do protocolo, e uma suíte que confere se
   o que o contrato diz é verdade — **não existe em nenhum deles** [li, §1–§4].
   Todos os padrões atuais são *hints*: a spec do MCP diz literalmente que os
   clientes "MUST consider tool annotations to be untrusted unless they come from
   trusted servers" [li, §1.1].

Então: a ideia está **~45% coberta** (campos 1, 4 e 6 da lista inicial têm
cobertura forte ou parcial; 2, 3, 5 e 7 não têm). O que sobra — e é o que vale —
é: **contrato que se verifica**, não contrato que se declara. O risco de
redundância é real e tem nome (§5); a mitigação é estrutural: MAPI não pode ser
um 16º formato, tem de ser um *verificador que lê e escreve os formatos que já
existem* (OpenAPI + extensões `x-`, MCP annotations, Arazzo). Ver `spec-v0.md`.

Prova interna de que a tese tem chão: a casa já escreveu o padrão à mão **duas
vezes**, de jeitos diferentes, e as duas divergem (§4). Isso é exatamente o
sintoma que um compilador resolve.

---

## 1. Padrões vivos e o que cada um já cobre

### 1.1 MCP (Model Context Protocol) — revisão 2026-07-28

- Revisão atual: **2026-07-28**, descrita pelo changelog oficial como a maior da
  história do padrão; a anterior era 2025-11-25 [li:
  https://modelcontextprotocol.io/specification/latest/changelog, lido em
  2026-10-20].
- Mudanças que afetam o desenho do MAPI [li, mesmo changelog]:
  - **Sem estado**: removidos `initialize` e `Mcp-Session-Id` (SEP-2567/2575);
    todo pedido carrega versão e capacidades em `_meta`. Estado entre chamadas é
    *handle* explícito devolvido pela tool ("Stateful Tools", não normativo).
  - **MRTR (Multi Round-Trip Requests, SEP-2322)**: a tool pode devolver
    `resultType: "input_required"` com `inputRequests` (ex.: `elicitation/create`)
    e o cliente repete o pedido com `inputResponses`. **Isso é o canal nativo
    para "confirmar explícito"** — mas a spec não define *quando* uma tool deve
    pedir; fica a critério do servidor.
  - **Tasks** saíram do núcleo para a extensão `io.modelcontextprotocol/tasks`
    (SEP-2663): `tasks/get` (polling), `tasks/update`, `tasks/cancel`; o servidor
    decide quando devolve um handle de task [li: changelog + busca; a página da
    extensão está marcada como *draft*].
  - `resultType` obrigatório em todo resultado; `ttlMs`/`cacheScope` obrigatórios
    em `tools/list`; ordem determinística recomendada para cache de prompt.
  - Deprecados: Roots, Sampling, Logging, HTTP+SSE, Dynamic Client Registration.
- **Tool annotations** (schema.ts da revisão 2026-07-28) [li:
  https://raw.githubusercontent.com/modelcontextprotocol/modelcontextprotocol/main/schema/2026-07-28/schema.ts]:

  | campo | tipo | padrão | significado |
  |---|---|---|---|
  | `title` | string | — | nome humano |
  | `readOnlyHint` | bool | `false` | "não modifica o ambiente" |
  | `destructiveHint` | bool | **`true`** | pode fazer atualizações destrutivas, não só aditivas (só vale se `readOnlyHint=false`) |
  | `idempotentHint` | bool | `false` | repetir com os mesmos args não tem efeito adicional |
  | `openWorldHint` | bool | `true` | interage com mundo aberto (web) vs domínio fechado |

  Só esses cinco. O doc-comment diz que são *hints* que podem não descrever o
  comportamento real, e a página de tools: clientes **MUST** tratá-los como não
  confiáveis salvo servidor confiável [li:
  https://modelcontextprotocol.io/specification/latest/server/tools].
- `outputSchema` + `structuredContent` existem (servidor MUST conformar, cliente
  SHOULD validar) [li, mesma página]. Isso é **forma** da saída, não **estado**
  do mundo depois da chamada.
- O que **não existe** no MCP [li, por ausência nas páginas acima e no
  schema.ts]: custo por chamada, tamanho máximo de saída, inversa/compensação,
  pré-condição (backup antes de destruir), dry-run como semântica, verificação
  do resultado contra o estado.
- **Quem obedece aos hints hoje** (evidência, não opinião):
  - Codex CLI tem um modo "writes" que deixa `readOnlyHint=true` passar sem
    prompt, força prompt em `destructiveHint` e trata tool sem anotação como
    escrita [li: blog de terceiro,
    https://codex.danielvaughan.com/2026/07/24/codex-cli-writes-app-approval-mode-mcp-tool-annotations-read-only-hint-approval-flow/].
  - Claude Code: issue aberta em 2026-08-17 pedindo que o motor de permissão
    processe `ToolAnnotations`; hoje trata toda tool MCP igual [li:
    https://claudeissues.com/issue/87452-feature-permission-engine-should-process-mcp-toolannotations-hints-readonlyhint].
  - Conclusão [deduzi]: os hints são lidos de forma desigual e sem verificação;
    um contrato *verificado* teria um cliente consumidor imediato (Codex) e um
    buraco a preencher (Claude Code).
- Governança: doado por Anthropic à **Agentic AI Foundation (AAIF)**, fundo
  dirigido da Linux Foundation, em 2025-12-09, com OpenAI (AGENTS.md) e Block
  (goose) como cofundadores; maintainers e processo (SEPs) continuam [li:
  https://itbrief.co.uk/story/anthropic-donates-mcp-to-new-agentic-ai-foundation,
  https://opensourceforu.com/2025/12/anthropic-openai-block-move-agentic-ai-infrastructure-to-open-source-governance-under-linux-foundation/].
  A revisão 2026-07-28 formalizou SEPs em PR e uma política de ciclo de vida
  com janela mínima de 12 meses de deprecação [li: changelog].

### 1.2 OpenAPI 3.2 / 3.3, Arazzo 1.1, Overlay 1.0 — OpenAPI Initiative (Linux Foundation)

- **OpenAPI 3.2.0**: 2025-09-19 [li: Wikipedia + Speakeasy release notes; a página
  de anúncio em openapis.org não carregou na minha leitura]. Novidades citadas:
  tags estruturadas, streaming, métodos HTTP arbitrários (`QUERY`), OAuth2
  device flow. **Nada sobre efeito colateral além da semântica do método HTTP**
  (GET seguro, PUT/DELETE idempotentes por RFC 9110) [memória: RFC 9110 §9.2.1–2,
  não conferido hoje].
- **OpenAPI 3.3** (em planejamento): o blog da OAI diz que o foco é Security
  Schemes e "maior integração com MCP e protocolos de IA"; a newsletter de
  2026-06-09 investiga "Standardized API Features (SAFs)" — marcar
  comportamentos definidos por spec externa (RFC) [li:
  https://www.openapis.org/blog/2025/12/04/openapi-initiative-newsletter-december-2025,
  https://www.openapis.org/blog/2026/06/09/openapi-initiative-newsletter-june-2026].
  **Implicação**: a OAI está abrindo exatamente a porta por onde um vocabulário
  MAPI entraria como extensão/SAF, em vez de padrão rival.
- **Arazzo 1.1.0**, 2026-05-17 [li: https://spec.openapis.org/arazzo/latest.html].
  Workflows sobre OpenAPI *e* AsyncAPI. O `Step Object` tem **`successCriteria`**
  (lista de `Criterion`: `context` + `condition` + `type` ∈ simple|regex|jsonpath|xpath),
  `onSuccess`, `onFailure` (`end|retry|goto`, `retryAfter`, `retryLimit`),
  `outputs`, `dependsOn`, `timeout`. **Não define** compensação, undo, rollback,
  custo, idempotência nem classificação de efeito; e diz explicitamente que não
  modela confirmação de entrega em AsyncAPI [li, mesma página]. Logo:
  - `successCriteria` é o parente mais próximo de `prova.espera` — mas avalia a
    **resposta** do passo, não uma **releitura independente** do estado.
  - Composição de fluxos (campo 6) **já tem formato**: MAPI deve
    emitir Arazzo, não inventar outro.
- **Overlay 1.0.0**, 2024-10-22: arquivo separado que aplica atualizações
  (add/overwrite/remove) a uma descrição OpenAPI sem editar o original [li:
  https://spec.openapis.org/overlay/v1.0.0]. **Isso é o veículo natural do
  importador OpenAPI→MAPI**: o que o MAPI acrescenta pode viver como overlay
  sobre o OpenAPI de alguém, sem fork do arquivo dele.
- Governança: OAI é projeto da Linux Foundation desde 2015-11 (Swagger doado pela
  SmartBear) [li: https://en.wikipedia.org/wiki/OpenAPI_Specification,
  https://nordicapis.com/whats-the-difference-between-swagger-and-openapi/].

### 1.3 Smithy 2.0 (AWS)

Traits de comportamento: `readonly` (efetivamente só leitura, logo idempotente),
`idempotent`, `idempotencyToken` (membro de entrada usado para descartar replay),
`retryable`, `paginated`, `longPoll` (instável), `requestCompression` [li:
https://smithy.io/2.0/spec/behavior-traits.html]. É o vocabulário de efeito
mais maduro que existe em IDL — mas é declaração, sem verificação, sem inversa,
sem custo, sem prova.

### 1.4 Protobuf / gRPC

`MethodOptions.idempotency_level` ∈ {`IDEMPOTENCY_UNKNOWN`=0, `NO_SIDE_EFFECTS`=1
(implica idempotente), `IDEMPOTENT`=2 (pode ter efeito)}; implementações HTTP
podem mapear para GET/PUT [li:
https://protobuf.dev/reference/java/api-docs/com/google/protobuf/DescriptorProtos.MethodOptions.IdempotencyLevel.html].
Prova de que "efeito + idempotência" é ideia de 2016 [memória: o campo entrou no
proto3 por volta de 2016, não conferido].

### 1.5 TypeSpec (Microsoft)

Decoradores HTTP (`@get`, `@put`, `@delete`…); o emissor infere o verbo pelo
nome/assinatura [li: https://typespec.io/docs/libraries/http/reference/decorators/,
https://typespec.io/docs/emitters/openapi3/openapi/]. Não achei decorador de
efeito, idempotência ou segurança além do verbo. TypeSpec é **linguagem que
emite OpenAPI** — modelo mental igual ao do MAPI (fonte única → vários alvos),
útil como referência de arquitetura, não como concorrente de vocabulário.

### 1.6 A2A 1.0 (Google → Linux Foundation → AAIF)

Versão 1.0.0 (2026-03, segundo cobertura) [li: https://a2a-protocol.org/latest/specification/
mostra 1.0.0 como última]. Entrou na AAIF em 2026-08-17 [li:
https://aaif.io/blog/a2a-joins-aaif]. O Agent Card descreve identidade,
capacidades (`streaming`, `pushNotifications`, `extendedAgentCard`), skills,
`securitySchemes`. Idempotência só por operação (`messageId` para dedupe); **sem**
efeito declarado por skill, custo, undo ou verificação de resultado [li, spec,
primeiros 100 k chars; o restante não lido].

### 1.7 GraphQL, JSON-RPC, AsyncAPI — resumo

- GraphQL: `query` vs `mutation` é a única classificação de efeito, sem
  idempotência; **custo** existe como diretiva `@cost(weight)`/`@listSize` (spec
  IBM, implementada no Apollo Router ≥ 1.53 e no Hive Gateway) [li:
  https://www.apollographql.com/docs/graphos/routing/security/demand-control].
  É o único padrão de API vivo com orçamento no contrato — mas é custo de
  *consulta* (profundidade/listas), não custo monetário por chamada.
- JSON-RPC 2.0: nada sobre efeito [memória, trivial].
- AsyncAPI: mensagens/canais; Arazzo 1.1 já a cobre em fluxos [li, §1.2]. Não
  aprofundei: não é onde mora o problema.

### 1.8 Sinais do ecossistema HTTP/OpenAI que já carregam pedaços do MAPI

- `x-openai-isConsequential` (GPT Actions): operação `true` sempre pede
  confirmação e não mostra "always allow"; `false` mostra; padrão: GET=false,
  resto=true [li: threads da comunidade OpenAI que citam a doc oficial,
  https://community.openai.com/t/how-to-stop-custom-gpt-displaying-confirm-deny-buttons/874551;
  a página oficial não foi lida]. **É consentimento no contrato, já em produção
  desde 2023** [memória para a data].
- `x-speakeasy-mcp` (operação): `disabled`, `name`, `scopes` (read/write/…),
  `description` para o modelo; aplicável por Overlay [li:
  https://www.speakeasy.com/blog/generating-mcp-from-openapi-lessons-from-50-production-servers,
  2025-06-24]. É o importador OpenAPI→MCP com curadoria — sem efeito verificado,
  sem inversa, sem prova.
- IETF httpapi: `Idempotency-Key` (draft-07, 2025-10-15, expirado em
  2026-04-18 sem RFC) e `RateLimit`/`RateLimit-Policy` (draft-11, 2026-05, ativo)
  [li: https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/,
  https://www.ietf.org/archive/id/draft-ietf-httpapi-ratelimit-headers-11.html].
  Idempotência por token e orçamento por cabeçalho são *runtime*, não contrato.
- Compensação: Sagas (Garcia-Molina & Salem, SIGMOD 1987) [li:
  https://www.cs.princeton.edu/research/techreps/598]; BPEL/WS-BA/WS-CAF em
  orquestração [li parcial: Wikipedia "Long-running transaction"; BPEL não
  conferido]. **A inversa é ideia de 40 anos em orquestradores e zero anos em
  contratos de API.** Esse é o vazio mais claro.

---

## 2. Geradores OpenAPI→MCP e por que as tools saem ruins (evidência)

- **Estudo empírico** (Mastouri, Ksontini, Barrak, Kessentini, arXiv:2507.16044,
  v4 2026-04-06): 116 servidores MCP oficiais + 80 contratos OpenAPI reais.
  **88,6 %** dos servidores são total ou parcialmente REST por baixo; **92 %**
  implementam tools como "bare API wrappers"; os servidores expõem **mediana de
  19 %** das operações da API; geração automática funciona em **76 %** das tools
  e sobe para **94,2 %** com reparo automático da spec; filtrar e reagrupar
  reduz a contagem de tools por API em um terço [li:
  https://arxiv.org/abs/2507.16044].
  Leitura [deduzi]: o problema não é gerar código, é **decidir o que expor e
  como descrever** — e isso é o que um contrato com `quando_usar`, efeito e
  orçamento força a escrever.
- **Speakeasy, 50+ servidores em produção** (2025-06-24): "tool explosion"
  (200 endpoints → ~200 tools; GitHub > 500), descrições humanas vagas ("Fetches
  user details" em três endpoints), custo de tokens das descrições, payloads
  com envelope `{result}` que confundem o modelo, exposição irrestrita (uma
  chamada vaza ou altera); resposta deles: `x-speakeasy-mcp` + scopes
  read/write por método [li, URL em §1.8].
- Prior art de "tool count": afirmação de queda de acerto acima de ~25–50 tools
  aparece em vários blogs **sem estudo citado** — trato como folclore até medir
  [li: resumo de busca; nenhum número com fonte primária].
- **Medido nesta casa**: o Factory MCP tem **79 tools** num servidor só [medi:
  `ast` em (código privado)]; o registro da Genesis limita a descrição a **300
  caracteres** porque "o construtor de GPT avisa e corta descrição de operação
  acima de 300" [li: (arquivo do repo privado)]. Limite real do
  ecossistema para `quando_usar`.

---

## 3. Casos históricos de adoção (para calibrar a cunha)

- **Swagger → OpenAPI (2015)**: venceu por doação à Linux Foundation com SmartBear,
  Google, IBM, Microsoft etc.; a spec 2.0 foi "semanticamente idêntica" ao
  Swagger 2.0 — **venceu o formato que já tinha a base instalada**, não o mais
  elegante [li: Wikipedia; nordicapis]. RAML e API Blueprint perderam mesmo sendo
  mais expressivos; os dois acabaram "entrando" na OAI [memória, não conferido:
  MuleSoft entrou na OAI em 2017; Apiary foi comprada pela Oracle em 2017].
- **MCP (2024-11 → 2025-12)**: venceu por (a) SDKs em todas as linguagens no
  dia 1, (b) adoção pelos clientes (Claude, Cursor, Codex, ChatGPT), (c) doação a
  fundação neutra quando já tinha >10 mil servidores públicos [li: itbrief].
  Padrão de agente vence por **cliente que o consome**, não por spec.
- **xkcd 927** ("Standards", 2011): "14 competing standards → one universal
  standard → 15 competing standards" [li: https://xkcd.com/927/]. Risco
  literal aqui: MCP + OpenAPI + Arazzo + Smithy + TypeSpec + A2A + x-openai +
  x-speakeasy = 8 vocabulários de capacidade; o MAPI seria o 9º **se tiver
  sintaxe própria sem compilar para os outros**.
- Lição comum [deduzi]: os que venceram **absorveram** a base instalada (Swagger
  2.0 = OpenAPI 2.0) ou **foram consumidos** por cliente dominante (MCP). Um
  padrão novo em 2026 só entra se (1) lê o que já existe sem edição (Overlay),
  (2) escreve o que os clientes já leem (annotations, `x-openai-isConsequential`,
  scopes) e (3) oferece algo que nenhum deles oferece: verificação.

---

## 5. Tabela-veredito: os 7 campos

| # | campo | já existe em | o que falta (= o que o MAPI acrescenta) | novo? |
|---|---|---|---|---|
| 1 | efeito (leitura/escrita/destrutivo) + idempotência | MCP annotations (5 hints), Smithy `readonly`/`idempotent`, protobuf `idempotency_level`, HTTP (RFC 9110), `x-openai-isConsequential`, `x-speakeasy-mcp.scopes`, GraphQL query/mutation | tudo é *hint* não verificado; `destructiveHint` tem padrão `true` (ruído); nenhum cliente confere | **não** (≈90 % coberto); o novo é *verificar* |
| 2 | inversa obrigatória em toda escrita | nenhum contrato de API; só orquestração (Sagas 1987, BPEL/WS-BA) e `volta` em texto na casa | campo tipado + compilador que recusa escrita sem inversa ou sem `irreversible.reason` | **sim** |
| 3 | prova: avaliador do estado depois | Arazzo `successCriteria` (sobre a resposta), MCP `outputSchema` (forma), `confirmado_pelo_estado` na casa (2 módulos) | releitura **independente** (`read` + `expect` + janela) como parte do contrato, emitida como teste e como `successCriteria` | **sim** (Arazzo cobre ~30 %) |
| 4 | consentimento: seco por padrão, confirmar explícito | MCP MRTR/elicitation (canal), `x-openai-isConsequential`, Codex writes mode, `confirmar=True` em 32 tools da casa | **dry-run como semântica de protocolo** (toda escrita responde `faria` sem `confirm`); a spec do MCP só diz "SHOULD have a human in the loop" | parcial (≈50 %) |
| 5 | orçamento: custo por chamada e saída máxima | GraphQL `@cost` (custo de consulta), `RateLimit` headers (runtime), MCP `ttlMs` (cache, não custo) | custo monetário/unitário e `max_output_bytes` no contrato, somáveis por fluxo | **sim** (≈20 % coberto) |
| 6 | composição determinística de fluxos | **Arazzo 1.1** (workflows, `successCriteria`, `onFailure`, `dependsOn`) | compensação automática (inversas em ordem reversa), soma de orçamento, recusa de fluxo com escrita sem inversa — **como validador sobre Arazzo**, não como formato novo | parcial (≈70 %); emitir Arazzo |
| 7 | conformance suite: só é MAPI quem passa | MCP tem testes de protocolo [memória, não conferido: repo `conformance`]; OpenAPI tem validadores de **forma**; a casa tem 60+ testes à mão | testes **gerados do contrato** que provam que `effect`, `inverse`, `proof` e `budget` são verdade contra um servidor real/fake | **sim** |

Soma honesta: **3 campos novos de verdade (2, 3, 7), 2 parciais (4, 5), 2
cobertos (1, 6).** A frase que resume: *o MAPI não é um vocabulário novo; é a
diferença entre `destructiveHint: false` e um teste que falha quando isso é
mentira.*

## 6. Riscos de pesquisa (o que eu não consegui confirmar)

- Página oficial de `x-openai-isConsequential` não lida (só threads que a citam).
- Conformance repo do MCP: não conferido.
- Datas de RAML/MuleSoft/Apiary: memória.
- Resto da spec A2A (156 k chars) não lido: pode haver campo de efeito em
  `AgentSkill` que eu não vi.
- `_meta` em objetos `Tool` do MCP para carregar o contrato inteiro: vi `_meta`
  em `Result`/requests; em `Tool` não confirmei — o compilador deve usar
  `annotations` nativas + descrição e tratar `_meta` como opcional até conferir.
