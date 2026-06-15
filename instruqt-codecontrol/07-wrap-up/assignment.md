---
slug: wrap-up
id: h243x280iq9n
type: quiz
title: Wrap-Up
teaser: You shipped features safely. Now see how the same ideas apply to AI agents.
notes:
- type: text
  contents: You've completed the CodeControl track. Flags, targeting, rollouts, experiments,
    kill switches — you've used all of them. One last question, then a bridge to what's
    next.
answers:
- AgentControl is a separate product with no overlap with CodeControl — it uses a
  completely different SDK and a separate dashboard.
- AgentControl applies the same runtime-control ideas to AI agents — prompts, models,
  and rollout strategy become flags you control from the LaunchDarkly UI without redeploying.
- AgentControl replaces feature flags for AI-powered applications. Once you adopt it,
  you no longer need CodeControl.
- AgentControl is only for Python applications using AWS Bedrock.
solution:
- 1
difficulty: ""
timelimit: 600
enhanced_loading: null
---

You just used CodeControl to ship a new storefront feature, target it by user tier, roll it out progressively, run an experiment, and pull a kill switch — all without touching a deployment.

ToggleWear is also about to get an AI shopping assistant named Otto. Otto has his own prompts, his own model, his own rollout strategy — and his own runtime control plane.

What does AgentControl add on top of what you just learned?
