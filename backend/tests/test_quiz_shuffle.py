from app.routers.quizzes import _option_map, _shuffle_rows


def rows():
    return [dict(id=i, option_a="Alpha", option_b="Beta", option_c="Gamma", option_d="Delta", correct_answer="B", chosen="B") for i in range(1, 9)]


def test_shuffle_is_stable_and_keeps_correct_content():
    source = rows()
    shuffled = _shuffle_rows(source, 123)
    assert shuffled == _shuffle_rows(source, 123)
    assert source == rows()
    assert {q["id"] for q in shuffled} == set(range(1, 9))
    for q in shuffled:
        assert q[f"option_{q['correct_answer'].lower()}"] == "Beta"
        assert _option_map(q, 123)[q["chosen"]] == "B"


def test_new_attempt_changes_order():
    assert _shuffle_rows(rows(), 123) != _shuffle_rows(rows(), 124)


def test_two_options_remain_two():
    q = dict(id=1, option_a="Đúng", option_b="Sai", option_c=None, option_d="", correct_answer="A")
    result = _shuffle_rows([q], 123)[0]
    assert {result["option_a"], result["option_b"]} == {"Đúng", "Sai"}
    assert result["option_c"] is None and result["option_d"] == ""
    assert result[f"option_{result['correct_answer'].lower()}"] == "Đúng"
