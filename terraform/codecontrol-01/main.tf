# End-state for CodeControl Challenge 01 — "Your First Feature Flag".
#
# Creates the new-arrivals-enabled boolean flag in the per-student project.
# The flag starts OFF in production — the learner turns it on in the UI.
# solve-workstation applies this module then turns the flag on via the REST API.

resource "launchdarkly_feature_flag" "new_arrivals" {
  project_key    = var.project_key
  key            = "new-arrivals-enabled"
  name           = "New Arrivals Enabled"
  description    = "Shows the New Arrivals banner on the ToggleWear storefront."
  variation_type = "boolean"
  tags           = ["instruqt", "codecontrol"]

  defaults {
    on_variation  = 0
    off_variation = 1
  }
}

resource "launchdarkly_feature_flag_environment" "new_arrivals_production" {
  flag_key    = launchdarkly_feature_flag.new_arrivals.key
  project_key = var.project_key
  env_key     = "production"
  on          = false

  fallthrough {
    variation = 0
  }

  off_variation = 1
}
