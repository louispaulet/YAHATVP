"""Fixture tests for declaration search and source XML detail routes."""

import json
from types import SimpleNamespace

import main
import service
from query_declaration import build_declaration_query
from query_search import build_search_query

AUTH = {"Authorization": "Bearer secret"}


def request(path: str, args: dict[str, str] | None = None) -> SimpleNamespace:
    return SimpleNamespace(path=path, method="GET", headers=AUTH, args=args or {})


class Client:
    def __init__(self, rows):
        self.rows = rows
        self.queries = []
        self.configs = []

    def query(self, query, location=None, job_config=None):
        self.queries.append(query)
        self.configs.append(job_config)
        return SimpleNamespace(result=lambda: self.rows)


def body(result):
    return json.loads(result[0])


def search_row():
    result = {"declaration_uuid": "fixture-uuid-1", "prenom": "Alice", "nom": "DUPONT"}
    return {
        "snapshot_date": "2026-08-18",
        "generated_at": "2026-08-18T08:00:00+00:00",
        "results_json": json.dumps([result]),
    }


def test_search_query_is_parameterized_and_public():
    query = build_search_query("project", "dataset")
    assert (
        "REGEXP_REPLACE(NORMALIZE_AND_CASEFOLD(@search_term, NFD), r'\\p{M}', '') AS term" in query
    )
    assert (
        "REGEXP_REPLACE(NORMALIZE_AND_CASEFOLD(COALESCE(p.nom, ''), NFD), r'\\p{M}', '')" in query
    )
    assert "p.nom" in query and "d.mandat_label" in query
    assert "i.income_stream" in query and "a.asset_name" in query
    assert "LIMIT 50" in query
    for field in ("email", "telephone", "adresse_", "date_naissance", "raw_record_json"):
        assert field not in query


def test_declaration_query_uses_uuid_parameter_without_private_fields():
    query = build_declaration_query("project", "dataset")
    assert "@declaration_uuid" in query
    assert "result_json" in query
    assert "p.nom" in query
    assert "email" not in query


def test_bridge_rejects_an_empty_search_term(monkeypatch):
    monkeypatch.setenv("BRIDGE_TOKEN", "secret")
    result = main.dashboard(request("/v1/dashboard/search"))
    assert result[1] == 400
    assert body(result)["error"]["code"] == "INVALID_QUERY"


def test_bridge_returns_search_result_and_uses_a_query_config(monkeypatch):
    client = Client([search_row()])
    monkeypatch.setenv("BRIDGE_TOKEN", "secret")
    monkeypatch.setenv("BQ_PROJECT_ID", "project")
    monkeypatch.setenv("BQ_DATASET", "hatvp")
    monkeypatch.setattr(service, "client", lambda: client)

    result = main.dashboard(request("/v1/dashboard/search", {"q": "Dupont"}))

    assert result[1] == 200
    assert body(result)["results"][0]["lastName"] == "DUPONT"
    assert client.configs[0] is not None
