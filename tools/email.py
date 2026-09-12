import imaplib
import os
from typing import List

from settings import settings
from services.email.client import Account,EmailSummary,GmailClient


def load_accounts_from_env() -> List[Account]:
    accounts = []
    for entry in filter(None, (e.strip() for e in settings.GMAIL_ACCOUNTS.split(","))):
        parts = entry.split(":")
        if len(parts) == 3:
            label, address, password = parts
        elif len(parts) == 2:
            label, (address, password) = "", parts
        else:
            print(f"WARNING: Skipping malformed account entry: {entry}")
            continue
        accounts.append(Account(address=address, app_password=password, label=label))
    print("accounts: ", accounts)
    return accounts


def fetch_all(accounts: List[Account], limit: int = 10) -> List[EmailSummary]:

    all_summaries: List[EmailSummary] = []
    for account in accounts:
        try:
            with GmailClient(account) as client:
                summaries = client.fetch_recent(limit=limit)
                all_summaries.extend(summaries)
                print(f"INFO: Fetched {len(summaries)} emails from {account.display_name}")
        except imaplib.IMAP4.error as e:
            print(f"ERROR: Auth/IMAP error for {account.display_name}: {e} (use an App Password, not your login password)")
        except Exception as e:
            print(f"ERROR: Failed to fetch from {account.display_name}: {e}")
    return all_summaries


def format_summaries(summaries: List[EmailSummary]) -> str:
    lines = []
    for s in summaries:
        lines.append(f"\nemail From: {s.sender}")
        lines.append(f"  on Subject: {s.subject}")
        lines.append(f"  at : {s.date}")
    return "\n".join(lines)


def check_email(limit: int = 5):
    accounts = load_accounts_from_env()
 
    if not accounts:
        return "No accounts configured"
    else:
        results = fetch_all(accounts, limit)
        ans = format_summaries(results)
        return ans