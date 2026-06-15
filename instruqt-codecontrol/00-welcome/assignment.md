---
slug: welcome
id: 2ckjc8tjodk7
type: challenge
title: Welcome to ToggleWear
teaser: Meet the ToggleWear storefront and get oriented before you start shipping features.
notes:
- type: text
  contents: ToggleWear sells LaunchDarkly-branded apparel. Over the next seven challenges
    you'll use CodeControl to ship new features safely — starting with your first flag
    and ending with a kill switch that can stop a bad release in seconds.
tabs:
- id: e3ply3wjii1o
  title: LaunchDarkly
  type: browser
  hostname: launchdarkly
- id: 9ot4e4j6vvns
  title: ToggleWear
  type: service
  hostname: workstation
  port: 3000
- id: ni65f74hsgjo
  title: Code Editor
  type: service
  hostname: workstation
  port: 8080
difficulty: basic
timelimit: 300
enhanced_loading: null
---

# Welcome

Over the next ~1 hour, you're going to use **LaunchDarkly CodeControl** to ship new features to the **ToggleWear** storefront — a fictional online retailer of LaunchDarkly-branded apparel.

CodeControl gives you runtime control over what's live in production without redeploying. You'll create flags, write targeting rules, run rollouts, run an experiment, and pull a kill switch — all from the LaunchDarkly UI, all without touching a deployment pipeline.

# What you'll do

| # | Challenge |
|---|---|
| 01 | Create your first feature flag and wire it into the app. |
| 02 | Add targeting rules — free and premium users see different things. |
| 03 | Roll a new feature out progressively: 10% → 50% → 100%. |
| 04 | Run an A/B experiment on two storefront headlines. Pick the winner. |
| 05 | Simulate a bad release. Pull the kill switch. Watch it recover. |
| 06 | Quick quiz to consolidate what you've learned. |
| 07 | Wrap up and bridge to AgentControl. |

# The tabs

- **[LaunchDarkly](#tab-0)** — the LD UI where you'll create flags, write rules, and read results.
- **[ToggleWear](#tab-1)** — the live storefront. Changes you make in LD show up here immediately.
- **[Code Editor](#tab-2)** — `server.py` and the frontend. You'll paste a few code blocks here.

Click **Check** when you're ready to start.
