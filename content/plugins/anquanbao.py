import re


__product__ = "Anquanbao Web Application Firewall (Anquanbao)"


def detect(content, **kwargs):
    headers = kwargs.get("headers", None)
    content = str(content)
    detection_scehmas = (re.compile(r"/aqb_cc/error/"), )
    if headers is not None:
        for detection in detection_scehmas:
            if detection.search(content) is not None:
                return True
        if re.compile(r"MISS").search(headers.get("X-Powered-By-Anquanbao", "")) is not None:
            return True