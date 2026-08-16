from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from lxml import etree

from .normalize import normalize_text, parse_date, parse_french_number, raw_text

XML_ROOT_NAME = "declarations"
ALLOWED_TOP_LEVEL_CHILDREN = {"declaration", "declarations"}


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _child(element: etree._Element | None, name: str) -> etree._Element | None:
    if element is None:
        return None
    return next((child for child in element if _local_name(child.tag) == name), None)


def _children(element: etree._Element | None, name: str) -> list[etree._Element]:
    if element is None:
        return []
    return [child for child in element if _local_name(child.tag) == name]


def _raw_child_text(element: etree._Element | None, name: str) -> str | None:
    child = _child(element, name)
    return raw_text(child.text if child is not None else None)


def _normalized_child_text(element: etree._Element | None, name: str) -> str | None:
    child = _child(element, name)
    return normalize_text(child.text if child is not None else None)


def _item_groups(section: etree._Element | None) -> list[etree._Element]:
    container = _child(section, "items")
    if container is None:
        return []
    nested = _children(container, "items")
    return nested or [container]


def _flatten_leaf_values(element: etree._Element, prefix: str = "") -> dict[str, str | None]:
    children = list(element)
    if not children:
        return {prefix or _local_name(element.tag): raw_text(element.text)}
    result: dict[str, str | None] = {}
    for child in children:
        name = _local_name(child.tag)
        child_prefix = name if not prefix or name == "items" else f"{prefix}_{name}"
        result.update(_flatten_leaf_values(child, child_prefix))
    return result


def _first_value(values: dict[str, str | None], *names: str) -> str | None:
    for name in names:
        value = values.get(name)
        if value is not None:
            return value
    return None


def _first_key_containing(values: dict[str, str | None], *parts: str) -> str | None:
    for key, value in values.items():
        if value is not None and all(part.casefold() in key.casefold() for part in parts):
            return value
    return None


def _raw_record(values: dict[str, str | None]) -> str:
    return json.dumps(values, ensure_ascii=False, sort_keys=True)


def _date_fields(values: dict[str, str | None], field: str) -> tuple[str | None, str | None]:
    raw = values.get(field)
    return raw, parse_date(raw)


def _declaration_row(declaration: etree._Element, snapshot_date: str) -> dict[str, Any]:
    general = _child(declaration, "general")
    declaration_type = _child(general, "typeDeclaration")
    mandate = _child(general, "mandat")
    quality_mandate = _child(general, "qualiteMandat")
    organ = _child(general, "organe")

    date_depot_raw = _raw_child_text(declaration, "dateDepot")
    date_debut_raw = _raw_child_text(general, "dateDebutMandat")
    date_fin_raw = _raw_child_text(general, "dateFinMandat")
    return {
        "declaration_uuid": _normalized_child_text(declaration, "uuid"),
        "snapshot_date": snapshot_date,
        "source_file": "declarations.xml",
        "date_depot_raw": date_depot_raw,
        "date_depot": parse_date(date_depot_raw),
        "origine": _normalized_child_text(declaration, "origine"),
        "complete": _normalized_child_text(declaration, "complete"),
        "declaration_version": _normalized_child_text(declaration, "declarationVersion"),
        "declaration_type_id": _normalized_child_text(declaration_type, "id"),
        "declaration_type_label": _normalized_child_text(declaration_type, "label"),
        "mandat_label": _normalized_child_text(mandate, "label")
        or _normalized_child_text(general, "mandat"),
        "mandat_type": _normalized_child_text(quality_mandate, "typeMandat"),
        "mandat_category_code": _normalized_child_text(quality_mandate, "codCategorieMandat"),
        "mandat_category_label": _normalized_child_text(quality_mandate, "nomCategorieMandat"),
        "mandat_file_type": _normalized_child_text(quality_mandate, "codTypeMandatFichier"),
        "mandat_type_label": _normalized_child_text(quality_mandate, "labelTypeMandat"),
        "organ_code": _normalized_child_text(organ, "codeOrgane"),
        "organ_code_list": _normalized_child_text(organ, "codeListeOrgane"),
        "organ_label": _normalized_child_text(organ, "labelOrgane"),
        "organ_declaration_label": _normalized_child_text(organ, "labelDeclaration"),
        "organ_parent": _normalized_child_text(organ, "organeParent"),
        "quality_declarant": _normalized_child_text(general, "qualiteDeclarant"),
        "quality_declarant_pdf": _normalized_child_text(general, "qualiteDeclarantForPDF"),
        "date_debut_mandat_raw": date_debut_raw,
        "date_debut_mandat": parse_date(date_debut_raw),
        "date_fin_mandat_raw": date_fin_raw,
        "date_fin_mandat": parse_date(date_fin_raw),
        "date_derniere_declaration_raw": _raw_child_text(general, "dateDernDeclar"),
        "declaration_modificative": _normalized_child_text(general, "declarationModificative"),
    }


