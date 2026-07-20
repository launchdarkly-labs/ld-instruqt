---
slug: progressive-rollout
id: sbdrdct1vvxy
type: challenge
title: Progressive Rollout
teaser: Roll a new layout out to 0%, then 50%, then 100% — without redeploying.
notes:
- type: text
  contents: Shipping to 100% of users at once is a gamble. A progressive rollout lets
    you expose a feature to an increasing slice of your user base and pull back the
    moment something looks wrong. LaunchDarkly uses the context key to bucket users
    consistently — the same user always lands in the same bucket for the duration
    of the rollout.
tabs:
- id: nwz6ndytqmsq
  title: LaunchDarkly
  type: browser
  hostname: launchdarkly
- id: kprcoox5sahu
  title: ToggleWear
  type: service
  hostname: workstation
  port: 3000
- id: zaosvxwuspkt
  title: Code Editor
  type: service
  hostname: workstation
  port: 8080
difficulty: basic
timelimit: 900
enhanced_loading: null
---

# Create the flag

Open [LaunchDarkly](#tab-0).

<!-- VERIFY: Confirm exact navigation path to Feature Flags -->
1. In the left sidebar, click **Feature Flags** under **CodeControl**.
2. Click **Create flag**.
3. For **Name**, enter:
```text
New Product Layout
```
4. For **Key**, confirm or enter:
```text
new-product-layout
```
5. For **Flag type**, select **Boolean**.
6. Click **Create flag**.

# Set up the rollout

<!-- VERIFY: Confirm exact UI steps for configuring a percentage rollout -->
1. Click the **Targeting** tab on the `new-product-layout` flag.
2. Make sure the environment selector reads **Production**.
3. Toggle the flag **On**.
4. Under **Default rule**, click the variation dropdown and select **Percentage rollout**.
5. Set the rollout to **0%** true / **100%** false.
6. Click **Review and save** → **Save changes**.

The flag is on, but 0% of users will see the new layout. That's the starting state of any progressive rollout.

# Wire it into the app

Open [Code Editor](#tab-2) and open `server.py`. Find this line:

```python
        "premium_banner_enabled": ld_client.variation("premium-banner", context, False),
```

Add the following line **immediately after** it:

```python
        "new_layout_enabled": ld_client.variation("new-product-layout", context, False),
```

Save the file. The ToggleWear service auto-reloads.

# Watch the rollout expand

Open [ToggleWear](#tab-1). At 0%, the sort bar above the product grid is hidden — reload the page a few times to confirm it never appears.

Now expand the rollout:

1. Back in [LaunchDarkly](#tab-0), open the `new-product-layout` flag → **Targeting** tab.
2. Change the rollout to **50%** true / **50%** false.
3. Click **Review and save** → **Save changes**.
4. Open [ToggleWear](#tab-1) and reload the page a few times. Roughly half the sessions should see the sort bar.

Now roll out to everyone:

1. Change the rollout to **100%** true.
2. Save. Reload [ToggleWear](#tab-1) — the sort bar should appear on every reload.

When you're ready to check, make sure the rollout is above 0%.

Click **Check**.
