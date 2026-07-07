    # ─── Evaluate 02: built-in judges — invoke via create_judge + track ───
    # cfg.evaluator comes back with 0 judges because completion_config()
    # doesn't wire attached judges into the returned Evaluator.
    # ai_client.create_model() would (and that's the "managed" path),
    # but switching ch01's server.py to create_model is a larger
    # refactor. For now: fetch the list of attached judges from Otto's
    # variation via REST, create a Judge instance per attached key via
    # ai_client.create_judge(), invoke each with its per-variation
    # samplingRate, and emit results via tracker.track_judge_result --
    # the SDK's canonical evaluator-metric event path.
    import asyncio as _asyncio
    try:
        import urllib.request as _urlreq
        import json as _json
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

            async def _run_one(_jk, _sr):
                _judge = ai_client.create_judge(_jk, context)
                if _judge is None:
                    return None
                return await _judge.evaluate(
                    req.message, assistant_text, sampling_rate=_sr,
                )

            async def _run_all():
                _tasks = []
                for _j in _attached:
                    _jk = _j.get("judgeConfigKey")
                    _sr = float(_j.get("samplingRate", 1.0))
                    _tasks.append((_jk, _run_one(_jk, _sr)))
                _res = await _asyncio.gather(*(t[1] for t in _tasks))
                return list(zip((t[0] for t in _tasks), _res))

            for _jk, _result in _asyncio.run(_run_all()):
                if _result is None:
                    log.warning("builtin-judge: create_judge returned None key=%s", _jk)
                    continue
                tracker.track_judge_result(_result)
                log.info(
                    "builtin-judge: emitted judge=%s metric=%s score=%s "
                    "sampled=%s success=%s error=%s",
                    getattr(_result, "judge_config_key", None),
                    getattr(_result, "metric_key", None),
                    getattr(_result, "score", None),
                    getattr(_result, "sampled", None),
                    getattr(_result, "success", None),
                    getattr(_result, "error_message", None),
                )
    except Exception:  # noqa: BLE001
        log.exception("builtin-judge: outer failure")
