import os
import imaplib
import email as email_lib
from email.header import decode_header

# Set env vars: EMAIL_PASSWORD, and optionally EMAIL_IMAP_SERVER
# (defaults to Gmail's IMAP server).
def check_email(email_address: str, query: str):
    """
    Logs into the mailbox for `email_address` via IMAP and searches for
    messages matching `query` (searches subject and body).
    Returns a list of dicts with subject, from, date, and a snippet.
    """
    password = os.environ.get("EMAIL_PASSWORD")
    if not password:
        raise EnvironmentError("EMAIL_PASSWORD environment variable not set")

    imap_server = os.environ.get("EMAIL_IMAP_SERVER", "imap.gmail.com")

    results = []
    with imaplib.IMAP4_SSL(imap_server) as mail:
        mail.login(email_address, password)
        mail.select("inbox")

        search_criteria = f'(OR SUBJECT "{query}" BODY "{query}")'
        status, data = mail.search(None, search_criteria)
        if status != "OK":
            return results

        for num in data[0].split():
            status, msg_data = mail.fetch(num, "(RFC822)")
            if status != "OK":
                continue

            msg = email_lib.message_from_bytes(msg_data[0][1])

            subject, encoding = decode_header(msg.get("Subject", ""))[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8", errors="ignore")

            from_ = msg.get("From", "")
            date_ = msg.get("Date", "")

            snippet = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            snippet = payload.decode(errors="ignore")[:200]
                            break
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    snippet = payload.decode(errors="ignore")[:200]

            results.append({
                "subject": subject,
                "from": from_,
                "date": date_,
                "snippet": snippet,
            })

    return results