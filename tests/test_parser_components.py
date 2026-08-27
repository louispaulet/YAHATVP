"""Direct unit tests for parser dispatch, CSV validation, and XML navigation."""

import csv
from pathlib import Path

import pytest
from lxml import etree

from hatvp.config import load_pipeline_config
from hatvp.models import ParseContext
from hatvp.parser import is_allowed_top_level
from hatvp.parser.csv import (
    csv_config,
    csv_delimiter,
    csv_has_header,
    csv_row_count,
    parse_csv,
    validate_identity_columns,
)
from hatvp.parser.declaration_support import child_values, local_name
from hatvp.parser.dispatch import (
    COMPONENT_TABLES,
    append_rows,
    component_table_names,
    output_table_count,
)
from hatvp.parser.mandates import mandate_rows
from hatvp.xml_support import children, item_groups, normalized_child_text
from tests.parser_support import FIXTURES


def test_csv_component_reports_config_and_fixture_shape() -> None:
    delimiter, identities = csv_config()
    path = FIXTURES / "liste.csv"

    assert delimiter == csv_delimiter() == ";"
    assert "id_origine" in identities
    assert csv_has_header(path)
    assert csv_row_count(path) == 2


def test_csv_identity_validation_rejects_unrelated_headers() -> None:
    with pytest.raises(ValueError, match="identity columns"):
        validate_identity_columns(["other"], ("identifiant",))


def test_dispatch_helpers_keep_the_normalized_table_contract() -> None:
    tables = {name: [] for name in COMPONENT_TABLES}
    append_rows(tables, "people", [{"declaration_uuid": "fixture"}])

    assert component_table_names() == COMPONENT_TABLES
    assert output_table_count(tables) == len(COMPONENT_TABLES)
    assert tables["people"][0]["declaration_uuid"] == "fixture"


def test_xml_navigation_is_namespace_safe_and_grouped() -> None:
    root = etree.fromstring(
        b"<root xmlns='urn:test'><items><items><name>A</name></items></items></root>"
    )
    item = children(children(root, "items")[0], "items")[0]

    assert local_name(root.tag) == "root"
    assert normalized_child_text(item, "name") == "A"
    assert child_values(item)["name"] == "A"
    assert item_groups(root) == [item]
    assert is_allowed_top_level("declaration")


def test_namespaced_general_mandate_keeps_quality_only_rows() -> None:
    element = etree.fromstring(
        b'<declaration xmlns="urn:test"><uuid>fixture</uuid><general>'
        b"<qualiteMandat><typeMandat>local</typeMandat></qualiteMandat></general>"
        b"</declaration>"
    )

    rows = mandate_rows(element, ParseContext("2026-08-16"), load_pipeline_config().parser)
    assert rows[0]["mandate_type"] == "local"


def test_csv_fixture_can_be_read_with_the_configured_delimiter(tmp_path: Path) -> None:
    path = tmp_path / "listing.csv"
    path.write_text("identifiant;nom\nA;Dupont\n", encoding="utf-8")

    with path.open(newline="") as source:
        rows = list(csv.DictReader(source, delimiter=csv_delimiter()))

    assert rows == [{"identifiant": "A", "nom": "Dupont"}]


@pytest.mark.parametrize("primary_value", [" ", "Néant"])
def test_csv_identity_fallback(tmp_path: Path, primary_value: str) -> None:
    path = tmp_path / "listing.csv"
    path.write_text(
        f"id_origine;url_dossier\n{primary_value};https://example.test/declaration\n",
        encoding="utf-8",
    )

    rows = parse_csv(path, "2026-08-16")

    assert rows[0]["source_record_id"] == "https://example.test/declaration"
