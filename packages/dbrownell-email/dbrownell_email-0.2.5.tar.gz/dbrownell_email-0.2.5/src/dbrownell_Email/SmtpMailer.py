"""Contains the SmtpMailer object."""

import datetime
import json
import mimetypes
import os
import smtplib
import ssl
import textwrap

from dataclasses import dataclass, field
from email import encoders
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from collections.abc import Generator
from pathlib import Path

from dbrownell_Common.ContextlibEx import ExitStack


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class SmtpMailer:
    """Code that manages SMTP profiles and uses them to send messages."""

    # ----------------------------------------------------------------------
    # |  Public Types
    PROFILE_EXTENSION = ".SmtpMailer"

    # ----------------------------------------------------------------------
    # |  Public Data
    host: str
    username: str
    password: str
    from_name: str
    from_email: str

    ssl: bool = field(kw_only=True)

    port: int | None = field(default=None)

    # ----------------------------------------------------------------------
    # |  Public Methods
    def ToString(
        self,
        *,
        show_password: bool = False,
    ) -> str:
        """Return a string representation of the profile."""

        return textwrap.dedent(
            """\
            host        : {host}
            username    : {username}
            password    : {password}
            from_name   : {from_name}
            from_email  : {from_email}
            ssl         : {ssl}
            port        : {port}
            """,
        ).format(
            host=self.host,
            username=self.username,
            password=self.password if show_password else "****",
            from_name=self.from_name,
            from_email=self.from_email,
            ssl=self.ssl,
            port=self.port,
        )

    # ----------------------------------------------------------------------
    def Save(
        self,
        profile_name: str,
    ) -> None:
        """Save a profile."""

        content = json.dumps(self.__dict__).encode("utf-8")

        if os.name == "nt":
            import win32crypt  # noqa: PLC0415

            content = win32crypt.CryptProtectData(content, "", None, None, None, 0)

        with (Path("~").expanduser() / (profile_name + self.__class__.PROFILE_EXTENSION)).open("wb") as f:
            f.write(content)

    # ----------------------------------------------------------------------
    def SendMessage(
        self,
        recipients: list[str],
        subject: str,
        message: str,
        attachment_filenames: list[Path] | None = None,
        message_format: str = "plain",  # "html"
    ) -> None:
        """Send an email message using the current profile."""

        if self.ssl:
            port = self.port or 465
            smtp = smtplib.SMTP_SSL(self.host, port, context=ssl.create_default_context())
        else:
            port = self.port or 26
            smtp = smtplib.SMTP(self.host, port)

        smtp.connect(self.host, port)
        with ExitStack(smtp.close):
            if not self.ssl:
                smtp.starttls()

            smtp.login(self.username, self.password)

            from_addr = "{} <{}>".format(self.from_name, self.from_email)

            msg = MIMEMultipart() if attachment_filenames else MIMEMultipart("alternative")

            msg["Subject"] = subject
            msg["From"] = from_addr
            msg["To"] = ", ".join(recipients)

            msg.attach(MIMEText(message, message_format))

            for attachment_filename in attachment_filenames or []:
                ctype, encoding = mimetypes.guess_type(attachment_filename)

                if ctype is None or encoding is not None:
                    ctype = "application/octet-stream"

                maintype, subtype = ctype.split("/", 1)

                with attachment_filename.open("rb") as f:
                    content = f.read()

                if maintype == "text":
                    attachment = MIMEText(content.decode("utf-8"), _subtype=subtype)
                elif maintype == "image":
                    attachment = MIMEImage(content, _subtype=subtype)
                elif maintype == "audio":
                    attachment = MIMEAudio(content, _subtype=subtype)
                else:
                    attachment = MIMEBase(maintype, subtype)

                    attachment.set_payload(content)
                    encoders.encode_base64(attachment)

                attachment.add_header("Content-Disposition", "attachment", filename=attachment_filename.name)

                msg.attach(attachment)

            smtp.sendmail(from_addr, recipients, msg.as_string())

    # ----------------------------------------------------------------------
    def SendTestMessage(
        self,
        recipients: list[str],
        attachment_filenames: list[Path] | None = None,
    ) -> None:
        """Send a test message using the current profile."""

        self.SendMessage(
            recipients,
            f"SmtpMailer Verification ({datetime.datetime.now()})",  # noqa: DTZ005
            "This is a test message to ensure that the profile is working as expected.\n",
            attachment_filenames,
        )

    # ----------------------------------------------------------------------
    @classmethod
    def Load(
        cls,
        profile_name: str,
    ) -> "SmtpMailer":
        """Load a previously saved profile file."""

        data_filename = Path("~").expanduser() / (profile_name + cls.PROFILE_EXTENSION)

        if not data_filename.is_file():
            message = f"'{profile_name}' is not a recognized profile name."
            raise Exception(message)

        content = data_filename.read_bytes()

        if os.name == "nt":
            import win32crypt  # noqa: PLC0415

            content = win32crypt.CryptUnprotectData(content, None, None, None, 0)[1]

        return cls(**json.loads(content.decode("utf-8")))

    # ----------------------------------------------------------------------
    @classmethod
    def EnumProfiles(cls) -> Generator[str, None, None]:
        """Enumerate all saved profiles."""

        for item in Path("~").expanduser().iterdir():
            if item.suffix == cls.PROFILE_EXTENSION:
                yield item.stem
