---
slug: first-flag
id: oncldha6pfpc
type: challenge
title: Your First Feature Flag
teaser: Create a boolean flag, wire it into the app, and flip it on without redeploying.
notes:
- type: text
  contents: The ToggleWear storefront is about to get a "New Arrivals" banner. Instead
    of shipping it live to everyone, you'll put it behind a feature flag — so you
    can turn it on and off from the LaunchDarkly UI without touching the code or running
    a deployment.
tabs:
- id: z7j89p52ljh2
  title: LaunchDarkly
  type: browser
  hostname: launchdarkly
- id: b8tmbrbhrrgf
  title: ToggleWear
  type: service
  hostname: workstation
  port: 3000
- id: ysnajh9xcabx
  title: Code Editor
  type: service
  hostname: workstation
  port: 8080
difficulty: basic
timelimit: 900
enhanced_loading: null
---

# Create the flag

Open the [LaunchDarkly](#tab-0) tab.

<!-- VERIFY: Confirm the exact navigation path to Feature Flags in the current LD UI -->
1. In the left sidebar, click **Feature Flags** under the **CodeControl** section.
2. Click **Create flag** in the upper right.
3. For **Name**, enter:
```text
New Arrivals Enabled
```
4. For **Key**, confirm or enter:
```text
new-arrivals-enabled
```
5. For **Flag type**, select **Boolean**.
6. Click **Create flag**.

The flag exists, but it's off everywhere. You'll turn it on after wiring the code.

# Wire the flag into the app

Open [Code Editor](#tab-2) and open `server.py`.

Find the block marked:

```python
# ─────────────────────────────────────────────────────────────────────
# CodeControl Challenge 01 paste block — replace this stub with flag evaluation.
```

Replace **everything between the opening marker and the** `# ─── End CodeControl Challenge 01 paste block` **line** with:

```python
    context = Context.builder(session_id).kind("user").set("tier", user_tier).build()
    return {
        "new_arrivals_enabled": ld_client.variation("new-arrivals-enabled", context, False),
    }
```

Save the file (⌘ S / Ctrl S). The ToggleWear service auto-reloads.

The `Context.builder` call is how you tell LaunchDarkly *who* is asking. The `ld_client.variation()` call evaluates the flag for that context and returns `True` or `False`. The second argument to `variation()` is the default — returned if the SDK can't reach LaunchDarkly.

# Check the storefront before flipping the flag

Open [ToggleWear](#tab-1). The **New Arrivals** banner should be absent — the flag is off, so the app got `False` from `variation()` and hid the section.

# Turn the flag on

Back in [LaunchDarkly](#tab-0):

<!-- VERIFY: Confirm targeting tab navigation and toggle button label -->
1. Open the **new-arrivals-enabled** flag.
2. Click the **Targeting** tab.
3. Make sure the environment selector reads **Production**.
4. Toggle the flag **On**.
5. Click **Review and save** → **Save changes**.

# See it live

Switch to [ToggleWear](#tab-1). The **New Arrivals** banner should now be visible — no restart, no redeploy, no deployment pipeline.

Switch back to [LaunchDarkly](#tab-0), turn the flag **Off**, and watch it disappear again. That's a kill switch. Turn it back **On** before clicking Check.

Click **Check** when the banner is visible.
