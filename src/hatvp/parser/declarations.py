"""Declaration, person, and general-mandate parsers."""

from typing import Any

from lxml import etree

from ..models import ParseContext, ParserConfig
from ..normalize import birth_fields, parse_date
from ..xml_support import child, element_record, item_groups, normalized_child_text, raw_child_text
from .declaration_support import income_item_has_value
from .mandates import mandate_rows


def declaration_row(
    element: etree._Element, context: ParseContext, config: ParserConfig
) -> dict[str, Any]:
    general = child(element, "general")
    declaration_type = child(general, "typeDeclaration")
    mandate = child(general, "mandat")
    quality = child(general, "qualiteMandat")
    organ = child(general, "organe")
    income_section = child(element, config.sections["income"])
    depot_raw = raw_child_text(element, "dateDepot")
    start_raw = raw_child_text(general, "dateDebutMandat")
    end_raw = raw_child_text(general, "dateFinMandat")
    return {
        "declaration_uuid": normalized_child_text(element, "uuid"),
        "snapshot_date": context.snapshot_date,
        "source_file": context.source_file,
        "raw_record_json": element_record(element),
        "date_depot_raw": depot_raw,
        "date_depot": parse_date(depot_raw),
        "origine": normalized_child_text(element, "origine"),
        "complete": normalized_child_text(element, "complete"),
        "declaration_version": normalized_child_text(element, "declarationVersion"),
        "declaration_type_id": normalized_child_text(declaration_type, "id"),
        "declaration_type_label": normalized_child_text(declaration_type, "label"),
        "income_section_present": income_section is not None,
        "income_section_populated_item_count": sum(
            income_item_has_value(item) for item in item_groups(income_section)
        ),
        "mandat_label": normalized_child_text(mandate, "label")
        or normalized_child_text(general, "mandat"),
        "mandat_type": normalized_child_text(quality, "typeMandat"),
        "mandat_category_code": normalized_child_text(quality, "codCategorieMandat"),
        "mandat_category_label": normalized_child_text(quality, "nomCategorieMandat"),
        "mandat_file_type": normalized_child_text(quality, "codTypeMandatFichier"),
        "mandat_type_label": normalized_child_text(quality, "labelTypeMandat"),
        "organ_code": normalized_child_text(organ, "codeOrgane"),
        "organ_code_list": normalized_child_text(organ, "codeListeOrgane"),
        "organ_label": normalized_child_text(organ, "labelOrgane"),
        "organ_declaration_label": normalized_child_text(organ, "labelDeclaration"),
        "organ_parent": normalized_child_text(organ, "organeParent"),
        "quality_declarant": normalized_child_text(general, "qualiteDeclarant"),
        "quality_declarant_pdf": normalized_child_text(general, "qualiteDeclarantForPDF"),
        "date_debut_mandat_raw": start_raw,
        "date_debut_mandat": parse_date(start_raw),
        "date_fin_mandat_raw": end_raw,
        "date_fin_mandat": parse_date(end_raw),
        "date_derniere_declaration_raw": raw_child_text(general, "dateDernDeclar"),
        "declaration_modificative": normalized_child_text(general, "declarationModificative"),
    }


def person_row(element: etree._Element, context: ParseContext) -> dict[str, Any]:
    general = child(element, "general")
    person = child(general, "declarant")
    address = child(person, "adresseDec")
    civilite = normalized_child_text(person, "civilite")
    birth_raw = raw_child_text(person, "dateNaissance")
    birth = parse_date(birth_raw)
    fields = {
        "civilite": civilite,
        "gender": {"M.": "male", "Mme": "female"}.get(civilite),
        "nom": normalized_child_text(person, "nom"),
        "prenom": normalized_child_text(person, "prenom"),
        "email": normalized_child_text(person, "email"),
        "date_naissance_raw": birth_raw,
        "date_naissance": birth,
        **birth_fields(birth_raw),
        "telephone_dec": normalized_child_text(person, "telephoneDec"),
        "raw_record_json": element_record(person),
    }
    fields.update(
        {
            f"adresse_{name}": normalized_child_text(address, name)
            for name in ("voie", "complement", "codePostal", "ville", "pays")
        }
    )
    return {
        "declaration_uuid": normalized_child_text(element, "uuid"),
        "snapshot_date": context.snapshot_date,
        "source_file": context.source_file,
        **fields,
    }


def declaration_mandates(element, context, config):
    return mandate_rows(element, context, config)