def _person_row(declaration: etree._Element, snapshot_date: str) -> dict[str, Any]:
    general = _child(declaration, "general")
    person = _child(general, "declarant")
    address = _child(person, "adresseDec")
    date_naissance_raw = _raw_child_text(person, "dateNaissance")
    return {
        "declaration_uuid": _normalized_child_text(declaration, "uuid"),
        "snapshot_date": snapshot_date,
        "source_file": "declarations.xml",
        "civilite": _normalized_child_text(person, "civilite"),
        "nom": _normalized_child_text(person, "nom"),
        "prenom": _normalized_child_text(person, "prenom"),
        "email": _normalized_child_text(person, "email"),
        "date_naissance_raw": date_naissance_raw,
        "date_naissance": parse_date(date_naissance_raw),
        "telephone_dec": _normalized_child_text(person, "telephoneDec"),
        "adresse_voie": _normalized_child_text(address, "voie"),
        "adresse_complement": _normalized_child_text(address, "complement"),
        "adresse_code_postal": _normalized_child_text(address, "codePostal"),
        "adresse_ville": _normalized_child_text(address, "ville"),
        "adresse_pays": _normalized_child_text(address, "pays"),
    }


def _mandate_rows(declaration: etree._Element, snapshot_date: str) -> list[dict[str, Any]]:
    declaration_uuid = _normalized_child_text(declaration, "uuid")
    general = _child(declaration, "general")
    mandate = _child(general, "mandat")
    quality_mandate = _child(general, "qualiteMandat")
    rows: list[dict[str, Any]] = []
    mandate_label = _normalized_child_text(mandate, "label") or _normalized_child_text(
        general, "mandat"
    )
    if general is not None and (mandate_label or quality_mandate is not None):
        date_debut_raw = _raw_child_text(general, "dateDebutMandat")
        date_fin_raw = _raw_child_text(general, "dateFinMandat")
        rows.append(
            {
                "declaration_uuid": declaration_uuid,
                "snapshot_date": snapshot_date,
                "source_section": "general",
                "description": mandate_label,
                "mandate_type": _normalized_child_text(quality_mandate, "typeMandat"),
                "commentaire": None,
                "employeur": None,
                "date_debut_raw": date_debut_raw,
                "date_debut": parse_date(date_debut_raw),
                "date_fin_raw": date_fin_raw,
                "date_fin": parse_date(date_fin_raw),
                "remuneration_raw": None,
                "remuneration_eur": None,
                "raw_record_json": None,
            }
        )

    section = _child(declaration, "mandatElectifDto")
    for index, item in enumerate(_item_groups(section)):
        values = _flatten_leaf_values(item)
        debut_raw, debut = _date_fields(values, "dateDebut")
        fin_raw, fin = _date_fields(values, "dateFin")
        remuneration_raw = _first_key_containing(values, "remuneration", "montant") or values.get(
            "remuneration"
        )
        rows.append(
            {
                "declaration_uuid": declaration_uuid,
                "snapshot_date": snapshot_date,
                "source_section": "mandatElectifDto",
                "source_item_index": index,
                "description": normalize_text(
                    _first_value(values, "descriptionMandat", "description", "label")
                ),
                "mandate_type": None,
                "commentaire": normalize_text(values.get("commentaire")),
                "employeur": normalize_text(values.get("employeur")),
                "date_debut_raw": debut_raw,
                "date_debut": debut,
                "date_fin_raw": fin_raw,
                "date_fin": fin,
                "remuneration_raw": remuneration_raw,
                "remuneration_eur": parse_french_number(remuneration_raw),
                "raw_record_json": _raw_record(values),
            }
        )
    return rows


def _activity_rows(declaration: etree._Element, snapshot_date: str) -> list[dict[str, Any]]:
    declaration_uuid = _normalized_child_text(declaration, "uuid")
    sections = (
        "activConsultantDto",
        "activProfCinqDerniereDto",
        "activProfConjointDto",
        "fonctionBenevoleDto",
        "activCollaborateursDto",
    )
    rows: list[dict[str, Any]] = []
    for section_name in sections:
        for index, item in enumerate(_item_groups(_child(declaration, section_name))):
            values = _flatten_leaf_values(item)
            debut_raw, debut = _date_fields(values, "dateDebut")
            fin_raw, fin = _date_fields(values, "dateFin")
            rows.append(
                {
                    "declaration_uuid": declaration_uuid,
                    "snapshot_date": snapshot_date,
                    "source_section": section_name,
                    "source_item_index": index,
                    "description": normalize_text(
                        _first_value(values, "description", "activite", "activiteProf", "label")
                    ),
                    "employeur": normalize_text(
                        _first_value(values, "employeur", "employeurConjoint", "nomEmployeur")
                    ),
                    "date_debut_raw": debut_raw,
                    "date_debut": debut,
                    "date_fin_raw": fin_raw,
                    "date_fin": fin,
                    "remuneration_raw": _first_key_containing(values, "remuneration", "montant"),
                    "raw_record_json": _raw_record(values),
                }
            )
    return rows


