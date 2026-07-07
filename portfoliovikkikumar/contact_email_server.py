from email.message import EmailMessage
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import smtplib
from urllib.parse import parse_qs


HOST = "127.0.0.1"
PORT = 8001


def get_field(form_data, name):
    value = form_data.get(name, [""])[0].strip()
    return value


def send_contact_email(name, email, service, message):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    email_to = os.getenv("EMAIL_TO", "vikki@example.com")
    email_from = os.getenv("EMAIL_FROM", smtp_user or "portfolio@example.com")

    if not smtp_host or not smtp_user or not smtp_password:
        raise RuntimeError(
            "Email settings missing. Set SMTP_HOST, SMTP_PORT, SMTP_USER, "
            "SMTP_PASSWORD, EMAIL_FROM, and EMAIL_TO."
        )

    email_body = f"""
New portfolio contact form message

Name: {name}
Email: {email}
Service: {service}

Message:
{message}
""".strip()

    msg = EmailMessage()
    msg["Subject"] = f"New portfolio enquiry from {name}"
    msg["From"] = email_from
    msg["To"] = email_to
    msg["Reply-To"] = email
    msg.set_content(email_body)

    if smtp_port == 465:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
    else:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)


def response_page(title, message):
    safe_title = escape(title)
    safe_message = escape(message)
    return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{safe_title}</title>
    <style>
        body {{
            min-height: 100vh;
            margin: 0;
            display: grid;
            place-items: center;
            font-family: Arial, sans-serif;
            color: #f8fafc;
            background: linear-gradient(135deg, #08111f, #05070d);
        }}
        main {{
            width: min(92%, 560px);
            padding: 34px;
            border: 1px solid rgba(255, 255, 255, 0.14);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.06);
        }}
        h1 {{
            margin: 0 0 14px;
            color: #d8b568;
        }}
        p {{
            line-height: 1.7;
        }}
        a {{
            color: #d8b568;
            font-weight: 700;
        }}
    </style>
</head>
<body>
    <main>
        <h1>{safe_title}</h1>
        <p>{safe_message}</p>
        <a href="javascript:history.back()">Back to portfolio</a>
    </main>
</body>
</html>"""


class ContactHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/send-email":
            self.send_error(404, "Page not found")
            return

        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length).decode("utf-8")
        form_data = parse_qs(raw_body)

        name = get_field(form_data, "name")
        email = get_field(form_data, "email")
        service = get_field(form_data, "service")
        message = get_field(form_data, "message")

        if not name or not email or not service or not message:
            self.send_html(400, response_page("Missing Details", "Please fill all form fields and try again."))
            return

        try:
            send_contact_email(name, email, service, message)
        except Exception as exc:
            self.send_html(
                500,
                response_page(
                    "Email Not Sent",
                    f"Your form was received, but email sending failed: {exc}",
                ),
            )
            return

        self.send_html(200, response_page("Message Sent", "Thank you. Your message has been sent successfully."))

    def do_GET(self):
        self.send_html(200, response_page("Contact Email Server", "The Python email server is running. Submit the contact form to send an email."))

    def send_html(self, status_code, html):
        body = html.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print(f"Contact email server running at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop.")
    HTTPServer((HOST, PORT), ContactHandler).serve_forever()
