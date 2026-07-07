    # ─── Evaluate 02: built-in judges — invoke attached judges ─────────────
    # server.py uses completion_config + tracker rather than the SDK's
    # create_model + run path, so attached judges don't auto-fire. Invoke
    # each attached judge explicitly on every /chat call.
    #
    # The variation endpoint at /ai-configs/{config}/variations/{var} in the
    # LD API returns a LIST of that variation's versions, shaped as
    # {items: [...], totalCount: N}. Each item is a versioned snapshot with
    # its own judgeConfiguration. Attaching judges via the UI creates a new
    # version -- so we iterate items and pick the latest one that has
    # judges attached.
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
            log.info(
                "builtin-judge: %d versions returned (totalCount=%s)",
                len(_items), _resp.get("totalCount"),
            )
            _attached = []
            _selected_ver = None
            for _item in _items:
                # LD may name the version field several things; try a few.
                _v = (
                    _item.get("version")
                    or _item.get("versionNumber")
                    or _item.get("_version")
                    or 0
                )
                _jc = _item.get("judgeConfiguration") or {}
                _judges = _jc.get("judges", [])
                log.info(
                    "builtin-judge: item version=%s judges=%d keys=%s",
                    _v, len(_judges), sorted(_item.keys())[:12],
                )
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
                log.info("builtin-judge: candidate key=%s sampling=%.2f", _jk, _sr)
                if _rand.random() > _sr:
                    continue
                _ctx = Context.builder(req.session_id).set("tier", req.user_tier).build()
                _jc_sdk = ai_client.judge_config(
                    _jk, _ctx, variables={"response": assistant_text}
                )
                log.info(
                    "builtin-judge: fetched cfg key=%s enabled=%s model=%s",
                    _jk, _jc_sdk.enabled,
                    (_jc_sdk.model.name if _jc_sdk.model else None),
                )
                if not _jc_sdk.enabled or _jc_sdk.model is None:
                    continue
                _sys = [
                    {"text": m.content}
                    for m in (_jc_sdk.messages or []) if m.role == "system"
                ]
                _msgs = [
                    {"role": m.role, "content": [{"text": m.content}]}
                    for m in (_jc_sdk.messages or []) if m.role != "system"
                ]
                _kw = {
                    "modelId": resolve_bedrock_model(_jc_sdk.model.name),
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
