    context = Context.builder(session_id).kind("user").set("tier", user_tier).build()
    return {
        "new_arrivals_enabled": ld_client.variation("new-arrivals-enabled", context, False),
    }
