import smtplib
from email.message import EmailMessage

import config as app_config


def send_report(html_path: str, subject: str, recipients: list[str] | None = None) -> None:
    recipients = recipients if recipients is not None else app_config.REPORT_RECIPIENTS
    recipients = [r for r in recipients if r]

    with open(html_path, "r", encoding="utf-8") as f:
        html_body = f.read()

    if app_config.DRY_RUN or not recipients:
        print(f"[DRY RUN] Would send '{subject}' to {', '.join(recipients) or '(no recipients configured)'}")
        return

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = app_config.REPORT_SENDER
    message["To"] = ", ".join(recipients)
    message.set_content("This report requires an HTML-capable email client.")
    message.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(app_config.SMTP_HOST, app_config.SMTP_PORT) as server:
        server.starttls()
        server.login(app_config.SMTP_USERNAME, app_config.SMTP_PASSWORD)
        server.send_message(message)

    print(f"Sent '{subject}' to {', '.join(recipients)}")
