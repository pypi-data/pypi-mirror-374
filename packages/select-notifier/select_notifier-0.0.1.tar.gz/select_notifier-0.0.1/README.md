## Name

**Select-Notifier: Lightweight Email Notification Module**

---

## Description

**Select-Notifier** is a small, production-friendly Python module that sends emails over SMTP with robust input validation, STARTTLS/SSL support, and built‑in retry/backoff handling. It is designed to be embedded inside Select services and pipelines where a simple, reliable notifier is needed.

Core component: `EmailNotifier` (in `src/email_notifier/notifier.py`).

---

## Badges

On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project.  
You can use [Shields.io](https://shields.io) to add badges. Many services also have instructions for adding a badge.

---

## Visuals

Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos).  
Tools like `ttygif` can help, but check out [Asciinema](https://asciinema.org) for a more sophisticated method.

---

## Features

```text
✅ SMTP + Authentication:
    - STARTTLS (587) and SMTPS/SSL (465)

✅ Robust Error Handling:
    - Retries with exponential backoff
    - Specific catch for SMTPAuthenticationError
    - Clear, actionable log messages

✅ Input Validation & Hygiene:
    - Email address validation for sender/recipient
    - Subject/body non-empty checks
    - Password normalization:
        • Removes whitespace
        • Converts non-ASCII digits (e.g., Persian ۰-۹) to ASCII

✅ Minimal Dependencies:
    - Standard library only for runtime
    - Dev/test tools isolated in dev requirements
```

---

## Repository Structure

```text
select-notifier/
├── src/
│   └── email_notifier/
│       ├── __init__.py
│       ├── __version__.py
│       ├── CHANGELOG.md
│       └── notifier.py          # notifier implementation
├── tests/
│   └── test_notifier.py         # Unit tests (pytest)
├── version_and_changelog.py           # Version bump + changelog generator
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

---

## Installation

1) Clone the repository:
```bash
git clone http://repo.afe.ir/afeai/select-notifier.git
cd select-notifier
```

2. Create virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate    # Linux/Mac
.venv\Scripts\activate     # Windows
```

3) Install requirements:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4) (Recommended) Install pre-commit hooks:
```bash
pre-commit install
pre-commit run --all-files
```

---

## Usage

### Quick Start (STARTTLS, port 587)
```python
from email_notifier.notifier import EmailNotifier

notifier = EmailNotifier.create(
    sender="noreply@example.com",
    password="your-app-password",  # App Password for Gmail/Outlook (no spaces)
    server="smtp.example.com",
    port=587,
    use_tls=True,
    use_ssl=False,
    timeout=30.0,
)

notifier.send_email(
    to="user@dest.com",
    subject="Hello from select-notifier",
    body_text="This is a test message from Select Notifier."
)
```

### SSL (SMTPS, port 465)
```python
from email_notifier.notifier import EmailNotifier

notifier = EmailNotifier.create(
    sender="noreply@example.com",
    password="your-app-password",
    server="smtp.example.com",
    port=465,
    use_tls=False,
    use_ssl=True,
    timeout=30.0,
)

notifier.send_email("user@dest.com", "Subject", "Body")
```

**Notes**
- For Gmail, use an **App Password** (no spaces) and ensure “Less secure apps” is not required.
- The module normalizes secrets by stripping whitespace and converting non-ASCII digits to ASCII digits.
- `send_email(..., retries=2, backoff=1.5)` controls retry behavior (`sleep = backoff ** attempt`).

---

## Configuration

There is no required configuration file. Supply SMTP details programmatically via `EmailNotifier.create(...)`. Key options:
- `use_tls` (STARTTLS) vs `use_ssl` (SMTPS)
- `timeout` (socket timeout in seconds)
- `retries` / `backoff` in `send_email`

You can wrap access to credentials by your own config manager or environment loader as needed.

---

## Testing

Run unit tests with pytest:
```bash
pytest -q --disable-warnings
```

The test suite covers:
- TLS vs SSL paths
- Retry/backoff logic
- Authentication failures (`SMTPAuthenticationError`)
- Password normalization (whitespace & Persian digits)
- Input validation (addresses, subject/body, retries/backoff)
- Email message headers & content

---

## Versioning & Changelog

We follow **Semantic Versioning (SemVer)**.

- Single source of truth for package version:
  ```text
  src/email_notifier/__version__.py
  ```

- CHANGELOG is kept **next to the package**:
  ```text
  src/email_notifier/CHANGELOG.md
  ```

- Use the helper to bump and generate changelog:
  ```bash
  # examples
  python version_and_changelog.py notifier --bump patch
  python version_and_changelog.py select-notifier --bump minor

  # skip changelog generation if needed
  python version_and_changelog.py notifier --bump patch --no-changelog
  ```

- Initial version is created automatically as **0.0.1** if missing.

For full policy, see `versioning_strategy.md` (Versioning Strategy).

---

## License

**Private Repository:**  
This codebase is private and currently not distributed under any open-source license.  
Contact the project owner for more information or collaboration requests.

---

## Contact

For questions, ideas, or collaboration, please reach out to the project maintainer.

---

## Project Status

**Under Development:**  
This project is still evolving. While core functionalities are operational, enhancements and stability improvements are ongoing.
