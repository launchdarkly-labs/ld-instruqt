---
slug: quick-takes
id: ybyy5xvmu261
type: challenge
title: Quick Takes from a Built-in Judge
teaser: Attach AgentControl's built-in judges to Otto and watch scores populate
  the monitoring view in near real time.
notes:
- type: text
  contents: Offline evaluation graded Otto against a curated dataset. That's
    useful before shipping, but you also want continuous quality signal in
    production. Built-in judges fill that role — they're pre-configured LLM
    judges you can attach to any completion-mode variation in 30 seconds,
    no code changes required.
tabs:
- id: m05u22ozg5sm
  title: LaunchDarkly
  type: browser
  hostname: launchdarkly
- id: vbrj53q6f5gs
  title: ToggleWear
  type: service
  hostname: workstation
  port: 3000
- id: ehs2dt4vqm5d
  title: Code Editor
  type: service
  hostname: workstation
  port: 8080
difficulty: basic
timelimit: 600
enhanced_loading: null
---

# What built-in judges are

AgentControl ships three pre-configured LLM-as-a-judge evaluators that you can attach to a completion-mode variation in a couple of clicks:

| Judge | What it scores |
|---|---|
| **Accuracy** | Whether the response is correct and grounded |
| **Relevance** | Whether the response addresses the user's request |
| **Toxicity** | Whether the response contains harmful or unsafe phrasing (lower = safer) |

When a judge is attached, the SDK fires it automatically against a configurable percentage of Otto's responses. The scores show up as metrics in the monitoring view, ready to drive dashboards, alerts, or — in a couple of challenges — guarded rollouts.

A low-rate stream of chat traffic is already flowing in the background, so by the time you finish attaching the judges, scores will be visible.

# Attach the judges

Open the [LaunchDarkly](#tab-0) tab.

1. Go to **Configs** → **Otto Assistant** → **Otto v1 (Born)**.
<!-- VERIFY: confirm the variation drilldown path; the UI may surface variations on a tab rather than a separate page. -->
2. Scroll to the **Judges** section and click **Attach judges**.
<!-- VERIFY: section name and button label. -->
3. Select all three built-ins: **Accuracy**, **Relevance**, and **Toxicity**.
4. Set the sampling rate for each to **25%**.
<!-- VERIFY: confirm sampling is a percentage slider per judge. -->
5. Click **Save**.

# Watch the scores

The background traffic generator is sending Otto ~20 questions per minute. At 25% sampling, each judge fires roughly 5 times a minute — fast enough that within a couple of minutes the monitoring view has visible data.

1. Click the **Monitoring** tab.
<!-- VERIFY: tab name. -->
2. From the metric dropdown, select **Evaluator metrics**.
<!-- VERIFY: dropdown label and where evaluator metrics live in the dropdown. -->
3. You should see three lines start to populate — one per judge — over the last few minutes.

Give it a minute or two if scores haven't appeared yet. The first scores typically land within 60-90 seconds of attaching the judges.

# Read what you see

A few questions to sit with:

- Which judge has the **highest** score on average? Which the lowest? Why might that be — what does Otto's current prompt do well, and where might it be slipping?
- Toxicity is a **safety** signal, not a quality one. A toxicity score of ~1.0 (with `isInverted` accounting) means Otto is clean. Is he?
- Accuracy and Relevance are correlated but not identical. Where might they diverge — what would a response that's relevant but inaccurate look like?

You won't fix anything in this challenge — observation is the point. The next two challenges write **custom** judges for the brand-voice and product-claim signals that the built-ins don't cover.

Click **Check** when at least one built-in is attached to Otto v1 (Born).
