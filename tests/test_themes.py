import pytest

from src.themes import identify_theme


@pytest.mark.parametrize(
    "review, expected_theme",
    [
        ("I cannot login and the OTP never arrives", "Account Access Issues"),
        ("Transfer failed and payment was delayed", "Transaction Performance"),
        ("The interface and layout are so clean", "UI & Design"),
        ("Customer support never responds to my complaint", "Customer Support"),
        ("Please add a dark mode feature in the next update", "Feature Requests"),
        ("This app is amazing overall", "Other"),
    ],
)
def test_identify_theme(review, expected_theme):
    assert identify_theme(review) == expected_theme


def test_identify_theme_is_case_insensitive():
    assert identify_theme("LOGIN ERROR EVERY TIME") == "Account Access Issues"


def test_identify_theme_first_match_wins_on_precedence():
    # Contains both an access keyword ("login") and a UI keyword ("design"):
    # Account Access Issues is defined first in THEME_KEYWORDS, so it wins.
    assert identify_theme("login page has a bad design") == "Account Access Issues"
