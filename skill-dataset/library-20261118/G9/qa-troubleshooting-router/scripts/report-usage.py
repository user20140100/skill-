#!/usr/bin/env python3
"""Best-effort usage telemetry. Never print credentials, responses, or errors."""

import json
import os
import time
import urllib.request


ENDPOINT = "https://ai-trouble-shot.test.seewo.com/api/skill-usage"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Do not forward the bearer credential to another URL.
        return None


def report_usage():
    token = os.environ.get("AI_TROUBLE_SHOT_MCP_TOKEN", "")
    if not token.strip() or "\r" in token or "\n" in token:
        return
    payload = json.dumps({"usedAt": time.time_ns() // 1_000_000}).encode("utf-8")
    request = urllib.request.Request(
        ENDPOINT,
        data=payload,
        headers={"Authorization": "Bearer " + token.strip(), "Content-Type": "application/json"},
        method="POST",
    )
    opener = urllib.request.build_opener(NoRedirect())
    with opener.open(request, timeout=3):
        pass


def main():
    try:
        report_usage()
    except Exception:
        pass


if __name__ == "__main__":
    main()
