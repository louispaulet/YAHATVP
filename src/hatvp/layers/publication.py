"""Cumulative declaration state and official publication lifecycle metadata."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import Any

from .silver_dedupe import detail_key

TABLES = ("declarations", "people", "incomes", "assets")
OFFICIAL_SOURCE = "hatvp_website"
VERSION_FIELDS = (
    "date_depot date_debut_mandat date_fin_mandat "
    "mandat_label declaration_modificative date_derniere_declaration_raw"
).split()


def publication_key(row: dict[str, Any]) -> str:
    """Identify one exact HATVP declaration version across exported snapshots."""

    uuid = str(row.get("declaration_uuid") or row.get("bronze_record_key") or "unknown")
    raw = row.get("raw_record_json")
    evidence = str(raw or tuple(row.get(field) for field in VERSION_FIELDS))
    digest = hashlib.sha256(evidence.encode()).hexdigest()
    return f"{uuid}:{digest}"


def publication_snapshot(
    tables: dict[str, list[dict[str, Any]]],
    history: dict[str, list[dict[str, Any]]],
    snapshot: str,
) -> dict[str, list[dict[str, Any]]]:
    """Build the full current corpus, marking versions absent from live XML."""

    rows = {name: [*history.get(name, []), *tables.get(name, [])] for name in TABLES}
    current = tables.get("declarations", [])
    official_current = [row for row in current if row.get("ingestion_source") == OFFICIAL_SOURCE]
    online = {publication_key(row) for row in official_current}
    fallback_time = _row_time({"snapshot_date": snapshot})
    observed = max((_row_time(row) for row in official_current), default=fallback_time)
    first: dict[str, datetime] = {}
    declarations = rows["declarations"]
    for row in declarations:
        if row.get("ingestion_source") == OFFICIAL_SOURCE:
            key, moment = publication_key(row), _row_time(row)
            first[key] = min(first.get(key, moment), moment)
    canonical: dict[tuple[str, str], dict[str, Any]] = {}
    for row in declarations:
        identity = (publication_key(row), str(row.get("ingestion_source") or "unknown"))
        if identity not in canonical or _rank(row) > _rank(canonical[identity]):
            canonical[identity] = row
    parent_state: dict[str, dict[str, Any]] = {}
    for (key, _), row in canonical.items():
        is_online = key in online
        parent_state[str(row.get("bronze_record_key") or "")] = {
            "publication_status": "online" if is_online else "unpublished",
            "first_online_at": first.get(key),
            "missing_from_latest_export_at": None if is_online else observed,
        }
    return {name: _rows_for_snapshot(name, rows[name], parent_state, snapshot) for name in TABLES}


def _rows_for_snapshot(name, rows, state, snapshot):
    latest = {}
    for row in rows:
        parent = str(row.get("bronze_record_key") or "")
        if parent not in state:
            continue
        identity = (parent, detail_key(row))
        candidate = {**row, **state[parent], "snapshot_date": snapshot}
        if (
            identity not in latest
            or ("metric_eligible" in row and "metric_eligible" not in latest[identity])
            or _rank(candidate) > _rank(latest[identity])
        ):
            latest[identity] = candidate
    return list(latest.values())


def _rank(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        int(row.get("ingestion_source") == OFFICIAL_SOURCE),
        _row_time(row),
        str(row.get("source_snapshot_date") or row.get("snapshot_date") or ""),
        str(row.get("bronze_record_key") or ""),
    )


def _row_time(row: dict[str, Any]) -> datetime:
    value = row.get("source_observed_at") or row.get("source_ingestion_snapshot_date")
    value = value or row.get("source_snapshot_date") or row.get("snapshot_date")
    try:
        text = str(value).replace("Z", "+00:00")
        result = value if isinstance(value, datetime) else datetime.fromisoformat(text)
    except ValueError:
        return datetime.min.replace(tzinfo=UTC)
    return result.astimezone(UTC) if result.tzinfo else result.replace(tzinfo=UTC)
