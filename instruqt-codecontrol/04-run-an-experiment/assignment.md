---
slug: run-an-experiment
id: 0aryqthrsefg
type: challenge
title: Run an Experiment
teaser: A/B test two hero headlines. Let the data pick the winner.
notes:
- type: text
  contents: Not every product decision is obvious. Experimentation lets you test a
    hypothesis with real users and real data before committing. You'll set up an A/B
    test on two versions of the ToggleWear hero headline, define a metric, let traffic
    flow, and promote the winner.
tabs:
- id: g1xnaujwh800
  title: LaunchDarkly
  type: browser
  hostname: launchdarkly
- id: gjoqhw7tx2ct
  title: ToggleWear
  type: service
  hostname: workstation
  port: 3000
- id: a6dftbf0vwhb
  title: Code Editor
  type: service
  hostname: workstation
  port: 8080
difficulty: basic
timelimit: 1200
enhanced_loading: null
---

# Create the flag

So far you've created boolean flags — on or off. This time you'll create a **string** flag with two text variations, so LaunchDarkly can serve different headlines to different users.

Open [LaunchDarkly](#tab-0).

<!-- VERIFY: Confirm the exact flow for creating a string multivariate flag in the current LD UI -->
1. In the left sidebar, click **Feature Flags** under **CodeControl**.
2. Click **Create flag**.
3. For **Name**, enter:
```text
Hero Headline
```
4. For **Key**, confirm or enter:
```text
hero-headline
```
5. For **Flag type**, select **String**.
6. Set the first variation's **Value** to:
```text
Wear your features on your sleeve.
```
7. Set the first variation's **Name** to `Control`.
8. Set the second variation's **Value** to:
```text
Ship fast. Look good.
```
9. Set the second variation's **Name** to `Treatment`.
10. Click **Create flag**.

# Wire it into the app

Open [Code Editor](#tab-2) and open `server.py`. You need to make two changes.

**Step 1 — Add the headline to the features endpoint.**

Find this line (it may be the last line in the `return` dict inside `api_features`):

```python
        "new_layout_enabled": ld_client.variation("new-product-layout", context, False),
```

Add the following line **immediately after** it:

```python
        "hero_headline": ld_client.variation("hero-headline", context, "Wear your features on your sleeve."),
```

Unlike the boolean flags, this `variation()` call returns a **string** — the headline text. The third argument is the default if the SDK can't reach LaunchDarkly.

**Step 2 — Wire click tracking.**

Find the block marked:

```python
# ─────────────────────────────────────────────────────────────────────
# CodeControl Challenge 04 paste block — replace this stub with event tracking.
```

Replace **everything between the opening marker and the** `# ─── End CodeControl Challenge 04 paste block` **line** with:

```python
    context = Context.builder(session_id).kind("user").build()
    ld_client.track(event_key, context)
    return {"ok": True}
```

This endpoint receives a custom event name and sends it to LaunchDarkly so Experimentation can count it.

Save the file (⌘ S / Ctrl S). The ToggleWear service auto-reloads.

# Create a metric

Back in [LaunchDarkly](#tab-0).

<!-- VERIFY: Confirm exact UI navigation path for creating a metric in the current LD UI -->
1. In the left sidebar, click **Experimentation**, then **Metrics**.
2. Click **Create metric**.
3. For **Event kind**, select **Custom**.
4. For **Event key**, enter:
```text
product-click
```
5. For **Name**, enter:
```text
Product Click
```
6. For **Success criteria**, choose **Higher than baseline** (more clicks = better headline).
7. For **Randomization unit**, select **user**.
8. Click **Save metric**.

This metric counts every `product-click` event the SDK receives. The storefront already sends one each time a visitor clicks a product card.

# Create an experiment

<!-- VERIFY: Confirm exact UI flow for creating an experiment in the current LD UI -->
1. Click **Experimentation** → **Experiments** in the left sidebar.
2. Click **Create experiment**.
3. For **Name**, enter:
```text
Hero Headline Test
```
4. Select the **hero-headline** flag.
5. Add the **Product Click** metric.
6. Configure two treatments:
   - **Control** — the first variation ("Wear your features on your sleeve.") at **50%**.
   - **Treatment** — the second variation ("Ship fast. Look good.") at **50%**.
7. Click **Create** (or **Save**), then **Start** the experiment.

# Generate some clicks

Open [ToggleWear](#tab-1). You should see one of the two headlines in the hero section — which one depends on how LaunchDarkly bucketed your session.

Click a few product cards. Each click sends a `product-click` event to LaunchDarkly through the `/api/track` endpoint you just wired.

Reload the page a few times (or open in an incognito window) to land in the other variation and click some products there too.

# View results

Back in [LaunchDarkly](#tab-0), open the **Hero Headline Test** experiment. You should see events starting to flow in. In a real deployment with thousands of users, you'd wait for statistical significance before declaring a winner. For this lab, seeing the events arrive is enough.

Click **Check** when the flag, metric, and code changes are in place.
