    # ─── Evaluate 02: built-in judges — manual Bedrock + tracker emit ─────
    # The SDK's create_judge / _build_evaluator path can't invoke Bedrock:
    # ldai's provider registry only knows about openai and langchain (via
    # separate ldai_openai / ldai_langchain packages). Since our judges
    # use Bedrock directly, RunnerFactory.create_model returns None ->
    # _create_judge_instance returns None -> Evaluator is empty.
    #
    # So we invoke Bedrock ourselves for each attached judge, then wrap
    # the score in a JudgeResult and route through
    # tracker.track_judge_result(). That routes the event with the
    # correct evaluationMetricKey AND the judgeConfigKey in the event
    # envelope -- the shape the LD Monitoring UI reads as evaluator
    # metrics. Plain ld_client.track(metric_key, ...) misses the
    # judgeConfigKey envelope and doesn't register.
    try:
        from ldai.providers.types import JudgeResult
        import urllib.request as _urlreq
        import json as _json
        import random as _rand
        _proj = os.environ.get("LD_PROJECT_KEY")
        _tok = os.environ.get("LD_API_TOKEN")
        if not (_proj and _tok):
            log.warning("builtin-judge: LD_PROJECT_KEY or LD_API_TOKEN missing")
        else:
            # Fetch attached judges from otto-born's latest variation version.
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
                _v = _item.get("version", 0)
                _jcfg = _item.get("judgeConfiguration") or {}
                _judges = _jcfg.get("judges", [])
                if _judges and (_selected_ver is None or _v > _selected_ver):
                    _attached = _judges
                    _selected_ver = _v
            log.info(
                "builtin-judge: variation version=%s attached=%d",
                _selected_ver, len(_attached),
            )

            for _j in _attached:
                _jk = _j.get("judgeConfigKey")
                _sr = float(_j.get("samplingRate", 1.0))
                if _rand.random() > _sr:
                    continue  # Not sampled; skip invocation + emission entirely.
                _jr = JudgeResult(judge_config_key=_jk)
                _jr.sampled = True
                try:
                    _cfg_j = ai_client.judge_config(
                        _jk, context, variables={"response": assistant_text}
                    )
                    if not _cfg_j.enabled or _cfg_j.model is None:
                        _jr.error_message = "judge disabled or no model"
                        tracker.track_judge_result(_jr)
                        continue
                    _metric_key = getattr(_cfg_j, "evaluation_metric_key", None)
                    if not _metric_key:
                        _jr.error_message = "no evaluation_metric_key on judge config"
                        tracker.track_judge_result(_jr)
                        log.warning("builtin-judge: key=%s missing evaluation_metric_key", _jk)
                        continue
                    _jr.metric_key = _metric_key

                    # Build the Bedrock request from the judge's messages.
                    _sys = [
                        {"text": m.content}
                        for m in (_cfg_j.messages or []) if m.role == "system"
                    ]
                    _msgs = [
                        {"role": m.role, "content": [{"text": m.content}]}
                        for m in (_cfg_j.messages or []) if m.role != "system"
                    ]
                    if not _msgs:
                        # Built-in judge templates only have a system prompt;
                        # Bedrock's Converse API requires at least one user
                        # turn. Include the response text explicitly so the
                        # model has something to evaluate.
                        _msgs = [{
                            "role": "user",
                            "content": [{
                                "text": (
                                    "Response to evaluate:\n\n"
                                    f"{assistant_text}\n\n"
                                    "Provide your score as a single number "
                                    "between 0.0 and 1.0."
                                ),
                            }],
                        }]
                    _raw_model = _cfg_j.model.name
                    try:
                        _model_id = resolve_bedrock_model(_raw_model)
                    except Exception:  # noqa: BLE001
                        _model_id = _raw_model
                    _kw = {
                        "modelId": _model_id,
                        "messages": _msgs,
                        "inferenceConfig": {"maxTokens": 8, "temperature": 0.0},
                    }
                    if _sys:
                        _kw["system"] = _sys
                    _br = bedrock.converse(**_kw)

                    # Extract score from response text.
                    _txt_parts = []
                    for _c in _br.get("output", {}).get("message", {}).get("content", []):
                        if "text" in _c:
                            _txt_parts.append(_c["text"])
                    _txt = "".join(_txt_parts).strip()
                    try:
                        _score = float(_txt.split()[0])
                    except (ValueError, IndexError):
                        _score = None
                    if _score is not None and 0.0 <= _score <= 1.0:
                        _jr.score = _score
                        _jr.success = True
                    else:
                        _jr.error_message = f"unparseable score: {_txt!r}"
                    tracker.track_judge_result(_jr)
                    log.info(
                        "builtin-judge: emitted judge=%s metric=%s score=%s success=%s",
                        _jk, _metric_key, _jr.score, _jr.success,
                    )
                except Exception as _pe:  # noqa: BLE001
                    _jr.error_message = str(_pe)
                    tracker.track_judge_result(_jr)
                    log.exception("builtin-judge: per-judge failure key=%s", _jk)
    except Exception:  # noqa: BLE001
        log.exception("builtin-judge: outer failure")
