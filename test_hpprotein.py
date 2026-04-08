from helper.hpprotein import verify as verify_hpprotein


def test_hpprotein_warmup_valid_snake():
    # Warm-up shape from problem statement with 2 contacts.
    coords = [[0, 0], [1, 0], [1, 1], [0, 1], [0, 2], [1, 2]]
    result = verify_hpprotein(
        instance={"sequence_id": "WARMUP_6H"},
        submission={"lattice": "2D", "coords": coords},
        current_record=2,
    )
    assert result["is_valid"] is True
    assert result["score"] == 2
    assert result["is_record"] is False


def test_hpprotein_reject_proven_optimal_instance_s1():
    # S1-S4 are intentionally excluded from allowed instances.
    coords = [[i, 0] for i in range(20)]
    result = verify_hpprotein(
        instance={"sequence_id": "S1"},
        submission={"lattice": "2D", "coords": coords},
    )
    assert result["is_valid"] is False
    assert result["error_code"] == "INVALID_INSTANCE"


def test_hpprotein_valid_open_instance_linear_fold():
    # A straight line is a valid self-avoiding walk; contacts can be zero.
    coords = [[i, 0] for i in range(48)]
    result = verify_hpprotein(
        instance={"sequence_id": "S5"},
        submission={"coords": coords},
    )
    assert result["is_valid"] is True
    assert isinstance(result["score"], int)


def test_hpprotein_reject_duplicate_coordinate():
    coords = [[0, 0], [1, 0], [1, 1], [0, 1], [0, 1], [1, 2]]
    result = verify_hpprotein(
        instance={"sequence_id": "WARMUP_6H"},
        submission={"coords": coords},
    )
    assert result["is_valid"] is False
    assert result["error_code"] == "VERIFICATION_FAILED"


def test_hpprotein_reject_broken_connectivity():
    coords = [[0, 0], [1, 0], [2, 0], [4, 0], [5, 0], [6, 0]]
    result = verify_hpprotein(
        instance={"sequence_id": "WARMUP_6H"},
        submission={"coords": coords},
    )
    assert result["is_valid"] is False
    assert result["error_code"] == "VERIFICATION_FAILED"


def test_hpprotein_record_detection():
    coords = [[0, 0], [1, 0], [1, 1], [0, 1], [0, 2], [1, 2]]
    result = verify_hpprotein(
        instance={"sequence_id": "WARMUP_6H"},
        submission={"coords": coords},
        current_record=1,
    )
    assert result["is_valid"] is True
    assert result["is_record"] is True
