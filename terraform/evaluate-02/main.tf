# End-state for Evaluate Challenge 02 — "Quick Takes".
#
# Attaches the three built-in judges (Accuracy, Relevance, Toxicity) to the
# otto-born variation at a 25% sampling rate each. The judges then grade
# 25% of incoming Otto responses automatically; scores appear in the
# monitoring view's evaluator metrics dropdown.
#
# The literal judgeConfigKey value for each built-in isn't published in
# the LD docs, so this module discovers the keys at apply-time by listing
# the project's judge-mode configs and matching on the well-known metric
# keys ($ld:ai:judge:accuracy, $ld:ai:judge:relevance, $ld:ai:judge:toxicity).
# Built-in judges appear to be auto-provisioned in every project when
# AgentControl is enabled.
#
# VERIFY: confirm the listing approach works against a freshly-bootstrapped
# project. If built-ins aren't surfaced via the configs listing, fall back
# to literal config keys (operator's click-through reveals the actual keys
# from the UI's URL bar).

locals {
  api_base = "https://app.launchdarkly.com/api/v2"

  sampling_rate = 0.25
}

resource "null_resource" "attach_built_in_judges" {
  triggers = {
    config    = "otto-assistant"
    variation = "otto-born"
    rate      = local.sampling_rate
  }

  provisioner "local-exec" {
    command = <<-EOT
      set -e

      ALL=$(curl -fsS -X GET \
        '${local.api_base}/projects/${var.project_key}/ai-configs?limit=100' \
        -H "Authorization: $LAUNCHDARKLY_ACCESS_TOKEN" \
        -H 'LD-API-Version: beta')

      ACCURACY_KEY=$(echo "$ALL" | jq -r '.items[]? | select(.mode == "judge" and .evaluationMetricKey == "$ld:ai:judge:accuracy") | .key' | head -n 1)
      RELEVANCE_KEY=$(echo "$ALL" | jq -r '.items[]? | select(.mode == "judge" and .evaluationMetricKey == "$ld:ai:judge:relevance") | .key' | head -n 1)
      TOXICITY_KEY=$(echo "$ALL" | jq -r '.items[]? | select(.mode == "judge" and .evaluationMetricKey == "$ld:ai:judge:toxicity") | .key' | head -n 1)

      if [ -z "$ACCURACY_KEY" ] || [ -z "$RELEVANCE_KEY" ] || [ -z "$TOXICITY_KEY" ]; then
        echo "Could not locate one or more built-in judges in this project."
        echo "Found: accuracy=$ACCURACY_KEY relevance=$RELEVANCE_KEY toxicity=$TOXICITY_KEY"
        echo "All judge-mode configs in this project:"
        echo "$ALL" | jq '.items[]? | select(.mode == "judge") | {key, name, evaluationMetricKey}'
        exit 1
      fi

      curl -fsS -X PATCH \
        '${local.api_base}/projects/${var.project_key}/ai-configs/otto-assistant/variations/otto-born' \
        -H "Authorization: $LAUNCHDARKLY_ACCESS_TOKEN" \
        -H 'Content-Type: application/json' \
        -H 'LD-API-Version: beta' \
        --data-raw "$(jq -n \
          --arg a "$ACCURACY_KEY" \
          --arg r "$RELEVANCE_KEY" \
          --arg t "$TOXICITY_KEY" \
          --argjson rate ${local.sampling_rate} \
          '{judgeConfiguration: {judges: [
            {judgeConfigKey: $a, samplingRate: $rate},
            {judgeConfigKey: $r, samplingRate: $rate},
            {judgeConfigKey: $t, samplingRate: $rate}
          ]}}')" \
        > /dev/null
    EOT
  }
}
