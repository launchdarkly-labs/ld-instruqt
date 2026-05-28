# Track 2 — Evaluate (L2)

Scope pending. Will become a sibling Instruqt track covering AgentControl's evaluation surface: judges, experiments, guarded rollout, and adaptive switching.

Planned challenges (high-level, see `../DECISIONS.md` for the 3-track-split decision):

1. Welcome — recap where Otto is, frame the eval story
2. Golden dataset + offline eval
3. Built-in judges (accuracy + relevance, ~25% sample)
4. Custom brand-voice judge (reuses the L1 `brand-voice` snippet)
5. Custom product-claim judge (catalog as ground truth)
6. Quiz interstitial
7. Prompt experiment on live lab traffic
8. Guarded rollout (lifts the former `07-trust-but-verify` from Build, rewired to consume the brand-voice judge introduced above)
9. Adaptive switching (request-time targeting flip from app-side)
10. Wrap-up

This directory will house `track.yml`, `config.yml`, `track_scripts/`, the per-challenge folders, and `assets/` once scoped.
