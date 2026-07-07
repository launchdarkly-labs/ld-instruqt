# End-state for CodeControl Challenge 03 — "Progressive Rollout".
#
# Creates the new-product-layout boolean flag with a 100% rollout in
# production (solve end-state = fully rolled out). During the lab the
# learner starts at 0% and expands manually via the UI.

resource "launchdarkly_feature_flag" "new_layout" {
  project_key    = var.project_key
  key            = "new-product-layout"
  name           = "New Product Layout"
  description    = "Progressively rolls out the sort bar above the product grid."
  variation_type = "boolean"
  tags           = ["instruqt", "codecontrol"]

  defaults {
    on_variation  = 0
    off_variation = 1
  }
}

resource "launchdarkly_feature_flag_environment" "new_layout_production" {
  flag_key    = launchdarkly_feature_flag.new_layout.key
  project_key = var.project_key
  env_key     = "production"
  on          = true

  fallthrough {
    rollout_weights = [100000, 0]
  }

  off_variation = 1
}
