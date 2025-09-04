from pmcc.risk import check_cushion


def base_cushion():
    return {"hard_floor": 0.15, "target_range": [0.2, 0.3]}


def test_block_when_below_hard_floor():
    c = base_cushion()
    r = check_cushion(c, current=0.10)
    assert r["status"] == "block"
    assert r["hard_floor"] == 0.15
    assert r["target_range"] == [0.2, 0.3]


def test_warn_when_between_floor_and_lo():
    c = base_cushion()
    r = check_cushion(c, current=0.18)
    assert r["status"] == "warn"


def test_ok_when_within_range():
    c = base_cushion()
    r = check_cushion(c, current=0.25)
    assert r["status"] == "ok"


def test_warn_when_above_hi():
    c = base_cushion()
    r = check_cushion(c, current=0.35)
    assert r["status"] == "warn"


def test_invalid_target_range_raises():
    c = {"hard_floor": 0.15, "target_range": [0.3, 0.2]}
    try:
        check_cushion(c, current=0.25)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_invalid_hard_floor_raises():
    c = {"hard_floor": "bad", "target_range": [0.2, 0.3]}
    try:
        check_cushion(c, current=0.25)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_invalid_target_range_non_list_raises():
    # target_range must be a list of length 2; tuple should raise
    c = {"hard_floor": 0.15, "target_range": (0.2, 0.3)}
    try:
        check_cushion(c, current=0.25)
        assert False, "expected ValueError"
    except ValueError:
        pass
