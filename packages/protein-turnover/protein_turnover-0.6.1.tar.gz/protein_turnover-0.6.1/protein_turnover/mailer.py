from __future__ import annotations

import smtplib
from email.mime.text import MIMEText
from typing import Literal


def sendmail(
    html: str,
    you: str,
    *,
    me: str | None = None,
    replyto: str | list[str] | None = None,
    mailhost: str | None = None,
    subject: str | None = None,
    mimetype: Literal["html", "plain"] = "html",
    timeout: float = 20.0,
) -> bool:
    from . import config

    if mailhost is None:
        mailhost = config.MAIL_SERVER

    if mailhost is None or mailhost == "none":
        return False

    if subject is None:
        subject = config.MAIL_SUBJECT

    if me is None:
        me = config.MAIL_SENDER

    msg = MIMEText(html, mimetype)

    msg["Subject"] = subject
    msg["From"] = me
    msg["To"] = you
    if replyto is not None:
        msg["Reply-To"] = replyto if isinstance(replyto, str) else ",".join(replyto)

    with smtplib.SMTP(timeout=timeout) as s:
        s.connect(mailhost)
        s.sendmail(me, [you], msg.as_string())

    return True
