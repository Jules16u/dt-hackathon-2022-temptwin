"""Hydroquebec customer module."""
import logging

from hydroqc.account import Account
from hydroqc.contract import Contract
from hydroqc.error import HydroQcError
from hydroqc.hydro_api.client import HydroClient
from hydroqc.logger import get_logger


class Customer:
    """Hydroquebec customer.

    Represents one customer (Titulaire)
    """

    def __init__(
        self,
        webuser_id: str,
        customer_id: str,
        customer_names: list[str],
        hydro_client: HydroClient,
        log_level: str | None = None,
    ):
        """Create a new customer."""
        self._logger: logging.Logger = get_logger(
            f"c-{customer_id}", log_level, parent=f"w-{webuser_id}"
        )
        self._log_level: str | None = log_level
        self._no_partenaire_demandeur: str = webuser_id
        self._no_partenaire_titulaire: str = customer_id
        self._nom_titulaires: list[str] = customer_names
        self._hydro_client: HydroClient = hydro_client
        self.accounts: list[Account] = []
        self._firstname: str = ""
        self._lastname: str = ""
        self._language: str = ""
        self._id_technique: str = ""

    async def get_info(self) -> None:
        """Retrieve account id, customer id and contract id."""
        self._logger.info("Get customer info")
        customer_data = await self._hydro_client.get_customer_info(
            self.webuser_id, self.customer_id
        )
        if not customer_data["infoCockpitPourPartenaireModel"]:
            return

        self._firstname = customer_data["infoCockpitPourPartenaireModel"]["prenom"]
        self._lastname = customer_data["infoCockpitPourPartenaireModel"]["nom"]
        self._email = customer_data["infoCockpitPourPartenaireModel"]["courriel"]
        self._language = customer_data["infoCockpitPourPartenaireModel"][
            "langueCorrespondance"
        ]
        self._id_technique = customer_data["infoCockpitPourPartenaireModel"][
            "idTechnique"
        ]

        for raw_account_data in customer_data["infoCockpitPourPartenaireModel"][
            "listeComptesContrats"
        ]:
            account_id = raw_account_data["noCompteContrat"]
            # Create new account if it's not there
            if account_id not in [a.account_id for a in self.accounts]:
                self._logger.info("Creating new account %s", account_id)
                account = Account(
                    self.webuser_id,
                    self.customer_id,
                    account_id,
                    [],
                    self._hydro_client,
                    self._log_level,
                )
                self.accounts.append(account)
            else:
                account = [a for a in self.accounts if a.account_id == account_id][0]
            await account.get_info()

            for contract_id in raw_account_data["listeNoContrat"]:
                if contract_id not in [c.contract_id for c in account.contracts]:
                    self._logger.info("Creating new contracts %s", contract_id)
                    contract = Contract(
                        self.webuser_id,
                        self.customer_id,
                        account_id,
                        contract_id,
                        self._hydro_client,
                        self._log_level,
                    )
                    account.contracts.append(contract)
                else:
                    contract = [
                        c for c in account.contracts if c.contract_id == contract_id
                    ][0]
                await contract.get_info()

    @property
    def webuser_id(self) -> str:
        """Get webuser id."""
        return self._no_partenaire_demandeur

    @property
    def customer_id(self) -> str:
        """Get customer id."""
        return self._no_partenaire_titulaire

    @property
    def names(self) -> list[str]:
        """Could be ["firstname", "lastname"] or ["fullname1", "fullname2"]."""
        return self._nom_titulaires

    def get_account(self, account_id: str) -> Account:
        """Find account by id."""
        if not (accounts := [c for c in self.accounts if c.account_id == account_id]):
            raise HydroQcError(f"Account {account_id} not found")
        return accounts[0]

    def __repr__(self) -> str:
        """Represent object."""
        return f"""<Customer - {self.webuser_id} - {self.customer_id}>"""
