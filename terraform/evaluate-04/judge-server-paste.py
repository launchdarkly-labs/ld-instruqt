    # ─── Evaluate 04: product-claim accuracy judge ──────────────────────────
    # Score Otto's response 0.0-1.0 against the product-catalog snippet via
    # the otto-claim-accuracy-judge Config. Emits otto-claim-accuracy-score.
    # Pass both {{input}} (the customer's question) and {{response}} as
    # template variables so the judge can ground its grading in context.
    try:
        cl_ctx = Context.builder(req.session_id).set("tier", req.user_tier).build()
        cl_cfg = ai_client.judge_config(
            "otto-claim-accuracy-judge",
            cl_ctx,
            variables={
                "input": req.message,
                "response": assistant_text,
            },
        )
        if cl_cfg.enabled and cl_cfg.model is not None:
            cl_system: list[dict] = []
            cl_messages: list[dict] = []
            for m in (cl_cfg.messages or []):
                if m.role == "system":
                    cl_system.append({"text": m.content})
                else:
                    cl_messages.append(
                        {"role": m.role, "content": [{"text": m.content}]}
                    )
            cl_kwargs = {
                "modelId": resolve_bedrock_model(cl_cfg.model.name),
                "messages": cl_messages,
                "inferenceConfig": {"maxTokens": 8, "temperature": 0.0},
            }
            if cl_system:
                cl_kwargs["system"] = cl_system
            cl_resp = bedrock.converse(**cl_kwargs)
            cl_text = _extract_text(cl_resp).strip()
            try:
                score = float(cl_text.split()[0])
            except (ValueError, IndexError):
                score = None
            if score is not None and 0.0 <= score <= 1.0:
                ld_client.track("otto-claim-accuracy-score", cl_ctx, None, score)
                log.info(
                    "claim-accuracy-judge session=%s otto_model=%s score=%.2f",
                    req.session_id, model_id, score,
                )
    except Exception:  # noqa: BLE001
        log.exception("Claim-accuracy judge eval failed (non-fatal)")
