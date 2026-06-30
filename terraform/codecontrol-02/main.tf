# End-state for CodeControl Challenge 02 — "Target by Tier".
#
# Creates a "Premium Members" segment (rule: tier = premium), the premium-banner
# boolean flag, and a targeting rule on the flag that serves true to anyone
# in the segment and false to everyone else.

resource "launchdarkly_segment" "premium_members" {
  project_key = var.project_key
  env_key     = "production"
  key         = "premium-members"
  name        = "Premium Members"
  description = "Users whose tier attribute equals premium."

  rules {
    clauses {
      attribute    = "tier"
      op           = "in"
      values       = ["premium"]
      context_kind = "user"
      negate       = false
    }
  }
}

resource "launchdarkly_feature_flag" "premium_banner" {
  project_key    = var.project_key
  key            = "premium-banner"
  name           = "Premium Banner"
  description    = "Shows the Members Only banner to premium-tier users on the ToggleWear storefront."
  variation_type = "boolean"
  tags           = ["instruqt", "codecontrol"]

  defaults {
    on_variation  = 0
    off_variation = 1
  }
}

resource "launchdarkly_feature_flag_environment" "premium_banner_production" {
  flag_key    = launchdarkly_feature_flag.premium_banner.key
  project_key = var.project_key
  env_key     = "production"
  on          = true

  rules {
    variation = 0
    clauses {
      attribute    = "segmentMatch"
      op           = "segmentMatch"
      values       = [launchdarkly_segment.premium_members.key]
      negate       = false
    }
  }

  fallthrough {
    variation = 1
  }

  off_variation = 1
}
