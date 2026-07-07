    # ─── Evaluate 02: built-in judges — invoke attached judges ─────────────
    # server.py uses completion_config + tracker rather than the SDK's
    # create_model + run path, so attached judges don't auto-fire. Invoke
    # each attached judge explicitly on every /chat call.
    #
    # The variation endpoint at /ai-configs/{config}/variations/{var} returns
    # a paginated LIST of versions of that variation. Attaching judges via
    # the UI creates a new version -- so we iterate items and pick the
    # latest with a non-empty judges array.
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
                _resp = _json.loads(_r.read())
            _items = _resp.get("items", [])
            _attached = []
            _selected_ver = None
            for _item in _items:
                _v = (
                    _item.get("version")
                    or _item.get("versionNumber")
                    or _item.get("_version")
                    or 0
                )
                _jc = _item.get("judgeConfiguration") or {}
                _judges = _jc.get("judges", [])
                if _judges and (_selected_ver is None or _v > _selected_ver):
                    _attached = _judges
                    _selected_ver = _v
            log.info(
                "builtin-judge: selected version=%s with %d judges",
                _selected_ver if _selected_ver is not None else "n/a",
                len(_attached),
            )
            for _j in _attached:
                _jk = _j.get("judgeConfigKey")
                _sr = float(_j.get("samplingRate", 0.0))
                if _rand.random() > _sr:
                    continue
                try:
                    _ctx = Context.builder(req.session_id).set("tier", req.user_tier).build()
                    _jc_sdk = ai_client.judge_config(
                        _jk, _ctx, variables={"response": assistant_text}
                    )
                    log.info(
                        "builtin-judge: step=fetched-cfg key=%s enabled=%s model=%s",
                        _jk, _jc_sdk.enabled,
                        (_jc_sdk.model.name if _jc_sdk.model else None),
                    )
                    if not _jc_sdk.enabled or _jc_sdk.model is None:
                        log.info("builtin-judge: skipping (not enabled or no model) key=%s", _jk)
                        continue
                    _sys = [
                        {"text": m.content}
                        for m in (_jc_sdk.messages or []) if m.role == "system"
                    ]
                    _msgs = [
                        {"role": m.role, "content": [{"text": m.content}]}
                        for m in (_jc_sdk.messages or []) if m.role != "system"
                    ]
                    if not _msgs:
                        # Built-in judge templates typically contain only a
                        # system prompt with {response} already interpolated.
                        # Bedrock's Converse API rejects an empty messages
                        # list -- it requires at least one user turn.
                        _msgs = [{
                            "role": "user",
                            "content": [{
                                "text": "Provide your score as a single number between 0.0 and 1.0.",
                            }],
                        }]
                    _raw_model = _jc_sdk.model.name
                    try:
                        _model_id = resolve_bedrock_model(_raw_model)
                    except Exception as _re:  # noqa: BLE001
                        log.warning(
                            "builtin-judge: step=resolve-model key=%s raw=%s -> exception %s; using raw",
                            _jk, _raw_model, _re,
                        )
                        _model_id = _raw_model
                    log.info(
                        "builtin-judge: step=resolved-model key=%s raw=%s -> %s sys=%d msgs=%d",
                        _jk, _raw_model, _model_id, len(_sys), len(_msgs),
                    )
                    _kw = {
                        "modelId": _model_id,
                        "messages": _msgs,
                        "inferenceConfig": {"maxTokens": 8, "temperature": 0.0},
                    }
                    if _sys:
                        _kw["system"] = _sys
                    _br = bedrock.converse(**_kw)
                    log.info("builtin-judge: step=bedrock-ok key=%s", _jk)
                    # Extract text without relying on a helper that may not
                    # exist in server.py at ch02 time.
                    _txt_parts = []
                    for _content in _br.get("output", {}).get("message", {}).get("content", []):
                        if "text" in _content:
                            _txt_parts.append(_content["text"])
                    _txt = "".join(_txt_parts).strip()
                    log.info("builtin-judge: step=extracted-text key=%s raw=%r", _jk, _txt[:80])
                    try:
                        _score = float(_txt.split()[0])
                    except (ValueError, IndexError):
                        _score = None
                    _metric_key = f"$ld:ai:judge:{_jk}"
                    if _score is not None and 0.0 <= _score <= 1.0:
                        ld_client.track(_metric_key, _ctx, None, _score)
                        log.info(
                            "builtin-judge: step=tracked session=%s judge=%s score=%.2f metric=%s",
                            req.session_id, _jk, _score, _metric_key,
                        )
                    else:
                        log.warning(
                            "builtin-judge: step=parse-fail key=%s raw=%r",
                            _jk, _txt,
                        )
                except Exception as _pe:  # noqa: BLE001
                    log.exception(
                        "builtin-judge: per-judge failure key=%s: %s",
                        _jk, _pe,
                    )
    except Exception as _oe:  # noqa: BLE001
        log.exception("builtin-judge: outer failure: %s", _oe)
