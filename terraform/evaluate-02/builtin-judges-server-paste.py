    # ─── Evaluate 02: built-in judges — invoke attached judges ─────────────
    # Reads otto-born's judgeConfiguration and invokes each attached judge
    # explicitly. Because server.py uses completion_config + tracker rather
    # than the SDK's create_model + run path, attached judges don't
    # auto-fire — we have to do it here.
    #
    # LD Configs are versioned; edits (like attaching judges via the UI)
    # create new versions. This block probes both the "current" variation
    # GET and the versions endpoint to figure out which one carries the
    # attached judges. Debug logging is intentionally verbose while the
    # correct fetch pattern is being nailed down.
    try:
        import urllib.request as _urlreq
        import urllib.error as _urlerr
        import json as _json
        import random as _rand
        _proj = os.environ.get("LD_PROJECT_KEY")
        _tok = os.environ.get("LD_API_TOKEN")
        if not (_proj and _tok):
            log.warning("builtin-judge: LD_PROJECT_KEY or LD_API_TOKEN missing")
        else:
            _base = (
                "https://app.launchdarkly.com/api/v2/projects/"
                f"{_proj}/ai-configs/otto-assistant/variations/otto-born"
            )
            _headers = {"Authorization": _tok, "LD-API-Version": "beta"}

            def _get(_url):
                _req = _urlreq.Request(_url, headers=_headers)
                with _urlreq.urlopen(_req, timeout=5) as _r:
                    return _json.loads(_r.read())

            # Probe 1: bare variation GET.
            _var = _get(_base)
            _jc_direct = _var.get("judgeConfiguration") or {}
            _judges_direct = _jc_direct.get("judges", [])
            log.info(
                "builtin-judge: bare variation GET keys=%s judges=%d",
                sorted(_var.keys()), len(_judges_direct),
            )

            # Probe 2: variation versions endpoint (if it exists).
            _attached = list(_judges_direct)
            try:
                _versions_resp = _get(_base + "/versions")
                _items = _versions_resp.get("items") or _versions_resp.get("versions") or []
                log.info("builtin-judge: /versions returned %d entries", len(_items))
                if _items:
                    # Pick the highest version number if the entries carry one;
                    # otherwise assume the list is ordered latest-first.
                    _has_version_num = any("version" in _i for _i in _items)
                    if _has_version_num:
                        _latest = max(_items, key=lambda v: v.get("version", 0))
                    else:
                        _latest = _items[0]
                    log.info(
                        "builtin-judge: latest version keys=%s",
                        sorted(_latest.keys()),
                    )
                    _jc_versioned = _latest.get("judgeConfiguration") or {}
                    _judges_versioned = _jc_versioned.get("judges", [])
                    if _judges_versioned:
                        log.info(
                            "builtin-judge: using versioned judges (%d)",
                            len(_judges_versioned),
                        )
                        _attached = _judges_versioned
            except _urlerr.HTTPError as _e:
                log.info(
                    "builtin-judge: /versions endpoint returned HTTP %d (skipping)",
                    _e.code,
                )

            log.info("builtin-judge: proceeding with %d attached judges", len(_attached))
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
