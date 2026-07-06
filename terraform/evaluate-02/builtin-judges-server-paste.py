    # ─── Evaluate 02: built-in judges — invoke attached judges ─────────────
    # Read otto-born's judgeConfiguration on every /chat call, invoke each
    # attached judge programmatically (server.py's completion_config +
    # tracker path doesn't auto-fire them), and emit the score to a
    # per-judge metric key that lands under Monitoring -> Evaluator metrics.
    #
    # Debug logging is intentionally verbose during smoke-test. Trim once
    # the flow is confirmed.
    try:
        import urllib.request as _urlreq
        import json as _json
        import random as _rand
        _proj = os.environ.get("LD_PROJECT_KEY")
        _tok = os.environ.get("LD_API_TOKEN")
        if not (_proj and _tok):
            log.warning("builtin-judge: LD_PROJECT_KEY or LD_API_TOKEN missing")
        else:
            _url = (
                "https://app.launchdarkly.com/api/v2/projects/"
                f"{_proj}/ai-configs/otto-assistant/variations/otto-born"
            )
            _req = _urlreq.Request(
                _url,
                headers={"Authorization": _tok, "LD-API-Version": "beta"},
            )
            with _urlreq.urlopen(_req, timeout=5) as _r:
                _var = _json.loads(_r.read())
            _attached = _var.get("judgeConfiguration", {}).get("judges", [])
            log.info("builtin-judge: %d judges attached to otto-born", len(_attached))
            for _j in _attached:
                _jk = _j.get("judgeConfigKey")
                _sr = float(_j.get("samplingRate", 0.0))
                log.info("builtin-judge: candidate key=%s sampling=%.2f", _jk, _sr)
                if _rand.random() > _sr:
                    continue
                _ctx = Context.builder(req.session_id).set("tier", req.user_tier).build()
                _jc = ai_client.judge_config(
                    _jk, _ctx, variables={"response": assistant_text}
                )
                log.info(
                    "builtin-judge: fetched cfg key=%s enabled=%s model=%s",
                    _jk, _jc.enabled, (_jc.model.name if _jc.model else None),
                )
                if not _jc.enabled or _jc.model is None:
                    continue
                _sys = [
                    {"text": m.content}
                    for m in (_jc.messages or []) if m.role == "system"
                ]
                _msgs = [
                    {"role": m.role, "content": [{"text": m.content}]}
                    for m in (_jc.messages or []) if m.role != "system"
                ]
                _kw = {
                    "modelId": resolve_bedrock_model(_jc.model.name),
                    "messages": _msgs,
                    "inferenceConfig": {"maxTokens": 8, "temperature": 0.0},
                }
                if _sys:
                    _kw["system"] = _sys
                _br = bedrock.converse(**_kw)
                _txt = _extract_text(_br).strip()
                try:
                    _score = float(_txt.split()[0])
                except (ValueError, IndexError):
                    _score = None
                # Metric key convention for built-in judges: $ld:ai:judge:<name>.
                # If the judgeConfigKey is something like "accuracy" this maps
                # directly; if it's a prefixed / UUID form, this line will
                # emit under an unintended key and the log will surface it.
                _metric_key = f"$ld:ai:judge:{_jk}"
                if _score is not None and 0.0 <= _score <= 1.0:
                    ld_client.track(_metric_key, _ctx, None, _score)
                    log.info(
                        "builtin-judge: session=%s judge=%s score=%.2f metric=%s",
                        req.session_id, _jk, _score, _metric_key,
                    )
                else:
                    log.warning(
                        "builtin-judge: parse-fail key=%s raw=%r",
                        _jk, _txt,
                    )
    except Exception:  # noqa: BLE001
        log.exception("Built-in judge invocation failed (non-fatal)")
