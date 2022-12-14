"""Hydroqc custom types."""
# pylint: disable=invalid-name
from typing import TypedDict


# API URL: https://cl-ec-spring.hydroquebec.com/portail/fr/group/clientele/
# portrait-de-consommation/resourceObtenirDonneesConsommationHoraires
class ConsoHourlyResultTyping(TypedDict, total=True):
    """Consumption Hourly json sub output format."""

    heure: "str"
    consoReg: float
    consoHaut: float
    consoTotal: float
    codeConso: str
    codeEvemenentEnergie: str
    zoneMessageHTMLEnergie: str | None


class ConsoHourlyResultsTyping(TypedDict, total=True):
    """Consumption Hourly json sub output format."""

    codeTarif: str
    affichageTarifFlex: bool
    dateJour: str
    echelleMinKwhHeureParJour: int
    echelleMaxKwhHeureParJour: int
    zoneMsgHTMLNonDispEnergie: str | None
    zoneMsgHTMLNonDispPuissance: str | None
    indErreurJourneeEnergie: bool
    indErreurJourneePuissance: bool
    listeDonneesConsoEnergieHoraire: list[ConsoHourlyResultTyping]


class ConsoHourlyTyping(TypedDict, total=True):
    """Consumption Hourly json output format."""

    success: bool
    results: ConsoHourlyResultsTyping


# API URL: https://cl-ec-spring.hydroquebec.com/portail/fr/group/clientele/
# portrait-de-consommation/resourceObtenirDonneesQuotidiennesConsommation
class ConsoDailyResultTyping(TypedDict, total=True):
    """Consumption Daily json sub output format."""

    dateJourConso: str
    zoneMessageHTMLQuot: str | None
    consoRegQuot: float
    consoHautQuot: float
    consoTotalQuot: float
    codeConsoQuot: str
    tempMoyenneQuot: int
    codeTarifQuot: str
    affichageTarifFlexQuot: bool
    codeEvenementQuot: str


class ConsoDailyResultsTyping(TypedDict, total=True):
    """Consumption Daily json sub output format."""

    courant: ConsoDailyResultTyping
    compare: ConsoDailyResultTyping


class ConsoDailyTyping(TypedDict, total=True):
    """Consumption Daily json output format."""

    success: bool
    results: list[ConsoDailyResultsTyping]


# API URL: https://cl-ec-spring.hydroquebec.com/portail/fr/group/clientele/
# portrait-de-consommation/resourceObtenirDonneesConsommationMensuelles
class ConsoMonthlyResultTyping(TypedDict, total=True):
    """Consumption Monthly json sub output format."""

    dateDebutMois: str
    dateFinMois: str
    codeConsoMois: str
    nbJourCalendrierMois: int
    presenceTarifDTmois: bool
    tempMoyenneMois: int
    moyenneKwhJourMois: float
    affichageTarifFlexMois: bool
    consoRegMois: int
    consoHautMois: int
    consoTotalMois: int
    zoneMessageHTMLMois: str | None
    indPresenceCodeEvenementMois: bool


class ConsoMonthlyResultsTyping(TypedDict, total=True):
    """Consumption Monthly json sub output format."""

    courant: ConsoMonthlyResultTyping
    compare: ConsoMonthlyResultTyping


class ConsoMonthlyTyping(TypedDict, total=True):
    """Consumption Monthly json output format."""

    success: bool
    results: list[ConsoMonthlyResultsTyping]


# API URL: https://cl-ec-spring.hydroquebec.com/portail/fr/group/clientele/
# portrait-de-consommation/resourceObtenirDonneesConsommationAnnuelles
class ConsoAnnualCompareTyping(TypedDict, total=True):
    """Consumption Annual json sub output format."""

    dateDebutAnnee: str
    dateFinAnnee: str
    nbJourCalendrierAnnee: int
    moyenneKwhJourAnnee: float
    consoRegAnnee: int
    consoHautAnnee: int
    consoTotalAnnee: int
    montantFactureAnnee: float
    moyenneDollarsJourAnnee: float
    isEligibleDRCV: bool
    codeTarifAnnee: str
    montantGainPerteDTversusBaseAnnee: int
    montantChauffageAnnee: int
    montantClimatisationAnnee: int
    kwhChauffageAnnee: int
    kwhClimatisationAnnee: int
    coutCentkWh: float


class ConsoAnnualCurrentTyping(ConsoAnnualCompareTyping, total=True):
    """Consumption Annual json sub output format."""

    zoneMsgHTMLAnneeSuiviDT: str
    texteValeurChauffage: str | None
    texteValeurClimatisation: str | None
    tooltipIdChauffage: str
    tooltipIdClimatisation: str
    tooltipIdChauffageComparaison: str
    tooltipIdClimatisationComparaison: str


class ConsoAnnualResultsTyping(TypedDict, total=True):
    """Consumption Annual json sub output format."""

    courant: ConsoAnnualCurrentTyping
    compare: ConsoAnnualCompareTyping


class ConsoAnnualTyping(TypedDict, total=True):
    """Consumption Annual json output format."""

    success: bool
    results: list[ConsoAnnualResultsTyping]
