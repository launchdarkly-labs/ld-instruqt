# End-state for Evaluate Challenge 04 — "Otto Checks His Facts".
#
# Creates the product-claim judge — a Config in judge mode that grades
# whether Otto's responses contain claims contradicting the ToggleWear
# catalog. The catalog itself lives in a snippet (`product-catalog`), so
# the same snippet-as-data pattern that drives the brand-voice judge
# drives this one too. Adding a new product means editing one snippet.
#
# Resources:
#   * null_resource create_product_catalog_snippet - REST POST (snippets
#     aren't exposed by the Terraform provider)
#   * launchdarkly_ai_config           - otto-claim-accuracy-judge
#   * launchdarkly_ai_config_variation - default, Haiku-backed
#   * null_resource set_judge_fallthrough
#   * launchdarkly_metric              - otto-claim-accuracy-score
#
# evaluationMetricKey on otto-assistant is NOT changed by this module —
# Evaluate ch03 already pointed it at otto-brand-voice-score, and the
# guarded rollout in ch07 needs that wiring intact. The claim-accuracy
# metric flows as an auxiliary signal in the monitoring view.

locals {
  product_catalog_text = trimspace(<<-CATALOG
    ToggleWear product catalog. These are the only products we sell. Anything not in this list is not a ToggleWear product.

    - Rocket Tee - $28. Heather grey, classic crew-neck t-shirt with the LaunchDarkly rocket.
    - Feature Flag Hoodie - $58. Midnight navy, pullover with embroidered flag logo.
    - Dark Mode Cap - $24. Six-panel dad cap with tone-on-tone black logo.
    - Ship It Mug - $16. 12oz ceramic, "Ship it" in the LaunchDarkly font.
    - Toggle Socks - $14. Crew socks with a tiny rocket on the ankle.
    - Release Notes Notebook - $18. A5 hardcover with dot grid.
    - Rollout Tote - $22. 12oz canvas with reinforced handles.
    - Feature Branch Crewneck - $52. Heavyweight sage green sweatshirt.

    Otto should not invent stock, sizes, materials beyond what's listed, colors not listed, return policies, shipping details, or any other facts not stated above. He may suggest customers check the product page or contact support for specifics he doesn't have.
  CATALOG
  )

  claim_judge_prompt = <<-PROMPT
    You are evaluating whether Otto's response to a customer makes any factual product claims that contradict the ToggleWear catalog.

    The catalog is the only source of truth:

    {{snippet.product-catalog#1}}

    Customer's question:
    {{input}}

    Otto's response:
    {{response}}

    Score 0.0 to 1.0:
    - 1.0: Response makes no claims that contradict the catalog, OR makes no factual product claims at all (e.g. asks a clarifying question, gracefully declines).
    - 0.5: Borderline — mentions a product detail not in the catalog but doesn't clearly contradict it.
    - 0.0: Response asserts a price, material, size, color, policy, or other fact that contradicts or is unsupported by the catalog.

    Respond with ONLY a number between 0.0 and 1.0. No other text.
  PROMPT
}

# ─── Product-catalog snippet ───────────────────────────────────────────────

resource "null_resource" "create_product_catalog_snippet" {
  triggers = {
    text_hash = sha256(local.product_catalog_text)
  }

  provisioner "local-exec" {
    command = <<-EOT
      curl -fsS -X POST \
        'https://app.launchdarkly.com/api/v2/projects/${var.project_key}/ai-configs/prompt-snippets' \
        -H "Authorization: $LAUNCHDARKLY_ACCESS_TOKEN" \
        -H 'Content-Type: application/json' \
        --data-raw "$(jq -n --arg t "${local.product_catalog_text}" \
          '{key:"product-catalog", name:"Product catalog", text:$t, tags:["instruqt"]}')" \
        || echo "(snippet may already exist — continuing)"
    EOT
  }
}

# ─── Product-claim judge Config ────────────────────────────────────────────

resource "launchdarkly_ai_config" "claim_judge" {
  project_key = var.project_key
  key         = "otto-claim-accuracy-judge"
  name        = "Otto Claim Accuracy Judge"
  description = "Scores Otto's responses 0.0-1.0 for accuracy against the product-catalog snippet. Drives otto-claim-accuracy-score."
  mode        = "judge"
  tags        = ["instruqt", "ai-configs-intro"]
}

resource "launchdarkly_ai_config_variation" "claim_judge_default" {
  project_key      = var.project_key
  config_key       = launchdarkly_ai_config.claim_judge.key
  key              = "default"
  name             = "Default"
  model_config_key = "Anthropic.claude-haiku-4-5"

  depends_on = [null_resource.create_product_catalog_snippet]

  messages {
    role    = "system"
    content = trimspace(local.claim_judge_prompt)
  }
}

resource "null_resource" "set_claim_judge_fallthrough" {
  triggers = {
    variation_id = launchdarkly_ai_config_variation.claim_judge_default.variation_id
  }

  provisioner "local-exec" {
    command = <<-EOT
      curl -fsS -X PATCH \
        'https://app.launchdarkly.com/api/v2/projects/${var.project_key}/ai-configs/${launchdarkly_ai_config.claim_judge.key}/targeting' \
        -H "Authorization: $LAUNCHDARKLY_ACCESS_TOKEN" \
        -H 'Content-Type: application/json; domain-model=launchdarkly.semanticpatch' \
        --data-raw '{"environmentKey":"test","instructions":[{"kind":"updateFallthroughVariationOrRollout","variationId":"${launchdarkly_ai_config_variation.claim_judge_default.variation_id}"}]}'
    EOT
  }
}

# ─── Claim-accuracy score metric ───────────────────────────────────────────

resource "launchdarkly_metric" "claim_accuracy_score" {
  project_key           = var.project_key
  key                   = "otto-claim-accuracy-score"
  name                  = "Otto Claim Accuracy Score"
  description           = "Mean claim-accuracy judge score (0.0-1.0) for Otto's responses. Higher is better."
  kind                  = "custom"
  event_key             = "otto-claim-accuracy-score"
  is_numeric            = true
  unit                  = "score"
  unit_aggregation_type = "average"
  success_criteria      = "HigherThanBaseline"
  analysis_type         = "mean"
  randomization_units   = ["user"]
  tags                  = ["instruqt"]
}
