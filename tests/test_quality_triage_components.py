"""Direct tests for triage fingerprint, matching, summary, and CLI helpers."""

from pathlib import Path

from lxml import etree

from hatvp.quality_triage import artifact_store, triage_output_paths, triage_snapshot_path
from hatvp.storage import LocalArtifactStore
from hatvp.triage_evidence_helpers import (
    asset_key,
    asset_rows,
    assets_match,
    name_rows,
    normal_name,
    same_asset_values,
)
from hatvp.triage_fingerprints import occurrence_hashes, xml_digest
from hatvp.triage_summary import duplicate_groups, summary_counts


def test_triage_matching_helpers_use_identity_and_source_positions() -> None:
    raw = {
        "declaration_uuid": "a",
        "source_section": "immeubleDto",
        "source_item_index": 0,
        "prenom": " Alice ",
        "nom": "Dupont",
        "raw_value": "10",
        "normalized_value": 10.0,
        "asset_name": "House",
    }
    source = [dict(raw)]
    persisted = [dict(raw)]

    assert normal_name(" Alice  Dupont ") == "alice dupont"
    assert name_rows([{"prenom": "Alice", "nom": "Dupont"}], raw)
    assert asset_key(raw) == ("a", "immeubleDto", 0)
    assert asset_rows(source, "a", raw) == source
    assert same_asset_values(source[0], raw)
    assert assets_match(source, persisted, raw)


def test_summary_helpers_classify_duplicate_content() -> None:
    fingerprints = {
        "a": [
            {"canonical_xml_sha256": "1", "semantic_xml_sha256": "same", "date_depot_raw": "x"},
            {"canonical_xml_sha256": "2", "semantic_xml_sha256": "same", "date_depot_raw": "x"},
        ]
    }
    records = [{"quality_reason": "negative", "disposition": "source_valid_flag"}]

    assert duplicate_groups(fingerprints)[0]["content_classification"] == "identical"
    assert summary_counts(records)["reason_counts"] == {"negative": 1}


def test_fingerprint_helpers_hash_canonical_xml() -> None:
    element = etree.fromstring(b"<declaration><uuid>a</uuid></declaration>")
    canonical, semantic, size = occurrence_hashes(element)

    assert canonical == xml_digest(etree.tostring(element, method="c14n", exclusive=True))
    assert semantic == canonical
    assert size > 0


def test_triage_output_and_store_helpers_are_local_fixture_safe(tmp_path: Path) -> None:
    directory = triage_snapshot_path(tmp_path, "2026-08-16")
    json_path, markdown_path = triage_output_paths(tmp_path, "2026-08-16")
    store = artifact_store(None, tmp_path, "hatvp")

    assert isinstance(store, LocalArtifactStore)
    assert directory.name == "snapshot_date=2026-08-16"
    assert json_path.name == "review.json"
    assert markdown_path.name == "review.md"
