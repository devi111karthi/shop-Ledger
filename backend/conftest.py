# ============================================================
# ShopLedger — pytest configuration
# File: backend/conftest.py
# Purpose: redirect test_app.py to the TEST database and stop
#          real emails from being sent during test runs.
# ============================================================

import pytest


@pytest.fixture(autouse=True)
def use_test_database(monkeypatch):
    """
    Automatically applied to every test.
    Points app.DB_CONFIG at 'shopledger_test' instead of the real
    'shopledger' database, so tests never touch production data.
    """
    import app as app_module
    monkeypatch.setitem(app_module.DB_CONFIG, "database", "shopledger_test")


@pytest.fixture(autouse=True)
def disable_real_emails(monkeypatch):
    """
    Automatically applied to every test.
    Prevents any test from sending a real email via Gmail SMTP
    (login summary, restock alerts, low-stock alerts, manual alerts).
    """
    import app as app_module

    def fake_send(*args, **kwargs):
        print("   📭 (email sending skipped in tests)")

    monkeypatch.setattr(app_module, "send_login_summary", fake_send, raising=False)
    monkeypatch.setattr(app_module, "send_restock_alert", fake_send, raising=False)
    monkeypatch.setattr(app_module, "send_low_stock_alert", fake_send, raising=False)

    # login() starts a background Thread(target=send_login_summary) —
    # patching send_login_summary above covers that call.
