import json
from types import SimpleNamespace

import main
import service

AUTH = {"Authorization": "Bearer secret"}


def request(path="/v1/dashboard/overview", method="GET", headers=None):
    return SimpleNamespace(path=path, method=method, headers=headers or {})


class Client:
    def __init__(self, rows):
        self.rows = rows
        self.queries = []
        self.location = None

    def query(self, query, location=None):
        self.queries.append(query)
        self.location = location
        return SimpleNamespace(result=lambda: self.rows)


def body(result):
    return json.loads(result[0])


def overview_row():
    tables = [
        {"table_name": "assets", "row_count": 4},
        {"table_name": "declarations", "row_count": 2},
        {"table_name": "incomes", "row_count": 3},
        {"table_name": "people", "row_count": 2},
    ]
    return {
        "snapshot_date": "2026-08-18",
        "generated_at": "2026-08-18T08:00:00+00:00",
        "tables_json": json.dumps(tables),
    }


def items_row():
    return {
        "snapshot_date": "2026-08-18",
        "generated_at": "2026-08-18T08:00:00+00:00",
        "items_json": json.dumps(
            [{"label": "mandate_remuneration", "row_count": 3, "total_value": 12}]
        ),
    }


def test_bridge_requires_bearer_token(monkeypatch):
    monkeypatch.setenv("BRIDGE_TOKEN", "secret")
    result = main.dashboard(request(headers={"Authorization": "Bearer wrong"}))
    assert result[1] == 401
    assert body(result)["error"]["code"] == "UNAUTHORIZED"


def test_bridge_returns_overview_slice(monkeypatch):
    client = Client([overview_row()])
    monkeypatch.setenv("BRIDGE_TOKEN", "secret")
    monkeypatch.setenv("BQ_PROJECT_ID", "project")
    monkeypatch.setenv("BQ_DATASET", "hatvp")
    monkeypatch.setenv("BQ_LOCATION", "europe-west1")
    monkeypatch.setattr(service, "client", lambda: client)

    result = main.dashboard(request(headers=AUTH))

    assert result[1] == 200
    assert body(result)["tables"] == {"declarations": 2, "people": 2, "incomes": 3, "assets": 4}
    assert "tables_json" in client.queries[0]
    assert client.location == "europe-west1"


def test_bridge_returns_breakdown_slice(monkeypatch):
    monkeypatch.setenv("BRIDGE_TOKEN", "secret")
    monkeypatch.setenv("BQ_PROJECT_ID", "project")
    monkeypatch.setenv("BQ_DATASET", "hatvp")
    monkeypatch.setattr(service, "client", lambda: Client([items_row()]))

    result = main.dashboard(request(path="/v1/dashboard/income", headers=AUTH))

    assert result[1] == 200
    assert body(result)["items"][0]["totalValue"] == 12.0


def test_bridge_reports_empty_result_without_leaking_query_details(monkeypatch):
    monkeypatch.setenv("BRIDGE_TOKEN", "secret")
    monkeypatch.setenv("BQ_PROJECT_ID", "project")
    monkeypatch.setenv("BQ_DATASET", "hatvp")
    monkeypatch.setattr(service, "client", lambda: Client([]))

    result = main.dashboard(request(headers=AUTH))

    assert result[1] == 404
    assert body(result)["error"]["code"] == "NO_DATA"
