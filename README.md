# MAPI

**One contract for a capability — readable by programs (API), agents (MCP) and auditors.**
**Um contrato para uma capacidade — legível por programas (API), agentes (MCP) e auditores.**

> Status: **draft v0.1 (design phase)**. There is a spec and hand-written examples.
> There is **no compiler yet**. Nothing here is a finished standard.
> Estado: **rascunho v0.1 (fase de desenho)**: spec e exemplos escritos à mão, ainda sem compilador.

## The idea

OpenAPI describes what a program can call. MCP describes what an agent can call.
Both stop at *"what can I call"*. Neither says what happens next: whether it changes
state, how to undo it, what it costs, who had to consent, and **how to prove it worked**.

MAPI is a thin layer **on top of** OpenAPI and MCP — it does not compete with them, it
compiles to both. An operation declares:

| field | meaning |
|---|---|
| `effect` | read / write / destroy (+ idempotency) |
| `reversible` | the inverse operation — **required** for writes, or an explicit `irreversible.reason` |
| `proof` | an independent re-read of the *state* after the call ("sent" is not "delivered") |
| `precondition.evidence` | for destructive ops: proof that it can be rebuilt, checked **before** destroying |
| `consent` | dry-run by default; explicit confirm to act |
| `budget` | cost per call, max output size, max duration |
| conformance | a suite generated from the contract: only what passes is "MAPI" |

## Honest status of the idea

Our own survey ([docs/research.md](docs/research.md)) estimates ~45% of this is already
covered elsewhere (effect/idempotency hints in MCP and Smithy, flows in Arazzo).
What we found genuinely missing in current standards: mandatory inverse, state-based
proof, evidence-before-destroy and behavioural conformance. If you know prior art for
those, please open an issue — that is the most useful contribution right now.

## Layout

- [SPEC.md](SPEC.md) — data model, refusal rules (R1–R15), mapping to OpenAPI and MCP.
- [examples/](examples/) — three contracts (`*.mapi.yaml`) with the OpenAPI and MCP
  tool schemas a compiler should emit from each (`*.openapi.yaml`, `*.mcp.json`).
- [docs/research.md](docs/research.md) — state of the art, with sources and dates.

## Roadmap

1. Meta-schema (`mapi-0.1.schema.json`) and a reference compiler (parse → check → emit).
2. OpenAPI → MAPI importer that pre-fills the new fields and flags what needs a human.
3. Conformance suite.

## License

Apache-2.0 — see [LICENSE](LICENSE).
