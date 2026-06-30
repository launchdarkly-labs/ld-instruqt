---
slug: target-by-tier
id: ckxhf2uxssi4
type: challenge
title: Target by User Tier
teaser: Create a segment for premium members and use it to show them something free users don't see.
notes:
- type: text
  contents: A boolean flag that's on for everyone is useful. A flag that evaluates
    differently per user is powerful. You'll create a reusable segment that defines
    who a premium member is, then target a flag at that segment — so the same group
    can be reused across as many flags as you need.
tabs:
- id: prle2r134nll
  title: LaunchDarkly
  type: browser
  hostname: launchdarkly
- id: pbazehorh56d
  title: ToggleWear
  type: service
  hostname: workstation
  port: 3000
- id: mraku7bfcetz
  title: Code Editor
  type: service
  hostname: workstation
  port: 8080
difficulty: basic
timelimit: 900
enhanced_loading: null
---

# Create a segment

A segment is a reusable group of users defined by rules. You'll create one called "Premium Members" — any user whose `tier` attribute equals `premium`.

Open [LaunchDarkly](#tab-0).

<!-- VERIFY: Confirm exact navigation path to Segments in the current LD UI -->
1. In the left sidebar, click **Segments** under **CodeControl**.
2. Click **Create segment**.
3. For **Name**, enter:
```text
Premium Members
```
4. For **Key**, confirm or enter:
```text
premium-members
```
5. Click **Create segment**.
6. On the segment detail page, click **Add rule**.
7. Set the rule to: `tier` **is one of** `premium`.
8. Click **Review and save** → **Save changes**.

Any user the app sends with `tier = "premium"` in their context now belongs to this segment automatically — no manual list required.

# Create the flag

<!-- VERIFY: Confirm exact navigation path to Feature Flags -->
1. In the left sidebar, click **Feature Flags** under **CodeControl**.
2. Click **Create flag**.
3. For **Name**, enter:
```text
Premium Banner
```
4. For **Key**, confirm or enter:
```text
premium-banner
```
5. For **Flag type**, select **Boolean**.
6. Click **Create flag**.

# Add a segment targeting rule

<!-- VERIFY: Confirm exact UI steps for adding a segment targeting rule -->
1. Click the **Targeting** tab on the `premium-banner` flag.
2. Make sure the environment selector reads **Production**.
3. Toggle the flag **On**.
4. Under **Targeting rules**, click **Add rule**.
5. Set the rule to: **If user is in segment** `Premium Members` **serve** `true`.
6. Under **Default rule**, confirm it serves `false`.
7. Click **Review and save** → **Save changes**.

Because you're targeting a segment — not a raw attribute — you can reuse **Premium Members** on any future flag without rewriting the rule.

# Wire it into the app

Open [Code Editor](#tab-2) and open `server.py`. Find this line:

```python
        "new_arrivals_enabled": ld_client.variation("new-arrivals-enabled", context, False),
```

Add the following line **immediately after** it:

```python
        "premium_banner_enabled": ld_client.variation("premium-banner", context, False),
```

Save the file. The ToggleWear service auto-reloads.

# See targeting in action

Open [ToggleWear](#tab-1). The tier dropdown is in the top-right corner.

1. With **Free user** selected — the **Members Only** banner should be hidden.
2. Switch to **Premium user** — the banner appears instantly.
3. Switch back to **Free user** — it disappears.

LaunchDarkly evaluated the `premium-banner` flag for each context, matched the `tier` attribute against the **Premium Members** segment rule, and returned the right variation each time — no page reload required.

Click **Check** when you can see the banner appear and disappear as you switch tiers.
