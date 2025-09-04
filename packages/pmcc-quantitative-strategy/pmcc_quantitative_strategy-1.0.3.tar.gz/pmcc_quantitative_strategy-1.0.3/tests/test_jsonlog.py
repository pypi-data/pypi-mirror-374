from __future__ import annotations

import io
import json
import logging

from pmcc.jsonlog import log_event


def test_jsonlog_emits_single_json_line():
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    logger = logging.getLogger("pmcc.jsonlog.test")
    logger.setLevel(logging.INFO)
    # ensure dedicated handler for this test
    for h in list(logger.handlers):
        logger.removeHandler(h)
    logger.addHandler(handler)

    log_event(logger, "test", a=1, b="x")
    handler.flush()
    out = stream.getvalue().strip()
    obj = json.loads(out)
    assert obj.get("event") == "test"
    assert obj.get("a") == 1 and obj.get("b") == "x"
    assert isinstance(obj.get("ts"), int)


def test_jsonlog_handles_unserializable_values_with_repr():
    import io
    import json
    import logging

    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    logger = logging.getLogger("pmcc.jsonlog.test.unserializable")
    logger.setLevel(logging.INFO)
    for h in list(logger.handlers):
        logger.removeHandler(h)
    logger.addHandler(handler)

    class X:  # noqa: D401 - simple object for repr fallback
        pass

    from pmcc.jsonlog import log_event

    log_event(logger, "repr", weird=X())
    handler.flush()
    out = stream.getvalue().strip()
    obj = json.loads(out)
    assert obj.get("event") == "repr"
    assert isinstance(obj.get("weird"), str)  # fallback to repr string
