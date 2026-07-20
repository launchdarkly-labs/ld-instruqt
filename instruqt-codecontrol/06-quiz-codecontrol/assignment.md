---
slug: quiz-codecontrol
id: dsexlcgdogxl
type: quiz
title: Quiz — CodeControl
teaser: A quick check on flags, targeting, rollouts, and experiments.
notes:
- type: text
  contents: You've created flags, written targeting rules, run a rollout, run an experiment,
    and pulled a kill switch. One question before the wrap-up.
answers:
- Flags are evaluated at deploy time, so the variation is baked into the binary.
- Flags are evaluated at runtime on every request, so a targeting change in the UI
  takes effect immediately without redeploying.
- The SDK polls the LaunchDarkly API every 60 seconds, so changes take up to a minute.
- Flag targeting is client-side only — server-side SDKs always return the default
  variation.
solution:
- 1
difficulty: ""
timelimit: 600
enhanced_loading: null
---

You changed a flag's targeting rules in the LaunchDarkly UI and the ToggleWear storefront updated within seconds — without restarting the server or running a deployment.

Why did that happen so quickly?
