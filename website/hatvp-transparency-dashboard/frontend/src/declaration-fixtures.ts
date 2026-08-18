export const declarationXmlFixtures = [
  `<declaration>
    <dateDepot>01/12/2025 08:30:00</dateDepot><uuid>fixture-uuid-1</uuid><origine>ADEL</origine><complete>true</complete><declarationVersion>20171221</declarationVersion>
    <mandatElectifDto><items><items><descriptionMandat>Maire</descriptionMandat><dateDebut>01/2020</dateDebut><dateFin/><remuneration><brutNet>brut</brutNet><montant>50 000,00</montant><annee>2025</annee></remuneration></items></items><neant>false</neant></mandatElectifDto>
    <participationFinanciereDto><items><items><nomSociete>ACME</nomSociete><evaluation>1 200,50</evaluation><nombreParts>10</nombreParts></items></items><neant>false</neant></participationFinanciereDto>
    <comptesBancaireDto><items><items><typeCompte>Compte courant</typeCompte><etablissement>Banque</etablissement><valeur>12 345,67</valeur></items></items><neant>false</neant></comptesBancaireDto>
    <revenuMandatDto><items><items><annee>2025</annee><revenuMandatItem0><typeRevenu>Traitements</typeRevenu><revenuElu>12 000,00</revenuElu><revenuConjoint/></revenuMandatItem0></items></items><neant>false</neant></revenuMandatDto>
    <general><typeDeclaration><id>DI</id><label>Déclaration d'intérêts</label></typeDeclaration><mandat><label>Élu local</label></mandat><qualiteMandat><typeMandat>Élu municipal</typeMandat></qualiteMandat><organe><labelOrgane>Paris</labelOrgane></organe><declarant><civilite>M.</civilite><nom>DUPONT</nom><prenom>Alice</prenom></declarant></general>
  </declaration>`,
  `<declaration>
    <dateDepot>14/01/2025 12:36:29</dateDepot><uuid>fixture-uuid-2</uuid><origine>ADEL</origine><complete>true</complete><declarationVersion>20171221</declarationVersion>
    <activProfCinqDerniereDto><items><items><description>Ingénieur systèmes et réseaux</description><employeur>Orange</employeur><brutNet>Net</brutNet><annee>2020</annee><montant>49 310</montant><annee>2021</annee><montant>48 527</montant></items></items><neant>false</neant></activProfCinqDerniereDto>
    <activProfConjointDto><items><items><nomConjoint>[Données non publiées]</nomConjoint><employeurConjoint>Pharmacie</employeurConjoint><activiteProf>Pharmacienne</activiteProf></items></items><neant>false</neant></activProfConjointDto>
    <activCollaborateursDto><items><items><nom>Ribardière Astrid</nom><descriptionActivite>Collaboratrice à temps plein</descriptionActivite></items><items><nom>Nivole Audrey</nom><descriptionActivite>Alternante</descriptionActivite></items></items><neant>false</neant></activCollaborateursDto>
    <fonctionBenevoleDto><neant>true</neant></fonctionBenevoleDto>
    <general><typeDeclaration><label>Déclaration d'intérêts et d'activités</label></typeDeclaration><mandat><label>Député ou sénateur</label></mandat><qualiteMandat><typeMandat>Député</typeMandat></qualiteMandat><organe><labelOrgane>Département d'élection</labelOrgane></organe><declarant><civilite>Mme</civilite><nom>MARTIN</nom><prenom>Claire</prenom></declarant></general>
  </declaration>`,
  `<declaration>
    <dateDepot>08/12/2025 23:24:22</dateDepot><uuid>fixture-uuid-3</uuid><origine>ADEL</origine><complete>true</complete><declarationVersion>0</declarationVersion>
    <immeubleDto><items><items><nature>Maison individuelle</nature><superficieBati>170</superficieBati><dateAcquisition>2015</dateAcquisition><valeur>380 000</valeur><droitReel>Pleine propriété</droitReel></items></items><neant>false</neant></immeubleDto>
    <valeursEnBourseDto><items><items><etablissement>Crédit agricole</etablissement><naturePlacement>Compte titre</naturePlacement><valeur>96</valeur></items></items><neant>false</neant></valeursEnBourseDto>
    <assuranceVieDto><items><items><souscripteur>GEFFRAY Edouard</souscripteur><etablissement>Crédit agricole</etablissement><valeurRachat>53 427</valeurRachat></items></items><neant>false</neant></assuranceVieDto>
    <comptesBancaireDto><items><items><typeCompte>Compte courant</typeCompte><etablissement>La banque postale</etablissement><valeur>38 381</valeur></items></items><neant>false</neant></comptesBancaireDto>
    <vehiculeDto><items><items><nature>Terrestre à moteur</nature><marque>Peugeot</marque><anneeAchat>2015</anneeAchat><valeurAchat>24 500</valeurAchat><valeur>10 000</valeur></items></items><neant>false</neant></vehiculeDto>
    <passifDto><items><items><nomCreancier>Crédit agricole</nomCreancier><nature>Emprunt immobilier</nature><montant>166306</montant><restantDu>68792</restantDu><mensualite>2100</mensualite></items></items><neant>false</neant></passifDto>
    <general><typeDeclaration><label>Déclaration de situation patrimoniale</label></typeDeclaration><mandat><label>Membre du Gouvernement</label></mandat><qualiteMandat><typeMandat>Membre</typeMandat></qualiteMandat><organe><labelOrgane>Intitulé du ministère</labelOrgane></organe><declarant><civilite>M.</civilite><nom>GEFFRAY</nom><prenom>Edouard</prenom></declarant></general>
  </declaration>`,
  `<declaration>
    <dateDepot>07/01/2026 18:24:16</dateDepot><uuid>fixture-uuid-4</uuid><origine>ADEL</origine><complete>true</complete><declarationVersion>20171221</declarationVersion>
    <attachedFiles><items><fileName>kbis.pdf</fileName><serverFileName>fixture-uuid-4_pj01</serverFileName></items><items><fileName>agreement.pdf</fileName><serverFileName>fixture-uuid-4_pj02</serverFileName></items></attachedFiles>
    <participationDirigeantDto><items><items><nomSociete>Lola invest</nomSociete><activite>Holding</activite><annee>2023</annee><montant>0</montant><annee>2024</annee><montant>15 001</montant></items></items><neant>false</neant></participationDirigeantDto>
    <participationFinanciereDto><items><items><nomSociete>Lola invest</nomSociete><evaluation>3 355 000</evaluation><capitalDetenu>20</capitalDetenu><nombreParts>199</nombreParts></items></items><neant>false</neant></participationFinanciereDto>
    <activConsultantDto><neant>true</neant></activConsultantDto><observationInteretDto><neant>true</neant></observationInteretDto>
    <general><typeDeclaration><label>Déclaration d'intérêts et d'activités</label></typeDeclaration><mandat><label>Député ou sénateur</label></mandat><qualiteMandat><typeMandat>Député</typeMandat></qualiteMandat><organe><labelOrgane>Département d'élection</labelOrgane></organe><declarant><civilite>Mme</civilite><nom>LEGRAND</nom><prenom>Emma</prenom></declarant></general>
  </declaration>`,
  `<declaration>
    <dateDepot>14/02/2025 16:45:11</dateDepot><uuid>fixture-uuid-5</uuid><origine>ADEL</origine><complete>false</complete><declarationVersion>20171221</declarationVersion>
    <activProfCinqDerniereDto><items><items><description>Professeur d'université</description><employeur>Université</employeur><brutNet>Net</brutNet><annee>2019</annee><montant>62 001</montant><annee>2020</annee><montant>61 807</montant><annee>2021</annee><montant>62 149</montant></items></items><neant>false</neant></activProfCinqDerniereDto>
    <mandatElectifDto><items><items><descriptionMandat>Conseiller municipal</descriptionMandat><dateDebut>03/2020</dateDebut><dateFin/><annee>2020</annee><montant>1 904</montant><annee>2021</annee><montant>3 265</montant></items></items><neant>false</neant></mandatElectifDto>
    <participationFinanciereDto><items><items><nomSociete>SCI familiale</nomSociete><evaluation>523 976</evaluation><remuneration>0</remuneration><capitalDetenu>99</capitalDetenu><nombreParts>1492</nombreParts></items></items><neant>false</neant></participationFinanciereDto>
    <general><typeDeclaration><label>Déclaration d'intérêts et d'activités modificative</label></typeDeclaration><mandat><label>Député ou sénateur</label></mandat><qualiteMandat><typeMandat>Député</typeMandat></qualiteMandat><organe><labelOrgane>Département d'élection</labelOrgane></organe><declarant><civilite>M.</civilite><nom>ROUX</nom><prenom>Louis</prenom></declarant></general>
  </declaration>`,
] as const;
