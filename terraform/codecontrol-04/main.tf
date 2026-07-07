# End-state for CodeControl Challenge 04 — "Run an Experiment".
#
# Creates the hero-headline string flag with two variations.
# The metric and experiment are created via curl in solve-workstation
# because the Terraform provider doesn't cover those resources.

resource "launchdarkly_feature_flag" "hero_headline" {
  project_key    = var.project_key
  key            = "hero-headline"
  name           = "Hero Headline"
  description    = "A/B test headline for the storefront hero section."
  variation_type = "string"
  tags           = ["instruqt", "codecontrol"]

  variations {
    value = "Wear your features on your sleeve."
    name  = "Control"
  }
  variations {
    value = "Ship fast. Look good."
    name  = "Treatment"
  }

  defaults {
    on_variation  = 0
    off_variation = 0
  }
}

resource "launchdarkly_feature_flag_environment" "hero_headline_production" {
  flag_key    = launchdarkly_feature_flag.hero_headline.key
  project_key = var.project_key
  env_key     = "production"
  on          = true

  fallthrough {
    variation = 0
  }

  off_variation = 0
}
