import smtplib
from smtplib import SMTPAuthenticationError

import pytest

from email_notifier.notifier import EmailNotifier, EmailSendError, SMTPConfig


# -----------------------------
# Test doubles (fakes/spies)
# -----------------------------
class FakeSMTPBase:
    """A context-manager compatible fake for smtplib.SMTP / SMTP_SSL."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.ehlo_called = 0
        self.starttls_called = False
        self.login_calls = []
        self.sent_messages = []
        self.raise_on = {}  # {"login": Exception, "send_message": Exception}
        self.closed = False

    # context manager
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.closed = True

    # smtp methods used by EmailNotifier
    def ehlo(self):
        self.ehlo_called += 1

    def starttls(self, context=None):
        self.starttls_called = True

    def login(self, user, password):
        exc = self.raise_on.get("login")
        if exc:
            # support call-by-call progression (list of exceptions)
            if isinstance(exc, list) and exc:
                to_raise = exc.pop(0)
                if to_raise is not None:
                    raise to_raise
            else:
                raise exc
        self.login_calls.append((user, password))

    def send_message(self, msg):
        exc = self.raise_on.get("send_message")
        if exc:
            if isinstance(exc, list) and exc:
                to_raise = exc.pop(0)
                if to_raise is not None:
                    raise to_raise
            else:
                raise exc
        self.sent_messages.append(msg)


class FakeSMTP(FakeSMTPBase):
    pass


class FakeSMTP_SSL(FakeSMTPBase):
    pass


# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def cfg_tls():
    return SMTPConfig(
        server="smtp.example.com",
        port=587,
        sender="noreply@example.com",
        password=" 12۳ 4  ",  # contains spaces + Persian digit ۳ to test normalization
        use_tls=True,
        use_ssl=False,
        timeout=5.0,
    )


@pytest.fixture
def cfg_ssl():
    return SMTPConfig(
        server="smtp.example.com",
        port=465,
        sender="noreply@example.com",
        password=" ab ۹  0 ",
        use_tls=False,
        use_ssl=True,
        timeout=5.0,
    )


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    # avoid real delays from backoff
    monkeypatch.setattr("time.sleep", lambda *_: None)


# -----------------------------
# Tests
# -----------------------------
def test_send_email_success_tls(monkeypatch, cfg_tls):
    smtp_instance = FakeSMTP()
    monkeypatch.setattr("smtplib.SMTP", lambda *a, **k: smtp_instance)

    notifier = EmailNotifier(cfg_tls)
    notifier.send_email("user@dest.com", "Hello", "Body")

    # TLS path: starttls used, SMTP_SSL not used
    assert smtp_instance.starttls_called is True
    assert len(smtp_instance.login_calls) == 1
    user, pwd = smtp_instance.login_calls[0]
    assert user == cfg_tls.sender
    # password should be normalized: spaces removed and non-ascii digits converted (۳ -> 3)
    assert pwd == "1234"
    assert len(smtp_instance.sent_messages) == 1
    msg = smtp_instance.sent_messages[0]
    assert msg["From"] == cfg_tls.sender
    assert msg["To"] == "user@dest.com"
    assert msg["Subject"] == "Hello"


def test_send_email_success_ssl(monkeypatch, cfg_ssl):
    smtp_ssl_instance = FakeSMTP_SSL()
    monkeypatch.setattr("smtplib.SMTP_SSL", lambda *a, **k: smtp_ssl_instance)

    notifier = EmailNotifier(cfg_ssl)
    notifier.send_email("u@d.com", "S", "B")

    # SSL path: no STARTTLS
    assert smtp_ssl_instance.starttls_called is False
    assert len(smtp_ssl_instance.login_calls) == 1
    assert smtp_ssl_instance.sent_messages, "message should be sent via SSL"


@pytest.mark.parametrize(
    "bad_sender,bad_to",
    [
        ("bad_sender", "ok@x.com"),
        ("ok@x.com", "bad to"),
    ],
)
def test_invalid_email_addresses_raise(monkeypatch, cfg_tls, bad_sender, bad_to):
    # patch SMTP to avoid network even if validation fails later
    monkeypatch.setattr("smtplib.SMTP", lambda *a, **k: FakeSMTP())

    # mutate sender or recipient and expect ValueError
    cfg = cfg_tls
    cfg = SMTPConfig(
        server=cfg.server,
        port=cfg.port,
        sender=bad_sender,
        password=cfg.password,
        use_tls=cfg.use_tls,
        use_ssl=cfg.use_ssl,
        timeout=cfg.timeout,
    )
    notifier = EmailNotifier(cfg)

    if bad_sender != "ok@x.com":
        with pytest.raises(ValueError):
            notifier.send_email("ok@x.com", "s", "b")
    else:
        with pytest.raises(ValueError):
            notifier.send_email(bad_to, "s", "b")


@pytest.mark.parametrize(
    "subject,body,err_type",
    [
        ("", "body", ValueError),
        ("S", "   ", ValueError),
        ("S", None, ValueError),
    ],
)
def test_input_validation_subject_body(subject, body, err_type, cfg_tls):
    notifier = EmailNotifier(cfg_tls)
    with pytest.raises(err_type):
        notifier.send_email("a@b.com", subject, body)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "retries,backoff,err",
    [
        (-1, 1.0, ValueError),
        (0, 0.0, ValueError),
        (1, -2.0, ValueError),
    ],
)
def test_input_validation_retries_backoff(cfg_tls, retries, backoff, err):
    notifier = EmailNotifier(cfg_tls)
    with pytest.raises(err):
        notifier.send_email("a@b.com", "S", "B", retries=retries, backoff=backoff)


def test_retry_then_success_on_smtp_exception(monkeypatch, cfg_tls):
    fake = FakeSMTP()
    # First send_message fails, second succeeds
    fake.raise_on["send_message"] = [smtplib.SMTPException("temp"), None]
    created = []

    def smtp_ctor(*a, **k):
        # a *new* instance each attempt (like real smtplib.SMTP)
        inst = FakeSMTP()
        inst.raise_on = dict(fake.raise_on)
        created.append(inst)
        return inst

    monkeypatch.setattr("smtplib.SMTP", smtp_ctor)

    notifier = EmailNotifier(cfg_tls)
    notifier.send_email("x@y.com", "S", "B", retries=2, backoff=1.1)

    # We expect 2 attempts (first failed, second succeeded)
    assert len(created) == 2
    assert created[-1].sent_messages, "second attempt should succeed"


def test_retry_auth_failure_then_give_up(monkeypatch, cfg_tls):
    # Always fail on login with SMTPAuthenticationError
    def smtp_ctor(*a, **k):
        inst = FakeSMTP()
        inst.raise_on["login"] = SMTPAuthenticationError(535, b"Auth failed")
        return inst

    monkeypatch.setattr("smtplib.SMTP", smtp_ctor)

    notifier = EmailNotifier(cfg_tls)
    with pytest.raises(EmailSendError) as ei:
        notifier.send_email("x@y.com", "S", "B", retries=1, backoff=1.2)

    assert "Failed to send email" in str(ei.value)


def test_message_headers_shape_without_network(monkeypatch, cfg_tls):
    fake = FakeSMTP()
    monkeypatch.setattr("smtplib.SMTP", lambda *a, **k: fake)
    notifier = EmailNotifier(cfg_tls)

    notifier.send_email("u@d.com", "Subject", "Body")
    msg = fake.sent_messages[0]

    # Has standard headers
    assert msg["Date"]
    assert msg["Message-ID"]
    # payload content
    payload = msg.get_content()
    assert "Body" in payload


def test_factory_create_builds_config_and_uses_ssl(monkeypatch):
    # Ensure .create wires config and use_ssl path
    ssl_fake = FakeSMTP_SSL()
    monkeypatch.setattr("smtplib.SMTP_SSL", lambda *a, **k: ssl_fake)

    notifier = EmailNotifier.create(
        sender="noreply@example.com",
        password=" ۱۲ 3 ",  # includes Persian ۱۲
        server="smtp.example.com",
        port=465,
        use_tls=False,
        use_ssl=True,
        timeout=10.0,
    )
    notifier.send_email("a@b.com", "S", "B")

    # no starttls in SSL mode
    assert ssl_fake.starttls_called is False
    # password normalized: "۱۲3" -> "123"
    user, pwd = ssl_fake.login_calls[0]
    assert pwd == "123"
