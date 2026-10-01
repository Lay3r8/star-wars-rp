import pytest

from star_wars_rp.modules.custom_d20.rules import resolve_check


def test_resolve_check_success_and_failure():
    assert resolve_check(12, 3, 15) == (15, True)
    assert resolve_check(11, 3, 15) == (14, False)


@pytest.mark.parametrize("natural", [0, 21])
def test_resolve_check_rejects_non_d20_values(natural):
    with pytest.raises(ValueError):
        resolve_check(natural, 0, 10)