def _participation_rows(declaration: etree._Element, snapshot_date: str) -> list[dict[str, Any]]:
    declaration_uuid = _normalized_child_text(declaration, "uuid")
    rows: list[dict[str, Any]] = []
    for section_name in ("participationDirigeantDto", "participationFinanciereDto"):
        for index, item in enumerate(_item_groups(_child(declaration, section_name))):
            values = _flatten_leaf_values(item)
            valuation_raw = _first_value(values, "evaluation", "valeur", "valeurActuelle")
            rows.append(
                {
                    "declaration_uuid": declaration_uuid,
                    "snapshot_date": snapshot_date,
                    "source_section": section_name,
                    "source_item_index": index,
                    "company_name": normalize_text(
                        _first_value(values, "nomSociete", "denomination")
                    ),
                    "activity": normalize_text(values.get("activite")),
                    "commentaire": normalize_text(values.get("commentaire")),
                    "evaluation_raw": valuation_raw,
                    "evaluation_eur": parse_french_number(valuation_raw),
                    "capital_detenu_raw": values.get("capitalDetenu"),
                    "nombre_parts_raw": values.get("nombreParts"),
                    "remuneration_raw": values.get("remuneration"),
                    "raw_record_json": _raw_record(values),
                }
            )
    return rows


ASSET_SECTIONS = (
    "immeubleDto",
    "sciDto",
    "valeursNonEnBourseDto",
    "valeursEnBourseDto",
    "assuranceVieDto",
    "comptesBancaireDto",
    "bienDiverDto",
    "vehiculeDto",
    "fondDto",
    "autreBienDto",
    "bienEtrangerDto",
)


def _asset_rows(declaration: etree._Element, snapshot_date: str) -> list[dict[str, Any]]:
    declaration_uuid = _normalized_child_text(declaration, "uuid")
    rows: list[dict[str, Any]] = []
    value_names = (
        "valeur",
        "evaluation",
        "valeurActuelle",
        "valeurRachat",
        "valeurVenale",
        "prixAcquisition",
        "valeurAchat",
    )
    name_names = (
        "nature",
        "nomSociete",
        "denomination",
        "typeCompte",
        "marque",
        "souscripteur",
        "etablissement",
        "localisation",
        "description",
    )
    for section_name in ASSET_SECTIONS:
        for index, item in enumerate(_item_groups(_child(declaration, section_name))):
            values = _flatten_leaf_values(item)
            raw_value = _first_value(values, *value_names)
            rows.append(
                {
                    "declaration_uuid": declaration_uuid,
                    "snapshot_date": snapshot_date,
                    "source_section": section_name,
                    "source_item_index": index,
                    "asset_name": normalize_text(_first_value(values, *name_names)),
                    "raw_value": raw_value,
                    "normalized_value": parse_french_number(raw_value),
                    "quality_status": "OK",
                    "quality_reason": None,
                    "raw_record_json": _raw_record(values),
                }
            )
    return rows


def _liability_rows(declaration: etree._Element, snapshot_date: str) -> list[dict[str, Any]]:
    declaration_uuid = _normalized_child_text(declaration, "uuid")
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(_item_groups(_child(declaration, "passifDto"))):
        values = _flatten_leaf_values(item)
        raw_value = _first_value(values, "restantDu", "mensualite", "valeur", "montant")
        rows.append(
            {
                "declaration_uuid": declaration_uuid,
                "snapshot_date": snapshot_date,
                "source_section": "passifDto",
                "source_item_index": index,
                "description": normalize_text(
                    _first_value(values, "objetDette", "nature", "nomCreancier", "description")
                ),
                "raw_value": raw_value,
                "normalized_value": parse_french_number(raw_value),
                "raw_record_json": _raw_record(values),
            }
        )
    return rows


