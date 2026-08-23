"""Cloud execution and response dispatch for the dashboard bridge."""

import json
import os
from typing import Any

from aggregate_payloads import dashboard_payload, row_value
from analysis_payloads import age_analysis_payload, simple_analysis_payload
from bridge_runtime import (
    configured_bucket,
    configured_prefix,
    error_payload,
    response,
    runtime_setting,
    storage_client,
)
from health_payloads import health_payload
from highlight_payloads import highlights_payload
from query import build_query
from query_analysis import build_age_analysis_query, build_simple_analysis_query
from query_declaration import build_declaration_query
from query_health import build_health_query
from query_highlights import build_highlights_query
from query_search import build_search_query
from raw_xml import read_declaration_xml
from search_payloads import declaration_payload, search_payload


def client() -> Any:
    from google.cloud import bigquery

    return bigquery.Client(project=os.environ["BQ_PROJECT_ID"])


def query_rows(query: str, config: Any = None) -> list[Any]:
    options: dict[str, Any] = {"location": runtime_setting("BQ_LOCATION")}
    if config is not None:
        options["job_config"] = config
    return list(client().query(query, **options).result())


def raw_declaration_xml(
    snapshot_date: str, declaration_uuid: str, source_object: str | None = None
) -> str:
    return read_declaration_xml(
        storage_client,
        configured_bucket(),
        configured_prefix(),
        snapshot_date,
        declaration_uuid,
        source_object,
    )


def run_dashboard(view: str = "overview") -> tuple[str, int, dict[str, str]]:
    try:
        query = build_query(os.environ["BQ_PROJECT_ID"], os.environ["BQ_DATASET"], view)
        rows = query_rows(query)
        if not rows or row_value(rows[0], "snapshot_date") is None:
            return response(error_payload("NO_DATA", "No dashboard snapshot is available"), 404)
        return response(dashboard_payload(rows[0], view), 200)
    except Exception:
        return response(error_payload("QUERY_FAILED", "Dashboard data is unavailable"), 502)


def run_simple_analysis() -> tuple[str, int, dict[str, str]]:
    """Return the latest DOB leaderboard and salary age-bin aggregates."""

    try:
        query = build_simple_analysis_query(os.environ["BQ_PROJECT_ID"], os.environ["BQ_DATASET"])
        rows = query_rows(query)
        if not rows or row_value(rows[0], "snapshot_date") is None:
            return response(error_payload("NO_DATA", "No dashboard snapshot is available"), 404)
        return response(simple_analysis_payload(rows[0]), 200)
    except Exception:
        return response(error_payload("QUERY_FAILED", "Age analysis is unavailable"), 502)


def run_highlights() -> tuple[str, int, dict[str, str]]:
    """Return source-linked records selected by fixed, explainable criteria."""

    try:
        query = build_highlights_query(os.environ["BQ_PROJECT_ID"], os.environ["BQ_DATASET"])
        rows = query_rows(query)
        if not rows or row_value(rows[0], "snapshot_date") is None:
            return response(error_payload("NO_DATA", "No dashboard snapshot is available"), 404)
        return response(highlights_payload(rows[0]), 200)
    except Exception:
        return response(error_payload("QUERY_FAILED", "Highlights are unavailable"), 502)


def run_health() -> tuple[str, int, dict[str, str]]:
    """Return current source, layer, quality, and anomaly health."""

    try:
        query = build_health_query(os.environ["BQ_PROJECT_ID"], os.environ["BQ_DATASET"])
        rows = query_rows(query)
        if not rows or row_value(rows[0], "snapshot_date") is None:
            return response(error_payload("NO_DATA", "No dashboard snapshot is available"), 404)
        snapshot = str(row_value(rows[0], "snapshot_date"))
        path = f"{configured_prefix()}/quality/snapshot_date={snapshot}/report.json"
        report = json.loads(
            storage_client().bucket(configured_bucket()).blob(path).download_as_bytes()
        )
        return response(health_payload(rows[0], report), 200)
    except Exception:
        return response(error_payload("QUERY_FAILED", "Pipeline health is unavailable"), 502)


def run_age_analysis(search_term: str) -> tuple[str, int, dict[str, str]]:
    """Return source-preserving annual analysis for one matched declarant."""

    try:
        from google.cloud import bigquery

        config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("search_term", "STRING", search_term)]
        )
        query = build_age_analysis_query(os.environ["BQ_PROJECT_ID"], os.environ["BQ_DATASET"])
        rows = query_rows(query, config)
        if not rows or row_value(rows[0], "snapshot_date") is None:
            return response(error_payload("NOT_FOUND", "Declarant not found"), 404)
        return response(age_analysis_payload(rows[0]), 200)
    except Exception:
        return response(error_payload("QUERY_FAILED", "Declarant analysis is unavailable"), 502)


def run_search(search_term: str) -> tuple[str, int, dict[str, str]]:
    try:
        from google.cloud import bigquery

        config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("search_term", "STRING", search_term)]
        )
        query = build_search_query(os.environ["BQ_PROJECT_ID"], os.environ["BQ_DATASET"])
        rows = query_rows(query, config)
        if not rows or row_value(rows[0], "snapshot_date") is None:
            return response(error_payload("NO_DATA", "No dashboard snapshot is available"), 404)
        return response(search_payload(rows[0]), 200)
    except Exception:
        return response(error_payload("QUERY_FAILED", "Declaration search is unavailable"), 502)


def run_declaration(declaration_uuid: str) -> tuple[str, int, dict[str, str]]:
    """Return one declaration's public metadata and source XML excerpt."""

    try:
        from google.cloud import bigquery

        config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("declaration_uuid", "STRING", declaration_uuid)
            ]
        )
        query = build_declaration_query(os.environ["BQ_PROJECT_ID"], os.environ["BQ_DATASET"])
        rows = query_rows(query, config)
        if not rows or row_value(rows[0], "snapshot_date") is None:
            return response(error_payload("NOT_FOUND", "Declaration not found"), 404)
        try:
            snapshot = str(row_value(rows[0], "snapshot_date"))
            raw_xml = raw_declaration_xml(
                snapshot, declaration_uuid, row_value(rows[0], "source_object")
            )
        except LookupError:
            return response(error_payload("NOT_FOUND", "Declaration XML not found"), 404)
        return response(declaration_payload(rows[0], raw_xml), 200)
    except Exception:
        return response(error_payload("RAW_XML_UNAVAILABLE", "Declaration XML is unavailable"), 502)
