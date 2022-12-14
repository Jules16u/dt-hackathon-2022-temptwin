"""Hydroqc custom types."""
from typing import TypedDict


class PeriodDataTyping(TypedDict, total=True):
    """Winter Credit Period json output format."""

    nbJourLecturePeriode: int
    nbJourPrevuPeriode: int
    montantFacturePeriode: float
    montantProjetePeriode: float
    moyenneDollarsJourPeriode: float
    moyenneKwhJourPeriode: float
    consoTotalPeriode: float
    consoTotalProjetePeriode: float
    consoRegPeriode: float
    consoHautPeriode: float
    tempMoyennePeriode: float
    coutCentkWh: float | None
    dernierTarif: str
    indMVEPeriode: bool


# Winter credits
class CriticalPeakDataTyping(TypedDict, total=False):
    """Winter Credit json sub output format."""

    dateEffacement: str
    heureDebut: str
    heureFin: str
    consoReelle: float
    consoReference: float
    consoEffacee: float
    montantEffacee: float
    codeConso: str
    indFacture: bool


class CriticalPeaksDataTyping(TypedDict, total=True):
    """Winter Credit json sub output format."""

    dateDebutPeriodeHiver: str
    dateFinPeriodeHiver: str
    periodesEffacementHiver: list[CriticalPeakDataTyping]


class TotalCriticalPeaksDataTyping(TypedDict, total=True):
    """Winter Credit json sub output format."""

    dateDebutPeriodeHiver: str
    consoEffacee: float
    montantEfface: float


class WinterCreditDataTyping(TypedDict, total=False):
    """Winter Credit json output format."""

    adresseCourriel: str
    adresseLieuConso1: str
    adresseLieuConso2: str
    codeAdhesionCPC: str
    codeEligibiliteCPC: str
    codeUsageContrat: str
    dateDebutAdhesionCPC: str
    dateFinAdhesionCPC: str
    indAppelRequis: bool
    montantEffaceProjete: str
    etatMontantEffaceeProjete: str
    nomMarketingActuel: str
    nomMarketingBase: str
    nomMarketingCPC: str
    optionTarifActuel: str
    optionTarifBase: str
    optionTarifCPC: str
    tarifActuel: str
    tarifBase: str
    tarifCPC: str
    success: bool
    periodesEffacementsHivers: list[CriticalPeaksDataTyping]
    cumulPeriodesEffacementsHivers: list[TotalCriticalPeaksDataTyping]
    # infoSimulation: list
