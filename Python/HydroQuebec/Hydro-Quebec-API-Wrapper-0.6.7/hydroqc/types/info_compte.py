"""Info compte json output formats."""
# pylint: disable=invalid-name
from typing import Any, TypedDict


# https://cl-services.idp.hydroquebec.com/cl/prive/api/v1_0/relations
class ComptesTyping(TypedDict, total=True):
    """Comptes json output format."""

    noPartenaireDemandeur: str
    nom1Demandeur: str
    nom2Demandeur: str
    noPartenaireTitulaire: str
    nom1Titulaire: str
    nom2Titulaire: str
    typeRelation: str
    indEcActif: bool
    indFavori: bool
    nickname: str
    actif: bool | None  # Could be not present
    dateDebutRelation: str | None  # Could be not present
    dateFinRelation: str | None  # Could be not present


# .../cl/prive/api/v3_0/partenaires/infoCompte
class listeComptesContratsTyping(TypedDict, total=True):
    """Info compte json sub output format."""

    titulaire: str
    nomTitulaire: str
    prenomTitulaire: str
    raisonSocialeTitulaire1: str
    raisonSocialeTitulaire2: str
    nomGroupeTitulaire1: str
    nomGroupeTitulaire2: str
    categorieTitulaire: str
    adresse: str
    modeEncaissement: str
    payeurDivergent: str
    dateEmission: str
    montantEchu: float
    typeMVE: str
    indContrats: bool
    indFinEventuelleCC: bool
    typeRelation: str
    indDonneesErreur: bool
    factureIXOSID: str
    documentArchivelinkID: str
    dateFin: str | None
    dateDebug: str | None
    indicateurPA: bool
    compteBancaire: str | None
    adresseFacturation: str
    regroupement: str
    listePaiements: list[str]
    noCompteContrat: str
    dateEcheance: str
    montant: float
    solde: float
    soldeEnSouffrance: float
    dernierMontantPaye: float
    contientPaiementsPostDates: bool
    coche: bool
    listeNoContrat: list[str]
    dateProchaineFacture: str
    typeDateProchaineFacture: str
    segmentation: str
    sousConsommationMVE: bool
    surConsommationMVE: bool
    revisionAnnuelleMVE: bool
    infoEligibiliteConfirmationPaiement: str | None
    noPartenaireMandataire: str | None
    infoEligibiliteEntentePaiement: str | None
    infoEligibiliteConfirmPaiementOuEntente: str | None
    indProjection: bool
    typeEntenteSansProjection: str
    gereDansEspaceClient: bool
    idBanque: str
    institution: str
    succursale: str
    folio: str
    libelle: str
    indBloquerPI: bool


class infoCockpitPourPartenaireModelTyping(TypedDict, total=True):
    """Info compte json output formats."""

    noPartenaire: str
    nom: str
    idTechnique: str
    prenom: str
    courriel: str
    segmentation: str
    categorie: str
    raisonSociale1: str
    raisonSociale2: str
    langueCorrespondance: str
    indPagePersonnelleActive: bool
    indFactureInternet: bool
    indPaiementInternet: bool
    indAucunCompteContrat: bool
    indDonneesConsommation: bool
    dateDerniereVisite: str
    etatFacturePapier: str
    listeComptesContrats: list[listeComptesContratsTyping]


class listeContratModelTyping(TypedDict, total=True):
    """Info compte json output formats."""

    codeResponsabilite: str | None
    noContrat: str
    adresseConsommation: str
    idLieuConsommation: str
    noCompteContrat: str
    noInstallation: str
    noCompteur: str
    indicateurPortrait: bool
    indicateurDiagnostique: bool
    indicateurDiagnostiqueDR: bool
    documentArchivelinkID: str
    codeDiagnostique: str
    codeDiagnostiqueDR: str
    indicateurAutoReleve: bool
    indicateurMVE: bool
    adhesionMVEEncours: bool
    retraitMVEEnCours: bool
    desinscritMVE: bool
    sousConsommationMVE: bool
    surConsommationMVE: bool
    mntEcart: float
    revisionAnnuelleMVE: bool
    indicateurEligibiliteMVE: bool
    codePortrait: str
    codeAutoReleve: str
    noCivique: str
    rue: str
    appartement: str
    ville: str
    codePostal: str
    dateDebutContrat: str
    dateFinContrat: str | None
    contratAvecArriveePrevue: bool
    contratAvecArriveePrevueDansLePasse: bool
    contratAvecDepartPrevu: bool
    contratAvecDepartPrevuDansLePasse: bool
    departPrevuSansAvis: bool
    numeroTelephone: str
    posteTelephone: str
    indPuissance: bool
    codeAdhesionCPC: str
    codeEligibiliteCPC: str | None
    codeEligibiliteCLT: str | None
    tarifActuel: str
    optionTarifActuel: str
    codeEligibiliteDRCV: str
    dateDebutEligibiliteDRCV: str | None
    indEligibiliteDRCV: bool


class InfoCompteTyping(TypedDict, total=True):
    """Info compte json output format."""

    indEligibilite: bool
    infoCockpitPourPartenaireModel: infoCockpitPourPartenaireModelTyping
    listeContratModel: list[listeContratModelTyping]
    listeInfoEligibiliteConfirmPaiementOuEntenteModel: list[Any]
