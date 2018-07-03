import re

from lib.settings import HTTP_HEADER


__product__ = "EdgeCast WAF (Verizon)"


def detect(content, **kwargs):
    headers = kwargs.get("headers", None)
    detection_schema = (
        re.compile(r"\AECDF", re.I),
    )
    for detection in detection_schema:
        if detection.search(headers.get(HTTP_HEADER.SERVER, "")) is not None:
            return True
