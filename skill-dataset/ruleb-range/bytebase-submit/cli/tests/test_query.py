import csv
import io
import json
import unittest
from unittest.mock import Mock, patch

import requests

from api_client import AuthExpiredError, BytebaseAPIClient
from query import (decode_value, normalize_results, parse_sheet_url,
                   render_results, resolve_database, select_data_source)


BASE = "https://bytebase.example"
DATABASE = "instances/csp/databases/pgdb_csp"


def response(data):
    result = Mock()
    result.json.return_value = data
    return result


class QueryTests(unittest.TestCase):
    def test_project_listing_sets_page_size_and_follows_pages(self):
        client = BytebaseAPIClient(BASE, {})
        with patch.object(client, "_request") as request:
            request.side_effect = [response({"projects": [{"name": "projects/a"}], "nextPageToken": "next"}),
                                   response({"projects": [{"name": "projects/b"}]})]
            self.assertEqual(client.list_projects(), [{"name": "projects/a"}, {"name": "projects/b"}])
            first, second = request.call_args_list
            self.assertEqual(first.kwargs["json"], {"pageSize": 1000, "pageToken": ""})
            self.assertEqual(second.kwargs["json"]["pageToken"], "next")

    def test_sheet_url_and_wrong_origin(self):
        self.assertEqual(parse_sheet_url(BASE + "/sql-editor/projects/sqpf/sheets/8664", BASE), ("sqpf", "8664"))
        for url in ["https://other.example/sql-editor/projects/sqpf/sheets/8664",
                    BASE + "/sql-editor/projects/sqpf/sheets/not-a-number"]:
            with self.assertRaises(ValueError):
                parse_sheet_url(url, BASE)

    @patch("api_client.requests.request")
    def test_query_request_uses_database_query_endpoint(self, request):
        request.return_value = response({"results": []})
        request.return_value.status_code = 200
        request.return_value.ok = True
        client = BytebaseAPIClient(BASE, {"access_token": "test"})
        client.query(DATABASE, "SELECT 1", "source", limit=5, schema="public", timeout=8)
        args, kwargs = request.call_args
        self.assertEqual(args, ("POST", BASE + "/v1/" + DATABASE + ":query"))
        self.assertEqual(kwargs["json"], {"name": DATABASE, "statement": "SELECT 1",
                                         "limit": 5, "dataSourceId": "source", "schema": "public"})
        self.assertEqual(kwargs["timeout"], 8)

    @patch("api_client.requests.request")
    def test_auth_and_permission_errors_do_not_retry(self, request):
        client = BytebaseAPIClient(BASE, {})
        for status, error_type in [(401, AuthExpiredError), (403, requests.HTTPError)]:
            result = Mock(status_code=status, ok=False, text="denied")
            result.raise_for_status.side_effect = requests.HTTPError("denied")
            request.return_value = result
            with self.assertRaises(error_type):
                client.query(DATABASE, "SELECT 1", "source")
        self.assertEqual(request.call_count, 2)

    def test_invalid_parameters_never_send_query(self):
        client = BytebaseAPIClient(BASE, {})
        with patch.object(client, "_request") as request:
            for database, sql, source, limit in [("pgdb_csp", "SELECT 1", "s", 1),
                                                 (DATABASE, " ", "s", 1),
                                                 (DATABASE, "SELECT 1", "s", 0),
                                                 (DATABASE, "SELECT 1", "", 1)]:
                with self.assertRaises(ValueError):
                    client.query(database, sql, source, limit=limit)
            request.assert_not_called()

    def test_database_lookup_checks_all_pages(self):
        client = Mock()
        target = {"name": DATABASE, "project": "projects/sqpf"}
        client._request.side_effect = [response({"databases": [], "nextPageToken": "next"}),
                                       response({"databases": [target]})]
        self.assertEqual(resolve_database(client, "pgdb_csp", "sqpf"), target)
        self.assertEqual(client._request.call_args.kwargs["params"]["pageToken"], "next")

    def test_ambiguous_database_is_rejected(self):
        client = Mock()
        client._request.return_value = response({"databases": [
            {"name": DATABASE}, {"name": "instances/other/databases/pgdb_csp"}]})
        with self.assertRaisesRegex(ValueError, "同名数据库"):
            resolve_database(client, "pgdb_csp", "sqpf")

    def test_data_source_selection(self):
        client = Mock()
        database = {"name": DATABASE, "instanceResource": {"dataSources": [
            {"id": "admin", "type": "ADMIN"}, {"id": "ro", "type": "READ_ONLY"}]}}
        self.assertEqual(select_data_source(client, database), "ro")
        self.assertEqual(select_data_source(client, database, "admin"), "admin")
        with self.assertRaises(ValueError):
            select_data_source(client, database, "unknown")
        client._request.assert_not_called()

    def test_result_values_preserve_types_and_precision(self):
        values = [{"nullValue": "NULL_VALUE"}, {"boolValue": False},
                  {"int64Value": "9223372036854775807"}, {"uint64Value": "18446744073709551615"},
                  {"doubleValue": 0.0}, {"stringValue": ""}, {"bytesValue": "AAE="},
                  {"valueValue": {"a": [1, None]}}, {"timestampTzValue": {"googleTimestamp": "2026-11-13T00:00:00Z", "zone": "Asia/Shanghai"}}]
        decoded = [decode_value(v) for v in values]
        self.assertEqual(decoded[:7], [None, False, 9223372036854775807, 18446744073709551615, 0.0, "", "AAE="])
        self.assertEqual(decoded[-1]["zone"], "Asia/Shanghai")

    def test_http_success_with_sql_failure_is_rejected(self):
        for result in [{"error": "permission denied"}, {"permissionDenied": {}},
                       {"syntaxError": {}}, {"postgresError": {"message": "bad SQL"}}]:
            with self.assertRaises(RuntimeError):
                normalize_results({"results": [result]})
        with self.assertRaises(RuntimeError):
            normalize_results({"results": []})

    def test_duplicate_columns_and_masking_metadata_preserved(self):
        result = normalize_results({"results": [{"columnNames": ["id", "id"],
            "masked": [{}, {"algorithm": "MASK"}],
            "rows": [{"values": [{"int64Value": "1"}, {"stringValue": "***"}]}]}]})
        data = json.loads(render_results(result, "json"))
        self.assertEqual(data["results"][0]["rows"], [[1, "***"]])
        self.assertEqual(data["results"][0]["columnNames"], ["id", "id"])
        self.assertEqual(data["results"][0]["masked"][1]["algorithm"], "MASK")

    def test_csv_quotes_multiline_values_and_rejects_multiple_results(self):
        results = [{"columnNames": ["value", "other"], "rows": [["a,b\nsecond", None]]}]
        rows = list(csv.reader(io.StringIO(render_results(results, "csv"))))
        self.assertEqual(rows, [["value", "other"], ["a,b\nsecond", ""]])
        with self.assertRaises(ValueError):
            render_results(results * 2, "csv")


if __name__ == "__main__":
    unittest.main()