def _income_rows(declaration: etree._Element, snapshot_date: str) -> list[dict[str, Any]]:
    declaration_uuid = _normalized_child_text(declaration, "uuid")
    rows: list[dict[str, Any]] = []
    section = _child(declaration, "revenuMandatDto")
    for item_index, item in enumerate(_item_groups(section)):
        values = _flatten_leaf_values(item)
        year = normalize_text(values.get("annee"))
        category_nodes = [
            child for child in item if _local_name(child.tag).startswith("revenuMandatItem")
        ]
        for category_index, category in enumerate(category_nodes):
            category_values = _flatten_leaf_values(category)
            raw_value = category_values.get("revenuElu")
            spouse_raw = category_values.get("revenuConjoint")
            rows.append(
                {
                    "declaration_uuid": declaration_uuid,
                    "snapshot_date": snapshot_date,
                    "source_section": "revenuMandatDto",
                    "source_item_index": item_index,
                    "income_category_index": category_index,
                    "income_year": year,
                    "income_type": normalize_text(category_values.get("typeRevenu")),
                    "raw_value": raw_value,
                    "normalized_value": parse_french_number(raw_value),
                    "spouse_raw_value": spouse_raw,
                    "spouse_normalized_value": parse_french_number(spouse_raw),
                    "quality_status": "OK",
                    "quality_reason": None,
                    "raw_record_json": _raw_record(category_values),
                }
            )
        if not category_nodes and values.get("totalElu") is not None:
            raw_value = values.get("totalElu")
            rows.append(
                {
                    "declaration_uuid": declaration_uuid,
                    "snapshot_date": snapshot_date,
                    "source_section": "revenuMandatDto",
                    "source_item_index": item_index,
                    "income_category_index": None,
                    "income_year": year,
                    "income_type": "totalElu",
                    "raw_value": raw_value,
                    "normalized_value": parse_french_number(raw_value),
                    "spouse_raw_value": values.get("totalConjoint"),
                    "spouse_normalized_value": parse_french_number(values.get("totalConjoint")),
                    "quality_status": "OK",
                    "quality_reason": None,
                    "raw_record_json": _raw_record(values),
                }
            )
    return rows


def parse_csv(path: Path, snapshot_date: str) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, delimiter=";")
        if not reader.fieldnames:
            raise ValueError("HATVP CSV has no header")
        if "id_origine" not in reader.fieldnames and "url_dossier" not in reader.fieldnames:
            raise ValueError("HATVP CSV is missing expected identity columns")
        rows = []
        for row in reader:
            normalized = {
                key: normalize_text(value) for key, value in row.items() if key is not None
            }
            normalized["snapshot_date"] = snapshot_date
            normalized["source_file"] = "liste.csv"
            rows.append(normalized)
    return rows


def _empty_tables() -> dict[str, list[dict[str, Any]]]:
    return {
        "liste": [],
        "declarations": [],
        "people": [],
        "mandates": [],
        "activities": [],
        "participations": [],
        "incomes": [],
        "assets": [],
        "liabilities": [],
    }


def parse_xml(path: Path, snapshot_date: str) -> dict[str, list[dict[str, Any]]]:
    tables = _empty_tables()
    context = etree.iterparse(
        str(path),
        events=("start", "end"),
        recover=False,
        huge_tree=True,
        load_dtd=False,
        no_network=True,
        resolve_entities=False,
    )
    declaration_count = 0
    root: etree._Element | None = None
    top_level_child_count = 0
    try:
        for event, element in context:
            if event == "start":
                if root is None:
                    root = element
                    if _local_name(element.tag) != XML_ROOT_NAME:
                        raise ValueError(
                            f"HATVP XML has unexpected root element: {_local_name(element.tag)}"
                        )
                    continue
                if element.getparent() is root:
                    top_level_child_count += 1
                    child_name = _local_name(element.tag)
                    if child_name not in ALLOWED_TOP_LEVEL_CHILDREN:
                        raise ValueError(f"HATVP XML has invalid top-level element: {child_name}")
                continue

            if _local_name(element.tag) != "declaration":
                continue
            declaration_count += 1
            tables["declarations"].append(_declaration_row(element, snapshot_date))
            tables["people"].append(_person_row(element, snapshot_date))
            tables["mandates"].extend(_mandate_rows(element, snapshot_date))
            tables["activities"].extend(_activity_rows(element, snapshot_date))
            tables["participations"].extend(_participation_rows(element, snapshot_date))
            tables["incomes"].extend(_income_rows(element, snapshot_date))
            tables["assets"].extend(_asset_rows(element, snapshot_date))
            tables["liabilities"].extend(_liability_rows(element, snapshot_date))

            parent = element.getparent()
            element.clear()
            if parent is not None:
                while element.getprevious() is not None:
                    del parent[0]
    except etree.XMLSyntaxError as exc:
        raise ValueError(f"HATVP XML is malformed: {exc}") from exc
    if root is None:
        raise ValueError("HATVP XML is empty")
    if top_level_child_count == 0:
        raise ValueError("HATVP XML has no top-level declaration container")
    if declaration_count == 0:
        raise ValueError("HATVP XML contains no declaration records")
    return tables


def parse_sources(
    csv_path: Path,
    xml_path: Path,
    snapshot_date: str,
) -> dict[str, list[dict[str, Any]]]:
    tables = parse_xml(xml_path, snapshot_date)
    tables["liste"] = parse_csv(csv_path, snapshot_date)
    return tables
