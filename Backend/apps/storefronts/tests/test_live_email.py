import os
from types import SimpleNamespace

import pytest
import resend

from services.email import EmailService


@pytest.mark.live_email
def test_send_real_branded_email(monkeypatch):
    """Send a real branded email when explicitly enabled by the caller."""
    if os.environ.get("RUN_LIVE_EMAIL_TESTS") != "1":
        pytest.skip("Set RUN_LIVE_EMAIL_TESTS=1 to enable real email delivery")

    recipient = os.environ.get("LIVE_EMAIL_RECIPIENT")
    if not recipient:
        pytest.fail("LIVE_EMAIL_RECIPIENT must be set for the live email test")
    recipient_domain = recipient.rpartition("@")[2].lower()
    if recipient_domain in {"example.com", "example.net", "example.org"}:
        pytest.fail(
            "LIVE_EMAIL_RECIPIENT must be your real inbox address, not the "
            f"placeholder {recipient!r}"
        )

    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        pytest.fail("RESEND_API_KEY must be configured for the live email test")

    # The test settings intentionally replace the provider key, so opt back into
    # the real environment key only inside this explicitly enabled test.
    monkeypatch.setattr(resend, "api_key", api_key)

    EmailService.send_template(
        subject="Storefront email logo delivery test",
        template_name="emails/welcome.html",
        context={"user": SimpleNamespace(first_name="Email tester")},
        recipients=[recipient],
    )
