from __future__ import annotations

import email
import imaplib
from dataclasses import dataclass
from email.header import decode_header
from email.message import Message
from typing import List, Optional
from dateutil import parser
from settings import settings

@dataclass(frozen=True)
class Account:
    address: str
    app_password: str
    label: str = ""

    @property
    def display_name(self) -> str:
        return self.label or self.address


@dataclass(frozen=True)
class EmailSummary:
    account: str
    sender: str
    subject: str
    date: str


class GmailClient:

    def __init__(self, account: Account, folder: str = "INBOX"):
        self.account = account
        self.folder = folder
        self._conn: Optional[imaplib.IMAP4_SSL] = None

    def __enter__(self) -> "GmailClient":
        self._conn = imaplib.IMAP4_SSL(settings.IMAP_HOST, settings.IMAP_PORT)
        self._conn.login(self.account.address, self.account.app_password)
        self._conn.select(self.folder)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._conn is not None:
            try:
                self._conn.logout()
            except Exception:
                pass

    def fetch_recent(self, limit: int = 10) -> List[EmailSummary]:
        status, data = self._conn.search(None, "ALL")
        if status != "OK":
            raise RuntimeError(f"IMAP search failed for {self.account.address}")

        ids = data[0].split()[-limit:]
        summaries = []
        for msg_id in reversed(ids):
            status, msg_data = self._conn.fetch(msg_id, "(RFC822)")
            if status != "OK":
                continue
            msg = email.message_from_bytes(msg_data[0][1])
            summaries.append(self._to_summary(msg))
        return summaries

    def _to_summary(self, msg: Message) -> EmailSummary:
        return EmailSummary(
            account= self.account.display_name,
            sender= self._decode(msg.get("From", "Unknown Sender")),
            subject= self._decode(msg.get("Subject", "(No Subject)")),
            date= self._extract_date_and_time(msg.get("Date", "")),
        )

    @staticmethod
    def _decode(header_value: str) -> str:
        parts = decode_header(header_value)
        return "".join(
            part.decode(enc or "utf-8", errors="replace") if isinstance(part, bytes) else part
            for part, enc in parts
        )

    @staticmethod
    def _extract_date_and_time(timestamp_str: str):
        dt = parser.parse(timestamp_str, fuzzy=True)
        date = dt.strftime("%d %b %Y")
        time = dt.strftime("%H:%M:%S")
        return f"{date} {time}"