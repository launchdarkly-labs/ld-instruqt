    # ─── Evaluate 02: built-in judges — emit judge scores via the SDK ────
    # When completion_config() ran on Otto's config, the SDK saw the
    # judges attached to the active variation and built a wired Evaluator
    # on `cfg`. Each Judge inside knows its own model, provider, prompt,
    # and evaluationMetricKey. Running the Evaluator invokes the judges
    # concurrently, parses each judge's structured {score, reasoning}
    # response, and produces a JudgeResult with the right metric_key and
    # event shape. Emitting via tracker.track_judge_result routes the
    # score through the SDK's canonical evaluator-metric event path --
    # which is what the LD Monitoring UI reads from.
    import asyncio as _asyncio
    try:
        _evaluator = getattr(cfg, "evaluator", None)
        if _evaluator is None:
            log.info("builtin-judge: no evaluator on cfg; nothing to emit")
        else:
            async def _run_judges():
                return await _evaluator.evaluate(req.message, assistant_text)
            _results = _asyncio.run(_run_judges())
            log.info("builtin-judge: evaluator returned %d results", len(_results))
            for _result in _results:
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
        log.exception("builtin-judge: evaluator invocation failed")
