#!/usr/bin/env python3
"""Read-only Wise evidence client, personal initial version."""
import argparse
import json
import sys
import subprocess
from uuid import UUID

BASE = "https://wise.cvte.com/api/v1"
KB = "88babf83-5082-4104-af51-cb40c48d95ab"
API_KEY = "sk-uYji_Dnx0yFY1eFpcE59SUVHOrNPejF9QU9LABM7oinWF2fb"


def request(path, body=None, method="GET"):
    # curl uses the host's trusted certificates; credentials travel over stdin.
    config = 'header = "X-API-Key: ' + API_KEY + '"\n'
    if body is not None:
        config += 'data = ' + json.dumps(json.dumps(body, ensure_ascii=False), ensure_ascii=False) + '\n'
    try:
        process = subprocess.run([
            "curl", "--disable", "--silent", "--show-error", "--max-time", "45",
            "--max-filesize", "8388608", "--request", method,
            "--header", "Content-Type: application/json", "--config", "-",
            "--write-out", "\n%{http_code}", BASE + path,
        ], input=config, capture_output=True, text=True, timeout=50, check=False)
        if process.returncode:
            raise ValueError("Wise transport failed: " + process.stderr[:800])
        raw, status = process.stdout.rsplit("\n", 1)
        if not 200 <= int(status) < 300:
            raise ValueError("Wise HTTP " + status + ": " + raw[:800])
        result = json.loads(raw)
        if not isinstance(result, dict):
            raise ValueError("Wise returned an unexpected response shape")
        if result.get("success") is False or result.get("ok") is False:
            raise ValueError("Wise application error: " + json.dumps(result, ensure_ascii=False)[:800])
        return result
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError("Wise connection failed: " + str(exc)) from None


def uuid(value):
    return str(UUID(value))


def document(identifier):
    doc = request("/knowledge/" + uuid(identifier))["data"]
    if doc.get("knowledge_base_id") != KB:
        raise ValueError("Document does not belong to the configured Mofang knowledge base")
    meta = doc.get("metadata") or {}
    return {"knowledge_id": doc["id"], "title": doc.get("title"),
            "source_url": doc.get("source"), "source_path": meta.get("source_path"),
            "source_updated_at": meta.get("source_updated_at"),
            "wise_url": "https://wise.cvte.com/knowledge/" + doc["id"] + "/info"}


def invoke(name, arguments):
    result = request("/agent-tools/" + name + "/invoke", {"arguments": arguments}, "POST")
    payload = result.get("result")
    if not isinstance(payload, dict) or payload.get("success") is False:
        raise ValueError("Wise tool failed: " + json.dumps(result, ensure_ascii=False)[:800])
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    search = sub.add_parser("search")
    search.add_argument("query")
    search.add_argument("--top", type=int, choices=range(1, 21), default=5)
    search.add_argument("--threshold", type=float)
    doc = sub.add_parser("document")
    doc.add_argument("id", type=uuid)
    chunks = sub.add_parser("chunks")
    chunks.add_argument("id", type=uuid)
    chunks.add_argument("--offset", type=int, default=0)
    chunks.add_argument("--limit", type=int, choices=range(1, 11), default=5)
    read = sub.add_parser("read", help="Use chunk IDs returned by this knowledge base's search")
    read.add_argument("ids", nargs="+", type=uuid)
    expand = sub.add_parser("expand", help="Use a chunk ID returned by this knowledge base's search")
    expand.add_argument("id", type=uuid)
    expand.add_argument("--count", type=int, choices=range(1, 11), default=2)
    args = parser.parse_args()
    if args.command == "search":
        if not args.query.strip():
            parser.error("query must not be blank")
        body = {"query_text": args.query, "match_count": args.top}
        if args.threshold is not None:
            if not 0 <= args.threshold <= 1:
                parser.error("threshold must be between 0 and 1")
            body["vector_threshold"] = args.threshold
        result = request("/knowledge-bases/" + KB + "/hybrid-search", body)
        hits = result.get("data", [])
        if not isinstance(hits, list):
            raise ValueError("Unexpected search result; expected data array")
        sources = {}
        for hit in hits:
            kid = hit.get("knowledge_id")
            if kid and kid not in sources:
                try:
                    sources[kid] = document(kid)
                except ValueError as exc:
                    sources[kid] = {"source_error": str(exc)}
        return {"knowledge_base_id": KB, "query": args.query, "hits": hits, "documents": sources}
    if args.command == "document":
        return document(args.id)
    if args.command == "chunks":
        if args.offset < 0:
            parser.error("offset must be nonnegative")
        source = document(args.id)
        return {"document": source, "chunks": invoke("list_knowledge_chunks", {
            "knowledge_id": args.id, "offset": args.offset, "limit": args.limit})}
    if args.command == "read":
        if len(args.ids) > 20:
            parser.error("read accepts at most 20 chunk IDs")
        return invoke("read_chunks", {"chunk_ids": args.ids})
    return invoke("expand_context", {"chunk_id": args.id, "direction": "both", "count": args.count})


if __name__ == "__main__":
    try:
        print(json.dumps({"ok": True, "output": main()}, ensure_ascii=False, indent=2))
    except (ValueError, KeyError) as exc:
        print(json.dumps({"ok": False, "error": str(exc).replace(API_KEY, "[REDACTED]")}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
