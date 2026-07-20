---
slug: kill-switch
id: cdxjoxdlh8ie
type: challenge
title: The Kill Switch
teaser: Simulate a bad release. Flip the flag off. Watch the storefront recover —
  no redeploy.
notes:
- type: text
  contents: Every feature flag is a kill switch. When a release goes wrong in production,
    the fastest remediation is turning the flag off — not rolling back a deployment.
    You'll see exactly how fast that is.
tabs:
- id: 7etktpv8i6g8
  title: LaunchDarkly
  type: browser
  hostname: launchdarkly
- id: owyynvqwzunt
  title: ToggleWear
  type: service
  hostname: workstation
  port: 3000
- id: maiudizrb3tb
  title: Code Editor
  type: service
  hostname: workstation
  port: 8080
difficulty: basic
timelimit: 600
enhanced_loading: null
---

# Something is wrong

Open [ToggleWear](#tab-1). The storefront is broken — product cards are skewed, colors are garish, images are distorted.

A bad CSS change shipped as part of the **New Product Layout** feature. Every user visiting the site right now sees this. In a traditional deployment workflow, you'd revert the commit, wait for CI to rebuild, redeploy, and hope nothing else breaks along the way. That takes minutes at best, hours at worst.

With LaunchDarkly, you have a faster option.

# Pull the kill switch

Open [LaunchDarkly](#tab-0).

<!-- VERIFY: Confirm targeting tab navigation and toggle-off button label -->
1. In the left sidebar, click **Feature Flags** under **CodeControl**.
2. Open the **new-product-layout** flag.
3. Click the **Targeting** tab.
4. Make sure the environment selector reads **Production**.
5. Toggle the flag **Off**.
6. Click **Review and save** → **Save changes**.

# Watch it recover

Switch to [ToggleWear](#tab-1) and reload the page.

The storefront should be back to normal — clean layout, correct colors, proper images. The broken CSS is still in the codebase, but it no longer affects users because the flag that activated it is off.

No rollback. No revert commit. No deployment pipeline. Seconds, not minutes.

Every feature flag you've created in this track is a kill switch:

- The **New Arrivals** banner from Challenge 01 — turn it off and the banner disappears.
- The **Premium Banner** from Challenge 02 — turn it off and premium targeting stops.
- The **Progressive Rollout** from Challenge 03 — turn it off and the layout reverts.
- The **Hero Headline** experiment from Challenge 04 — turn it off and the default headline returns.

This is the safety net that makes shipping fast possible. You can always turn it off.

Click **Check** when the flag is off and the storefront is healthy.
