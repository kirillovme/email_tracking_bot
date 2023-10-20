from email import message_from_string
from email.header import decode_header
from typing import Any

from bs4 import BeautifulSoup


class EmailDecoder:
    """Класс для декодирования email сообщений."""

    @classmethod
    def decode_email(cls, email_params: dict[str, str]) -> dict[str, Any]:
        """Декодирует переданные параметры письма."""
        decoded_params = {
            'Subject': cls._decode_subject(email_params.get('Subject', '')),
            'From': cls._decode_sender(email_params.get('From', '')),
            'To': cls._decode_recipient(email_params.get('To', '')),
            'Date': cls._decode_date(email_params.get('Date', '')),
            'Body': cls._decode_body(email_params.get('Body', ''))
        }
        return decoded_params

    @staticmethod
    def _decode_subject(encoded_str: str) -> str:
        """Декодирует тему письма."""
        return EmailDecoder.decode_mime_string(encoded_str)

    @staticmethod
    def _decode_sender(encoded_str: str) -> str:
        """Декодирует отправителя письма"""
        return EmailDecoder.decode_email_header(encoded_str)

    @staticmethod
    def _decode_recipient(encoded_str: str) -> str:
        """Декодирует получателя письма."""
        return EmailDecoder.decode_email_header(encoded_str)

    @staticmethod
    def _decode_date(encoded_str: str) -> str:
        """Декодирует дату письма."""
        return EmailDecoder.decode_mime_string(encoded_str)

    @staticmethod
    def _decode_body(encoded_str: str) -> dict[str, Any]:
        """Декодирует тело письма."""
        email_message = message_from_string(encoded_str)
        text_content = ''
        html_content = ''
        attachment_names = []
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get('Content-Disposition'))
                if 'attachment' in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        attachment_names.append(filename)
                else:
                    if content_type == 'text/html':
                        html_content = part.get_payload(decode=True).decode(part.get_content_charset())
                    elif content_type == 'text/plain':
                        text_content = part.get_payload(decode=True).decode(part.get_content_charset())
        else:
            text_content = email_message.get_payload(decode=True).decode(email_message.get_content_charset())
        if not text_content and html_content:
            soup = BeautifulSoup(html_content, 'html.parser')
            text_content = soup.get_text()
        return {
            'text_body': text_content,
            'html_body': html_content,
            'attachment_names': attachment_names
        }

    @staticmethod
    def decode_mime_string(encoded_str: str) -> str:
        """Декодирует MIME строку."""
        decoded_list = decode_header(encoded_str)
        decoded_string = ''.join(
            [t[0].decode(t[1] or 'ascii') if isinstance(t[0], bytes) else t[0] for t in decoded_list])
        return decoded_string

    @staticmethod
    def decode_email_header(encoded_str: str) -> str:
        """Декодирует заголовки письма."""
        parts = encoded_str.split(' <')
        if len(parts) == 2:
            name = EmailDecoder.decode_mime_string(parts[0])
            email = parts[1].rstrip('>')
            return name + ' <' + email + '>'
        else:
            return EmailDecoder.decode_mime_string(encoded_str)

    @staticmethod
    def email_to_html(email_data: dict[str, Any]) -> str:
        """Конвертирует данные пиьсма в HTML формат."""
        return f"""
                <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            padding: 20px;
                        }}
                        .email-header {{
                            background-color: #f2f2f2;
                            padding: 10px;
                            margin-bottom: 20px;
                        }}
                        .email-body {{
                            margin-bottom: 20px;
                        }}
                        .email-attachments {{
                            margin-top: 20px;
                        }}
                    </style>
                </head>
                <body>
                    <div class="email-header">
                        <p><b>Subject:</b> {email_data['Subject']}</p>
                        <p><b>From:</b> {email_data['From']}</p>
                        <p><b>To:</b> {email_data['To']}</p>
                        <p><b>Date:</b> {email_data['Date']}</p>
                    </div>
                    <div class="email-body">
                        {email_data['Body']['html_body']}
                    </div>
                    <div class="email-attachments">
                        <b>Attachments:</b>
                        <ul>
                            {''.join([f'<li>{name}</li>' for name in email_data['Body']['attachment_names']])}
                        </ul>
                    </div>
                </body>
                </html>
            """
