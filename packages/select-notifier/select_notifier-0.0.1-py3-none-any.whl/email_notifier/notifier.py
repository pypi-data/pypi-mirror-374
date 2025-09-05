from __future__ import annotations

import logging
import re
import smtplib
import ssl
import time
import unicodedata
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from smtplib import SMTPAuthenticationError
from typing import Callable, ContextManager, Protocol

# ----------------------------
# Logging
# ----------------------------
logger = logging.getLogger("select_notifier")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


# ----------------------------
# Errors
# ----------------------------
class EmailSendError(RuntimeError):
    """Raised when sending email fails after all retry attempts."""


# ----------------------------
# Config (SRP: فقط داده)
# ----------------------------
@dataclass(frozen=True)
class SMTPConfig:
    server: str
    port: int
    sender: str
    password: str
    use_tls: bool = True  # STARTTLS (587)
    use_ssl: bool = False  # SMTPS (465)
    timeout: float = 30.0


# ----------------------------
# SMTP factory protocol
# ----------------------------
class SMTPContextFactory(Protocol):
    def __call__(self, server: str, port: int, timeout: float) -> ContextManager[smtplib.SMTP]: ...


def _default_smtp_factory(
    server: str, port: int, timeout: float, *, use_ssl: bool
) -> ContextManager[smtplib.SMTP]:
    if use_ssl:
        return smtplib.SMTP_SSL(server, port, timeout=timeout)  # type: ignore[return-value]
    return smtplib.SMTP(server, port, timeout=timeout)  # type: ignore[return-value]


# ----------------------------
# Core Notifier (SRP + OCP + DIP)
# ----------------------------
class EmailNotifier:
    _EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def __init__(
        self,
        config: SMTPConfig,
        *,
        smtp_factory: Callable[[str, int, float], ContextManager[smtplib.SMTP]] | None = None,
    ) -> None:
        norm_pwd = self._normalize_secret(config.password)
        object.__setattr__(config, "password", norm_pwd)

        self._cfg = config
        if smtp_factory is None:
            self._smtp_factory = lambda host, port, timeout: _default_smtp_factory(
                host, port, timeout, use_ssl=config.use_ssl
            )
        else:
            self._smtp_factory = smtp_factory

    # ---------- Public API ----------
    def send_email(
        self,
        to: str,
        subject: str,
        body_text: str,
        *,
        retries: int = 2,
        backoff: float = 1.5,
    ) -> None:
        self._validate_email(self._cfg.sender, "sender")
        self._validate_email(to, "recipient")

        if not subject or not isinstance(subject, str):
            raise ValueError("Subject must be a non-empty string.")
        if body_text is None or not isinstance(body_text, str) or not body_text.strip():
            raise ValueError("Body text must be a non-empty string.")
        if retries < 0:
            raise ValueError("retries must be >= 0.")
        if backoff <= 0:
            raise ValueError("backoff must be > 0.")

        msg = self._build_text_message(self._cfg.sender, to, subject, body_text)

        attempt = 0
        last_err: Exception | None = None

        while attempt <= retries:
            attempt += 1
            try:
                logger.info("Sending email (attempt %d/%d) to %s", attempt, retries + 1, to)

                context = ssl.create_default_context()
                with self._smtp_factory(
                    self._cfg.server, self._cfg.port, self._cfg.timeout
                ) as smtp:
                    smtp.ehlo()
                    if self._cfg.use_tls and not self._cfg.use_ssl:
                        smtp.starttls(context=context)
                        smtp.ehlo()
                    smtp.login(self._cfg.sender, self._cfg.password)
                    smtp.send_message(msg)

                logger.info("Email sent successfully to %s", to)
                return

            except SMTPAuthenticationError as e:
                last_err = e
                logger.warning(
                    "SMTP auth failed (attempt %d): %s. "
                    "Check username/password (Gmail: App Password, no spaces).",
                    attempt,
                    e,
                )
                if attempt > retries:
                    break
                sleep_s = backoff**attempt
                logger.info("Retrying in %.2f seconds...", sleep_s)
                time.sleep(sleep_s)

            except (smtplib.SMTPException, OSError) as e:
                last_err = e
                logger.warning("SMTP send failed (attempt %d): %r", attempt, e)
                if attempt > retries:
                    break
                sleep_s = backoff**attempt
                logger.info("Retrying in %.2f seconds...", sleep_s)
                time.sleep(sleep_s)

        raise EmailSendError(
            f"Failed to send email to {to!r} via {self._cfg.server}:{self._cfg.port} after {attempt} attempts."
        ) from last_err

    # ---------- Private helpers ----------
    @staticmethod
    def _validate_email(addr: str, label: str) -> None:
        if not addr or not EmailNotifier._EMAIL_RE.match(addr):
            raise ValueError(f"Invalid {label} email address: {addr!r}")

    @staticmethod
    def _normalize_secret(secret: str) -> str:
        s = "".join(ch for ch in secret if not ch.isspace())
        s = "".join(
            str(unicodedata.digit(ch)) if ch.isdigit() and not ch.isascii() else ch for ch in s
        )
        return s

    @staticmethod
    def _build_text_message(sender: str, to: str, subject: str, body_text: str) -> EmailMessage:
        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = to
        msg["Subject"] = subject
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid()
        msg.set_content(body_text)
        return msg

    # ---------- Factory method ----------
    @classmethod
    def create(
        cls,
        *,
        sender: str,
        password: str,
        server: str,
        port: int,
        use_tls: bool = True,
        use_ssl: bool = False,
        timeout: float = 30.0,
    ) -> EmailNotifier:
        cfg = SMTPConfig(
            server=server,
            port=port,
            sender=sender,
            password=password,
            use_tls=use_tls,
            use_ssl=use_ssl,
            timeout=timeout,
        )
        return cls(cfg)
