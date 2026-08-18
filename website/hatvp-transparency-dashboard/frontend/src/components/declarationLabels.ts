import type { Language } from "../config/i18n";

const SECTION_LABELS: Record<string, [string, string]> = {
  general: ["Public profile", "Profil public"],
  attachedFiles: ["Attachments", "Pièces jointes"],
  activConsultantDto: ["Consulting activities", "Activités de conseil"],
  activProfCinqDerniereDto: ["Professional activities", "Activités professionnelles"],
  activProfConjointDto: ["Spouse or partner activity", "Activité du conjoint ou partenaire"],
  fonctionBenevoleDto: ["Volunteer roles", "Fonctions bénévoles"],
  mandatElectifDto: ["Elected mandates", "Mandats électifs"],
  revenuMandatDto: ["Other declared income", "Autres revenus déclarés"],
  participationDirigeantDto: ["Leadership positions", "Fonctions dirigeantes"],
  participationFinanciereDto: ["Financial interests", "Participations financières"],
  activCollaborateursDto: ["Collaborators", "Collaborateurs"],
  observationInteretDto: ["Interest observations", "Observations sur les intérêts"],
  immeubleDto: ["Real estate", "Immobilier"],
  sciDto: ["Property-holding companies", "Sociétés immobilières"],
  valeursNonEnBourseDto: ["Unlisted securities", "Valeurs non cotées"],
  valeursEnBourseDto: ["Listed securities", "Valeurs cotées"],
  assuranceVieDto: ["Life insurance", "Assurance-vie"],
  comptesBancaireDto: ["Bank accounts", "Comptes bancaires"],
  bienDiverDto: ["Miscellaneous assets", "Biens divers"],
  vehiculeDto: ["Vehicles", "Véhicules"],
  fondDto: ["Funds", "Fonds"],
  autreBienDto: ["Other assets", "Autres biens"],
  bienEtrangerDto: ["Foreign property", "Biens à l’étranger"],
  passifDto: ["Liabilities", "Passif"],
  evenementMajeurDto: ["Major events", "Événements majeurs"],
  observationPatrimoineDto: ["Asset observations", "Observations sur le patrimoine"],
};

const FIELD_LABELS: Record<string, [string, string]> = {
  dateDepot: ["Deposit date", "Date de dépôt"],
  uuid: ["Declaration ID", "Identifiant de la déclaration"],
  origine: ["Source system", "Système source"],
  complete: ["Complete record", "Dossier complet"],
  declarationVersion: ["Source version", "Version source"],
  label: ["Label", "Libellé"],
  descriptionMandat: ["Mandate", "Mandat"],
  description: ["Description", "Description"],
  commentaire: ["Comment", "Commentaire"],
  dateDebut: ["Start date", "Date de début"],
  dateFin: ["End date", "Date de fin"],
  annee: ["Year", "Année"],
  montant: ["Amount", "Montant"],
  revenuElu: ["Declarant income", "Revenu du déclarant"],
  revenuConjoint: ["Spouse or partner income", "Revenu du conjoint ou partenaire"],
  brutNet: ["Gross or net", "Brut ou net"],
  nomSociete: ["Company", "Société"],
  evaluation: ["Estimated value", "Valeur estimée"],
  valeur: ["Current value", "Valeur actuelle"],
  valeurAchat: ["Purchase value", "Valeur d’achat"],
  valeurRachat: ["Cash surrender value", "Valeur de rachat"],
  restantDu: ["Remaining balance", "Capital restant dû"],
  typeCompte: ["Account type", "Type de compte"],
  etablissement: ["Institution", "Établissement"],
  nature: ["Nature", "Nature"],
  adresse: ["Address", "Adresse"],
  employeur: ["Employer", "Employeur"],
  nom: ["Name", "Nom"],
  prenom: ["First name", "Prénom"],
  civilite: ["Title", "Civilité"],
  email: ["Email", "E-mail"],
  dateNaissance: ["Date of birth", "Date de naissance"],
  neant: ["None declared", "Néant"],
};

function humanize(value: string): string {
  return value
    .replace(/Dto$/, "")
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/^./, (character) => character.toUpperCase());
}

export function declarationSectionLabel(key: string, language: Language): string {
  return SECTION_LABELS[key]?.[language === "fr" ? 1 : 0] || humanize(key);
}

export function declarationFieldLabel(key: string, language: Language): string {
  return FIELD_LABELS[key]?.[language === "fr" ? 1 : 0] || humanize(key);
}

export function sectionIcon(key: string): string {
  if (key === "general") return "◉";
  if (key === "mandatElectifDto") return "↗";
  if (key.includes("activ") || key.includes("fonction") || key.includes("participation")) return "◎";
  if (key.includes("passif")) return "−";
  if (key.includes("immeuble") || key.includes("sci") || key.includes("bien")) return "⌂";
  if (key.includes("compte") || key.includes("valeur") || key.includes("assurance") || key.includes("fond")) return "€";
  return "•";
}
