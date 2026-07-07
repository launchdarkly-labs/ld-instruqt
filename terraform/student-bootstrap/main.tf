locals {
  project_key  = "agentcontrol-intro-${var.sandbox_id}"
  project_name = "Agent Control Intro — ${var.sandbox_id}"
}

resource "launchdarkly_project" "student" {
  key  = local.project_key
  name = local.project_name
  tags = ["instruqt", "agentcontrol-intro"]

  environments {
    key   = "test"
    name  = "Test"
    color = "417505"
  }
}
