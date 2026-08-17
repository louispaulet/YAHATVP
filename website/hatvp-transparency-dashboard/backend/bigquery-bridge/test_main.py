import json

import main
import pytest
import service


class Request:
    def __init__(self, path="/v1/dashboard", method="GET", headers=None):
        self.path = path
        self.method = method
        self.headers = headers or {}


class Row(dict):
    pass


class Job:
    def __init__(self, rows):
        self.rows = rows

    def result(self):
        return self.rows


class Client:
    def __init__(self, rows):
        self.rows = rows
        self.location = None

    def query(self, query, location=None):
        self.location = location
        return Job(self.rows)


def body(result):
    return json.loads(result[0])


def aggregate_row():
    return Row(
        snapshot_date="2026-08-18",
        generated_at="2026-08-18T08:00:00+00:00",
        tables_json=json.dumps(
            [
                {"table_name": "assets", "row_count": 4},
                {"table_name": "declarations", "row_count": 2},
                {"table_name": "incomes", "row_count": 3},
                {"table_name": "people", "row_count": 2},
            ]
        ),
        income_json=json.dumps(
            [{"label": "mandate_remuneration", "row_count": 3, "total_value": 12}]
        ),
        assets_json=json.dumps([{"label": "bank_accounts", "row_count": 4, "total_value": 20}]),
        declaration_json=json.dumps([{"label": "mandat", "row_count": 2}]),
    )


def test_bridge_requires_bearer_token(monkeypatch):
    monkeypatch.setenv("BRIDGE_TOKEN", "secret")
    result = main.dashboard(Request(headers={"Authorization": "Bearer wrong"}))
    assert result[1] == 401
    assert body(result)["error"]["code"] == "UNAUTHORIZED"


def test_bridge_returns_aggregate_payload(monkeypatch):
    client = Client([aggregate_row()])
    monkeypatch.setenv("BRIDGE_TOKEN", "secret")
    monkeypatch.setenv("BQ_PROJECT_ID", "project")
    monkeypatch.setenv("BQ_DATASET", "hatvp")
    monkeypatch.setenv("BQ_LOCATION", "europe-west1")
    monkeypatch.setattr(service, "client", lambda: client)

    result = main.dashboard(Request(headers={"Authorization": "Bearer secret"}))

    assert result[1] == 200
    payload = body(result)
    assert payload["tables"] == {"declarations": 2, "people": 2, "incomes": 3, "assets": 4}
    assert payload["incomeByStream"][0]["totalValue"] == 12.0
    assert client.location == "europe-west1"


def test_bridge_reports_empty_result_without_leaking_query_details(monkeypatch):
    monkeypatch.setenv("BRIDGE_TOKEN", "secret")
    monkeypatch.setenv("BQ_PROJECT_ID", "project")
    monkeypatch.setenv("BQ_DATASET", "hatvp")
    monkeypatch.setattr(service, "client", lambda: Client([]))

    result = main.dashboard(Request(headers={"Authorization": "Bearer secret"}))

    assert result[1] == 404
    assert body(result)["error"]["code"] == "NO_DATA"


@pytest.mark.parametrize("path", ["/", "/v1/other"])
def test_bridge_rejects_unknown_paths(path):
    result = main.dashboard(Request(path=path))
    assert result[1] == 404
