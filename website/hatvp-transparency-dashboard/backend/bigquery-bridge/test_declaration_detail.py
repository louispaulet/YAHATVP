"""Fixture tests for extracting and serving one source XML declaration."""

import json
from pathlib import Path
from types import SimpleNamespace

import main
import service

ROOT = Path(__file__).resolve().parents[4]
FIXTURE = ROOT / "tests" / "fixtures" / "declarations.xml"
AUTH = {"Authorization": "Bearer secret"}


def request(path: str) -> SimpleNamespace:
    return SimpleNamespace(path=path, method="GET", headers=AUTH, args={})


class Client:
    def __init__(self, rows):
        self.rows = rows

    def query(self, _query, location=None, job_config=None):
        return SimpleNamespace(result=lambda: self.rows)


class Storage:
    def __init__(self):
        self.names = []

    def bucket(self, _name):
        return self

    def blob(self, name):
        self.names.append(name)
        return self

    def download_to_filename(self, target):
        Path(target).write_bytes(FIXTURE.read_bytes())


def row(identifier: str = "fixture-uuid-1"):
    return {
        "snapshot_date": "2026-08-18",
        "generated_at": "2026-08-18T08:00:00+00:00",
        "result_json": json.dumps({"declaration_uuid": identifier, "nom": "DUPONT"}),
        "source_object": "raw/source=wayback_hf/snapshot_date=2026-08-18/declarations.xml",
    }


def body(result):
    return json.loads(result[0])


def configure(monkeypatch, client):
    monkeypatch.setenv("BRIDGE_TOKEN", "secret")
    monkeypatch.setenv("BQ_PROJECT_ID", "project")
    monkeypatch.setenv("BQ_DATASET", "hatvp")
    monkeypatch.setenv("HATVP_BUCKET", "bucket")
    monkeypatch.setattr(service, "client", lambda: client)
    storage = Storage()
    monkeypatch.setattr(service, "storage_client", lambda: storage)
    return storage


def test_detail_route_returns_only_the_matching_source_node(monkeypatch):
    storage = configure(monkeypatch, Client([row()]))

    result = main.dashboard(request("/v1/dashboard/declarations/fixture-uuid-1"))

    assert result[1] == 200
    payload = body(result)
    assert payload["declaration"]["declarationUuid"] == "fixture-uuid-1"
    assert "<uuid>fixture-uuid-1</uuid>" in payload["rawXml"]
    assert "<uuid>fixture-uuid-2</uuid>" not in payload["rawXml"]
    assert storage.names == [
        "hatvp/raw/source=wayback_hf/snapshot_date=2026-08-18/declarations.xml"
    ]


def test_detail_route_returns_not_found_for_unknown_uuid(monkeypatch):
    configure(monkeypatch, Client([]))

    result = main.dashboard(request("/v1/dashboard/declarations/missing"))

    assert result[1] == 404
    assert body(result)["error"]["code"] == "NOT_FOUND"


def test_detail_route_rejects_nested_identifiers(monkeypatch):
    configure(monkeypatch, Client([]))

    result = main.dashboard(request("/v1/dashboard/declarations/a/b"))

    assert result[1] == 400
    assert body(result)["error"]["code"] == "INVALID_QUERY"
