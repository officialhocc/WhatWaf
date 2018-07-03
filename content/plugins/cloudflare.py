import re

from lib.settings import HTTP_HEADER


__product__ = "CloudFlare Web Application Firewall (CloudFlare)"


def detect(content, **kwargs):
    headers = kwargs.get("headers", None)
    content = str(content)
    detection_schemas = (
        re.compile(r"CloudFlare Ray ID:|var CloudFlare=", re.I),
        re.compile(r"cloudflare-nginx", re.I),
        re.compile(r"\A__cfduid=", re.I),
        re.compile(r"CF_RAY", re.I),
        re.compile(r"<.+>attention.required\S.\S.cloudflare<.+.>", re.I)
    )
    for detection in detection_schemas:
        if detection.search(content) is not None:
            return True
        if detection.search(headers.get(HTTP_HEADER.SERVER, "")) is not None:
            return True
        if detection.search(headers.get(HTTP_HEADER.COOKIE, "")) is not None:
            return True
        if detection.search(str(headers)) is not None:
            return True
