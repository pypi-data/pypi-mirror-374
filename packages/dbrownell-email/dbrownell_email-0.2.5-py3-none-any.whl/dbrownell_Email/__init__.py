# noqa: D104
from importlib.metadata import version

from .SmtpMailer import SmtpMailer

__all__ = [
    "SmtpMailer",
]

__version__ = version("dbrownell_Email")
