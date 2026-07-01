    # ─── Evaluate 02: built-in judges — invoke attached judges explicitly ──
    # server.py uses completion_config + tracker instead of the SDK's
    # create_model + run path, so attached built-in judges don't auto-fire.
    # Discover them once (config-list filtered by metric key), read the
    # attached judges + sampling rates off otto-born, then on every /chat
    # call roll each judge's dice and invoke if sampled. Emits the score to
    # the corresponding $ld:ai:judge:* metric key so it lands under
    # Monitoring -> Evaluator metrics.
    try:
        if not globals().get("_BUILTIN_JUDGES_LOADED"):
            import urllib.request as _u_req_bij
            import urllib.error as _u_err_bij
            import json as _j_mod_bij
            _proj_bij = os.environ.get("LD_PROJECT_KEY")
            _tok_bij = os.environ.get("LAUNCHDARKLY_ACCESS_TOKEN")
            _wanted_bij = {
                "$ld:ai:judge:accuracy",
                "$ld:ai:judge:relevance",
                "$ld:ai:judge:toxicity",
            }
            _cache_bij = []
            if _proj_bij and _tok_bij:
                try:
                    _r_bij = _u_req_bij.Request(
                        f"https://app.launchdarkly.com/api/v2/projects/{_proj_bij}/ai-configs?limit=100",
                        headers={"Authorization": _tok_bij, "LD-API-Version": "beta"},
                    )
                    with _u_req_bij.urlopen(_r_bij, timeout=5) as _rp_bij:
                        _all_cfgs_bij = _j_mod_bij.loads(_rp_bij.read())
                    _metric_to_key_bij = {}
                    for _it_bij in _all_cfgs_bij.get("items", []):
                        _emk_bij = _it_bij.get("evaluationMetricKey")
                        if _it_bij.get("mode") == "judge" and _emk_bij in _wanted_bij:
                            _metric_to_key_bij[_emk_bij] = _it_bij.get("key")
                    _r_bij = _u_req_bij.Request(
                        f"https://app.launchdarkly.com/api/v2/projects/{_proj_bij}/ai-configs/otto-assistant/variations/otto-born",
                        headers={"Authorization": _tok_bij, "LD-API-Version": "beta"},
                    )
                    with _u_req_bij.urlopen(_r_bij, timeout=5) as _rp_bij:
                        _var_bij = _j_mod_bij.loads(_rp_bij.read())
                    _attached_bij = {
                        j.get("judgeConfigKey"): float(j.get("samplingRate", 0.0))
                        for j in _var_bij.get("judgeConfiguration", {}).get("judges", [])
                    }
                    for _metric_key_bij, _judge_key_bij in _metric_to_key_bij.items():
                        _rate_bij = _attached_bij.get(_judge_key_bij, 0.0)
                        if _rate_bij > 0:
                            _cache_bij.append((_judge_key_bij, _rate_bij, _metric_key_bij))
                except _u_err_bij.URLError as _e_bij:
                    log.warning("built-in judges: discovery failed: %s", _e_bij)
            globals()["_BUILTIN_JUDGES"] = _cache_bij
            globals()["_BUILTIN_JUDGES_LOADED"] = True
            log.info("built-in judges cached: %d attached at nonzero sampling", len(_cache_bij))

        import random as _rnd_bij
        for _judge_key_bij, _rate_bij, _metric_key_bij in globals().get("_BUILTIN_JUDGES", []):
            if _rnd_bij.random() > _rate_bij:
                continue
            _bij_ctx = Context.builder(req.session_id).set("tier", req.user_tier).build()
            _bij_cfg = ai_client.judge_config(
                _judge_key_bij,
                _bij_ctx,
                variables={"response": assistant_text},
            )
            if not _bij_cfg.enabled or _bij_cfg.model is None:
                continue
            _bij_sys = [
                {"text": m.content}
                for m in (_bij_cfg.messages or []) if m.role == "system"
            ]
            _bij_msgs = [
                {"role": m.role, "content": [{"text": m.content}]}
                for m in (_bij_cfg.messages or []) if m.role != "system"
            ]
            _bij_kw = {
                "modelId": resolve_bedrock_model(_bij_cfg.model.name),
                "messages": _bij_msgs,
                "inferenceConfig": {"maxTokens": 8, "temperature": 0.0},
            }
            if _bij_sys:
                _bij_kw["system"] = _bij_sys
            _bij_resp = bedrock.converse(**_bij_kw)
            _bij_text = _extract_text(_bij_resp).strip()
            try:
                _bij_score = float(_bij_text.split()[0])
            except (ValueError, IndexError):
                _bij_score = None
            if _bij_score is not None and 0.0 <= _bij_score <= 1.0:
                ld_client.track(_metric_key_bij, _bij_ctx, None, _bij_score)
                log.info(
                    "builtin-judge session=%s judge=%s score=%.2f",
                    req.session_id, _judge_key_bij, _bij_score,
                )
    except Exception:  # noqa: BLE001
        log.exception("Built-in judge invocation failed (non-fatal)")
