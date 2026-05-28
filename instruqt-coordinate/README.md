# Track 3 — Coordinate (L3)

Scope pending — requires a Phase 0 spike to confirm agent-mode + agent-graph surfaces are stable enough to lab against.

Will become a sibling Instruqt track covering the multi-agent surface of AgentControl. Otto's character survives — he becomes the brand-voice rewriter inside a team called the **Concierge**.

**Cast (see `../DECISIONS.md` and `../NARRATIVE.md` for naming rationale):**

- **Toggle** — triage agent. Greets the customer, routes to the right specialist.
- **Curator** — product-knowledge specialist
- **Tailor** — sizing specialist
- **Tracker** — order-status specialist
- **Otto** — brand-voice rewriter. Every response passes through him before reaching the customer.

**Topology:** `Toggle → (Curator | Tailor | Tracker) → Otto → customer`

Planned challenges (high-level):

1. Welcome — frame mode-permanence, meet the Concierge team
2. Build Toggle in agent mode (first agent-mode Config; concretely demonstrates mode-permanence)
3. Add the Curator (first specialist + first handoff JSON)
4. Add the Tailor and Tracker
5. Otto returns as the brand-voice rewriter
6. Build the graph in the UI (topology + edges)
7. Wire the SDK (`reverse_traverse` + `graph_key`)
8. Quiz interstitial
9. Per-agent guarded rollout on Otto-the-rewriter
10. Self-healing (synchronous judge + Haiku 4.5 fallback)
11. Wrap-up

This directory will house `track.yml`, `config.yml`, `track_scripts/`, the per-challenge folders, and `assets/` once scoped.
