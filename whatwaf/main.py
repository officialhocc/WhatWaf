import sys
import shlex
import time
import subprocess

from lib.cmd import WhatWafParser
from content import (
    detection_main,
    encode
)
from lib.settings import (
    configure_request_headers,
    auto_assign,
    WAF_REQUEST_DETECTION_PAYLOADS,
    BANNER,
)
from lib.formatter import (
    error,
    info,
    fatal,
    success
)


def main():
    opt = WhatWafParser().cmd_parser()

    if not len(sys.argv) > 1:
        error("you failed to provide an option, redirecting to help menu")
        time.sleep(2)
        cmd = "python whatwaf.py --help"
        subprocess.call(shlex.split(cmd))
        exit(0)

    if opt.encodePayload:
        spacer = "-" * 30
        payload, load_path = opt.encodePayload
        info("encoding '{}' using '{}'".format(payload, load_path))
        try:
            encoded = encode(payload, load_path)
            success("encoded successfully:")
            print(
                "{}\n{}\n{}".format(
                    spacer, encoded, spacer
                )
            )
        except (AttributeError, ImportError):
            fatal("invalid load path given, check the load path and try again")
        exit(0)

    if opt.encodePayloadList:
        spacer = "-" * 30
        try:
            file_path, load_path = opt.encodePayloadList
            info("encoding payloads from given file '{}' using given tamper '{}'".format(
                file_path, load_path
            ))
            with open(file_path) as payloads:
                encoded = [encode(p.strip(), load_path) for p in payloads.readlines()]
                if opt.saveEncodedPayloads is not None:
                    with open(opt.saveEncodedPayloads, "a+") as save:
                        for item in encoded:
                            save.write(item + "\n")
                    success("saved encoded payloads to file '{}' successfully".format(opt.saveEncodedPayloads))
                else:
                    success("payloads encoded successfully:")
                    print(spacer)
                    for i, item in enumerate(encoded, start=1):
                        print(
                            "#{} {}".format(i, item)
                        )
                    print(spacer)
        except IOError:
            fatal("provided file '{}' appears to not exist, check the path and try again".format(file_path))
        except (AttributeError, ImportError):
            fatal("invalid load path given, check the load path and try again")
        exit(0)

    if opt.updateWhatWaf:
        info("update in progress")
        cmd = shlex.split("git pull origin master")
        subprocess.call(cmd)
        exit(0)

    if not opt.hideBanner:
        print(BANNER)

    proxy, agent = configure_request_headers(
        random_agent=opt.useRandomAgent, agent=opt.usePersonalAgent,
        proxy=opt.runBehindProxy, tor=opt.runBehindTor
    )

    if opt.providedPayloads is not None:
        payload_list = [p.strip() if p[0] == " " else p for p in str(opt.providedPayloads).split(",")]
        info("using provided payloads")
    elif opt.payloadList is not None:
        payload_list = [p.strip("\n") for p in open(opt.payloadList).readlines()]
        info("using provided payload file '{}'".format(opt.payloadList))
    else:
        payload_list = WAF_REQUEST_DETECTION_PAYLOADS
        info("using default payloads")

    try:
        if opt.runSingleWebsite:
            url_to_use = auto_assign(opt.runSingleWebsite, ssl=opt.forceSSL)
            info("running single web application '{}'".format(url_to_use))
            detection_main(
                url_to_use, payload_list, agent=agent, proxy=proxy,
                verbose=opt.runInVerbose
            )

        elif opt.runMultipleWebsites:
            info("reading from '{}'".format(opt.runMultipleWebsites))
            with open(opt.runMultipleWebsites) as urls:
                for i, url in enumerate(urls, start=1):
                    url = auto_assign(url, ssl=opt.forceSSL)
                    info("currently running on site #{} ('{}')".format(i, url))
                    detection_main(
                        url, payload_list, agent=agent, proxy=proxy,
                        verbose=opt.runInVerbose
                    )
                    print("\n\b")
                    time.sleep(0.5)
    except KeyboardInterrupt:
        fatal("user aborted scanning")
