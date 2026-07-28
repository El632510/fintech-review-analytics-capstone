
from src.config import BANK_ID_BY_NAME, BANKS, DBConfig


def test_three_banks_configured_with_unique_app_ids():
    assert len(BANKS) == 3
    app_ids = {bank.app_id for bank in BANKS}
    assert len(app_ids) == 3  # no duplicate app IDs


def test_bank_id_mapping_is_1_indexed_and_matches_banks():
    assert set(BANK_ID_BY_NAME.values()) == {1, 2, 3}
    for bank in BANKS:
        assert bank.display_name in BANK_ID_BY_NAME


def test_db_config_reads_from_environment(monkeypatch):
    monkeypatch.setenv("DB_HOST", "test-host")
    monkeypatch.setenv("DB_PORT", "6543")
    monkeypatch.setenv("DB_NAME", "test_db")
    monkeypatch.setenv("DB_USER", "test_user")
    monkeypatch.setenv("DB_PASSWORD", "test_pw")

    config = DBConfig()

    assert config.host == "test-host"
    assert config.port == 6543
    assert config.database == "test_db"
    assert config.user == "test_user"
    assert config.password == "test_pw"


def test_db_config_never_hardcodes_a_password():
    # Regression guard for the plaintext password previously committed
    # inside database_insertion.ipynb (password="E@1992").
    config = DBConfig()
    assert config.password != "E@1992"
