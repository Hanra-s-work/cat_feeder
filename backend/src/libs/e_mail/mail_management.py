""" 
# +==== BEGIN AsperBackend =================+
# LOGO: 
# ..........####...####..........
# ......###.....#.#########......
# ....##........#.###########....
# ...#..........#.############...
# ...#..........#.#####.######...
# ..#.....##....#.###..#...####..
# .#.....#.##...#.##..##########.
# #.....##########....##...######
# #.....#...##..#.##..####.######
# .#...##....##.#.##..###..#####.
# ..#.##......#.#.####...######..
# ..#...........#.#############..
# ..#...........#.#############..
# ...##.........#.############...
# ......#.......#.#########......
# .......#......#.########.......
# .........#####...#####.........
# /STOP
# PROJECT: AsperBackend
# FILE: mail_management.py
# CREATION DATE: 11-10-2025
# LAST Modified: 3:43:51 25-11-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: The file in charge of managing the emissions of e-mails.
# // AR
# +==== END AsperBackend =================+
"""


import ssl
import smtplib
from typing import List
from email import encoders
from email.message import EmailMessage
from email.utils import make_msgid
from email.mime.base import MIMEBase
from display_tty import Disp, initialise_logger
from . import mail_constants as CONST
from ..core import FinalClass


class MailManagement(metaclass=FinalClass):
    """_summary_
    """

    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, error: int = 84, success: int = 0, debug: bool = False) -> None:
        """_summary_
            The class in charge of allowing the user to send e-mails.

        Args:
            error (int, optional): _description_. Defaults to 84.
            success (int, optional): _description_. Defaults to 0.
            debug (bool, optional): _description_. Defaults to False.
        """
        # ------------------------ The logging function ------------------------
        self.disp.update_disp_debug(debug)
        self.disp.log_debug("Initialising...")
        # -------------------------- Inherited values --------------------------
        self.success = success
        self.error = error
        self.debug = debug

        # ------------------------- email related data -------------------------
        self.sender = CONST.SENDER_ADDRESS
        self.host = CONST.SENDER_HOST
        self.api_key = CONST.SENDER_KEY
        self.port = CONST.SENDER_PORT

        self.disp.log_debug("Initialised")

    def _send(self, em: EmailMessage) -> int:
        """
        Internal method to handle the actual sending of an email.

        Args:
            em (EmailMessage): The email message to be sent.

        Returns:
            int: The status of the email sending operation.
        """
        context = ssl.create_default_context()

        try:
            with smtplib.SMTP_SSL(self.host, self.port, context=context) as smtp:
                smtp.login(self.sender, self.api_key)
                smtp.send_message(em)
                self.disp.log_debug("Email sent successfully")
                return self.success
        except (smtplib.SMTPException, OSError, ssl.SSLError) as e:
            # SMTP/network/OS-level errors (authentication, connection, socket, SSL)
            self.disp.log_critical(f"An error occurred sending email: {e}")
            return self.error

    def send_email(self, receiver: str, subject: str, body: str, body_type: str = "html") -> int:
        """
        Sends a simple email to a single receiver.

        Args:
            receiver (str): The recipient's email address.
            subject (str): The subject of the email.
            body (str): The content of the email.
            body_type (str, optional): The MIME type of the email content ('html' or 'plain'). Defaults to 'html'.

        Returns:
            int: The status of the email sending operation.
        """
        em = EmailMessage()
        em['From'] = self.sender
        em['To'] = receiver
        em['Subject'] = subject

        if body_type.lower() == "html":
            em.add_alternative(body, subtype='html')
        else:
            em.set_content(body)

        return self._send(em)

    def send_email_with_attachment(self, receiver: str, subject: str, body: str, attachments: List[str], body_type: str = "html") -> int:
        """
        Sends an email with one or more attachments.

        Args:
            receiver (str): The recipient's email address.
            subject (str): The subject of the email.
            body (str): The content of the email.
            attachments (List[str]): List of file paths for attachments.
            body_type (str, optional): The MIME type of the email content ('html' or 'plain'). Defaults to 'html'.

        Returns:
            int: The status of the email sending operation.
        """
        em = EmailMessage()
        em['From'] = self.sender
        em['To'] = receiver
        em['Subject'] = subject

        if body_type == "html":
            em.add_alternative(body, subtype='html')
        else:
            em.set_content(body)

        for file in attachments:
            try:
                with open(file, 'rb') as f:
                    file_data = f.read()
                    file_name = file.split('/')[-1]

                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(file_data)
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename={file_name}'
                    )
                    em.add_attachment(
                        part.get_payload(decode=True),
                        maintype='application',
                        subtype='octet-stream',
                        filename=file_name
                    )

            except OSError as e:
                # File I/O errors: missing file, permission denied, etc.
                self.disp.log_critical(
                    f"Error reading attachment {file}: {e}",
                    "send_email_with_attachment"
                )
                return self.error

        return self._send(em)

    def send_email_to_multiple(self, receivers: List[str], subject: str, body: str, body_type: str = "html") -> int:
        """
        Sends an email to multiple recipients (To, Cc, or Bcc).

        Args:
            receivers (List[str]): A list of recipients' email addresses.
            subject (str): The subject of the email.
            body (str): The content of the email.
            body_type (str, optional): The MIME type of the email content ('html' or 'plain'). Defaults to 'html'.

        Returns:
            int: The status of the email sending operation.
        """
        em = EmailMessage()
        em['From'] = self.sender
        em['To'] = ', '.join(receivers)
        em['Subject'] = subject

        if body_type == "html":
            em.add_alternative(body, subtype='html')
        else:
            em.set_content(body)

        return self._send(em)

    def send_email_with_inline_image(self, receiver: str, subject: str, body: str, image_path: str, body_type: str = "html") -> int:
        """
        Sends an email with an inline image embedded in the body.

        Args:
            receiver (str): The recipient's email address.
            subject (str): The subject of the email.
            body (str): The content of the email, including a placeholder for the image.
            image_path (str): The path to the image to be embedded.
            body_type (str, optional): The MIME type of the email content ('html' or 'plain'). Defaults to 'html'.

        Returns:
            int: The status of the email sending operation.
        """
        em = EmailMessage()
        em['From'] = self.sender
        em['To'] = receiver
        em['Subject'] = subject

        if body_type == "html":
            em.add_alternative(body, subtype='html')
        else:
            em.set_content(body)

        try:
            with open(image_path, 'rb') as img:
                img_data = img.read()
                img_cid = make_msgid()[1:-1]
                em.add_related(
                    img_data,
                    maintype='image',
                    subtype='jpeg',
                    cid=img_cid
                )
                # Formatting the body may raise KeyError/ValueError if placeholders
                # don't match; opening the file may raise OSError.
                em.set_content(body.format(img_cid=img_cid))
        except (OSError, KeyError, ValueError) as e:
            self.disp.log_critical(
                f"Error embedding inline image: {e}",
                "send_email_with_inline_image"
            )
            return self.error

        return self._send(em)
