"""Non-blocking, read-only checks of the official GitHub latest release."""
import json
import re
from urllib.parse import quote

from PySide6.QtCore import QObject, QTimer, QUrl, Signal
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

VERSION = "1.0.0"
RELEASES = "https://github.com/kennclark-yb/YOINK/releases"
LATEST_API = "https://api.github.com/repos/kennclark-yb/YOINK/releases/latest"


def version_key(value):
    """SemVer 2.0 precedence (optional Git tag v; build metadata ignored)."""
    match = re.fullmatch(
        r"v?(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
        r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
        r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?", value,
    )
    if not match:
        raise ValueError("Invalid semantic version")
    pre = match[4]
    identifiers = []
    for item in pre.split(".") if pre else []:
        if item.isdigit():
            if len(item) > 1 and item.startswith("0"):
                raise ValueError("Invalid numeric prerelease identifier")
            identifiers.append((0, int(item)))
        else:
            identifiers.append((1, item))
    return tuple(map(int, match.group(1, 2, 3))), pre is None, tuple(identifiers)


def newer_release(data):
    tag = data["tag_name"]
    newer = version_key(tag) > version_key(VERSION)
    if data.get("draft") or data.get("prerelease") or not newer:
        return None
    # Construct the destination ourselves; never trust a response-supplied URL.
    return tag, RELEASES + "/tag/" + quote(tag, safe="")


class UpdateChecker(QObject):
    completed = Signal(bool, object, bool)  # manual, release, failed

    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = QNetworkAccessManager(self)
        self.reply = None
        self.manual = False
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(10000)
        self.timer.timeout.connect(self.cancel_request)

    def check(self, manual=False):
        self.manual = self.manual or manual
        if self.reply is not None:
            return  # A manual request can adopt an in-flight startup check.
        request = QNetworkRequest(QUrl(LATEST_API))
        request.setRawHeader(b"Accept", b"application/vnd.github+json")
        request.setRawHeader(b"User-Agent", ("YOINK/" + VERSION).encode())
        request.setAttribute(QNetworkRequest.Attribute.RedirectPolicyAttribute,
                             QNetworkRequest.RedirectPolicy.ManualRedirectPolicy)
        self.reply = self.manager.get(request)
        self.reply.finished.connect(self._finished)
        self.timer.start()

    def cancel_request(self):
        if self.reply is not None:
            self.reply.abort()

    def _finished(self):
        self.timer.stop()
        reply, self.reply = self.reply, None
        manual, self.manual = self.manual, False
        release, failed = None, False
        try:
            if (reply.error() != QNetworkReply.NetworkError.NoError
                    or reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute) != 200):
                raise ValueError("Release check unavailable")
            release = newer_release(json.loads(bytes(reply.readAll())))
        except (ValueError, KeyError, TypeError):
            failed = True
        finally:
            reply.deleteLater()
        self.completed.emit(manual, release, failed)
