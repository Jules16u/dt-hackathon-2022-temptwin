"""HydroQc Client Module."""
import base64
import importlib.resources
import json
import logging
import random
import ssl
import string
import time
import uuid
from datetime import datetime, timedelta
from json import dumps as json_dumps
from typing import Any

import aiohttp
from hydroqc.error import HydroQcError, HydroQcHTTPError
from hydroqc.hydro_api.cache import CCached
from hydroqc.hydro_api.consts import (
    ANNUAL_DATA_URL,
    AUTH_URL,
    AUTHORIZE_URL,
    CUSTOMER_INFO_URL,
    DAILY_CONSUMPTION_API_URL,
    GET_WINTER_CREDIT_API_URL,
    HOURLY_CONSUMPTION_API_URL,
    LOGIN_URL_6,
    MONTHLY_DATA_URL,
    PERIOD_DATA_URL,
    PORTRAIT_URL,
    RELATION_URL,
    REQUESTS_TIMEOUT,
    SECURITY_URL,
    SESSION_REFRESH_URL,
    SESSION_URL,
)
from hydroqc.logger import get_logger
from hydroqc.winter_credit.consts import EST_TIMEZONE

from hydroqc.types import (
    ComptesTyping,
    ConsoAnnualTyping,
    ConsoDailyTyping,
    ConsoHourlyTyping,
    ConsoMonthlyTyping,
    InfoCompteTyping,
    PeriodDataTyping,
    WinterCreditDataTyping,
    listeComptesContratsTyping,
    listeContratModelTyping,
)


class HydroClient:
    """HydroQc HTTP Client."""

    _id_token: str
    access_token: str
    _selected_customer: str
    _selected_contract: str
    cookies: dict[str, Any]

    def __init__(
        self,
        username: str,
        password: str,
        timeout: int = REQUESTS_TIMEOUT,
        verify_ssl: bool = True,
        session: aiohttp.ClientSession | None = None,
        log_level: str | None = "INFO",
    ):
        """Initialize the client object."""
        self.username: str = username
        self.password: str = password
        self._timeout: int = timeout
        self._session: aiohttp.ClientSession | None = session
        self._verify_ssl: bool = verify_ssl
        with importlib.resources.path(
            __package__, "hydro-chain.pem"
        ) as hydro_chain_pem_file:
            self._sslcontext: ssl.SSLContext = ssl.create_default_context(
                cafile=hydro_chain_pem_file
            )
            self._sslcontext.set_ciphers("DEFAULT")  # Needed for python3.10
        self.guid: str = str(uuid.uuid1())
        self._logger: logging.Logger = get_logger("httpclient", log_level)
        self._logger.debug("HydroQc initialized")
        self.reset()

    def reset(self) -> None:
        """Reset collected data and temporary variable."""
        self._id_token = ""
        self.access_token = ""
        self.cookies = {}
        self._selected_customer = ""
        self._selected_contract = ""

    async def http_request(
        self,
        url: str,
        method: str,
        params: dict[str, Any] | None = None,
        data: str | dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        verify_ssl: bool | None = None,
        cookies: dict[str, Any] | None = None,
        status: int | None = 200,
    ) -> aiohttp.ClientResponse:
        """Prepare and run HTTP/S request."""
        site = url.split("/")[2]
        if params is None:
            params = {}
        if data is None:
            data = {}
        if headers is None:
            headers = {}
        if verify_ssl is None:
            verify_ssl = self._verify_ssl
        if cookies is None:
            if site not in self.cookies:
                self.cookies[site] = {}
            cookies = self.cookies[site]
        ssl_context = None
        if verify_ssl:
            ssl_context = self._sslcontext

        self._logger.debug("HTTP query %s to %s", url, method)
        raw_res: aiohttp.ClientResponse = await getattr(self._session, method)(
            url,
            params=params,
            data=data,
            allow_redirects=False,
            ssl=ssl_context,
            cookies=cookies,
            headers=headers,
        )
        if raw_res.status != status:
            self._logger.exception("Exception in http_request")
            data = await raw_res.text()
            self._logger.debug(data)
            raise HydroQcHTTPError(f"Error Fetching {url} - {raw_res.status}")

        for cookie, cookie_content in raw_res.cookies.items():
            if hasattr(cookie_content, "value"):
                self.cookies[site][cookie] = cookie_content.value
            else:
                self.cookies[site][cookie] = cookie_content

        return raw_res

    def _load_json(self, data: str | bytes) -> Any:
        """Safely read json, raise a HydroQcHTTPError when parsing fails."""
        try:
            return json.loads(data)
        except json.decoder.JSONDecodeError as exp:
            self._logger.debug("JSON received : ", data)
            raise HydroQcHTTPError("Bad JSON format") from exp

    @property
    def session_expired(self) -> bool:
        """Get Oauth session expired or not.

        returns True if the session has expired.
        """
        if self._id_token in {"", None}:
            return True
        raw_token_data = self._id_token.split(".")[1]
        # In some cases padding get lost, adding it to avoid issues with base64 decode
        raw_token_data += "=" * ((4 - len(raw_token_data) % 4) % 4)
        token_data = self._load_json(base64.b64decode(raw_token_data))
        return bool(time.time() > token_data["exp"])

    def _get_httpsession(self) -> None:
        """Set http session."""
        if self._session is None:
            self._session = aiohttp.ClientSession(
                requote_redirect_url=False,
            )

    def _get_customer_http_headers(
        self, webuser_id: str, customer_id: str
    ) -> dict[str, str]:
        """Prepare http headers for customer url queries."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.access_token,
            "NO_PARTENAIRE_DEMANDEUR": webuser_id,
            "NO_PARTENAIRE_TITULAIRE": customer_id,
            "DATE_DERNIERE_VISITE": datetime.now().strftime(
                "%Y-%m-%dT%H:%M:%S.000+0000"
            ),
            "GUID_SESSION": self.guid,
        }
        return headers

    async def close_session(self) -> None:
        """Close current session."""
        if self._session is not None:
            await self._session.close()

    async def login(self) -> bool:
        """Log in HydroQuebec website.

        Hydroquebec is using ForgeRock solution for authentication.
        """
        self._logger.info("Login using %s", self.username)
        # Reset cache
        self.reset()

        # Get http session
        self._get_httpsession()

        # Get the callback template
        headers = {
            "Content-Type": "application/json",
            "X-NoSession": "true",
            "X-Password": "anonymous",
            "X-Requested-With": "XMLHttpRequest",
            "X-Username": "anonymous",
        }
        res = await self.http_request(AUTH_URL, "post", headers=headers)
        data = await res.json()

        # Check if we are already logged in
        if "tokenId" not in data:
            # Fill the callback template
            data["callbacks"][0]["input"][0]["value"] = self.username
            data["callbacks"][1]["input"][0]["value"] = self.password

            data_str = json_dumps(data)

            try:
                res = await self.http_request(
                    AUTH_URL, "post", data=data_str, headers=headers
                )
            except HydroQcHTTPError:
                self._logger.critical("Unable to connect. Check your credentials")
                return False
            json_res = await res.json()

            if "tokenId" not in json_res:
                self._logger.error(
                    "Unable to authenticate."
                    "You can retry and/or check your credentials."
                )
                return False

        # Get oauth2 token
        await self._get_oauth2_token()

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.access_token,
        }
        await self.http_request(LOGIN_URL_6, "get", headers=headers)
        self._logger.info("Login completed using %s", self.username)
        return True

    async def _get_oauth2_token(self, refresh: bool = False) -> bool:
        """Retrieve a oauth2 token.

        .. todo::
            Explain where 'id_token token' response type comes from
        """
        # Find settings for the authorize
        res = await self.http_request(SECURITY_URL, "get")

        sec_config = await res.json()
        oauth2_config = sec_config["oauth2"][0]

        client_id = oauth2_config["clientId"]
        redirect_uri = oauth2_config["redirectUri"]
        scope = oauth2_config["scope"]
        # Generate some random strings
        state = "".join(
            random.choice(string.digits + string.ascii_letters) for i in range(40)
        )
        nonce = state
        # TODO find where this setting comes from
        response_type = "id_token token"

        # Get bearer token
        params = {
            "response_type": response_type,
            "client_id": client_id,
            "state": state,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "nonce": nonce,
            "locale": "en",
        }
        if refresh:
            params["grant_type"] = "refresh_token"
            params["refresh_token"] = self.access_token
            params["redirect_uri"] = SESSION_REFRESH_URL

        res = await self.http_request(AUTHORIZE_URL, "get", params=params, status=302)
        # Go to Callback URL
        callback_url = res.headers["Location"]
        await self.http_request(callback_url, "get")

        if not refresh:
            raw_callback_params = callback_url.split("/callback#", 1)[-1].split("&")
        else:
            raw_callback_params = callback_url.split("/silent-refresh#", 1)[-1].split(
                "&"
            )
        callback_params = dict([p.split("=", 1) for p in raw_callback_params])

        # Check if we have the access token
        if "access_token" not in callback_params or not callback_params["access_token"]:
            self._logger.critical("Access token not found")
            raise HydroQcHTTPError("Access token not found")

        self._id_token = callback_params["id_token"]
        self.access_token = callback_params["access_token"]
        return True

    @CCached(ttl=600)
    async def refresh_session(self) -> bool:
        """Refresh current session."""
        return await self._get_oauth2_token(True)

    @property
    def selected_customer(self) -> str:
        """Return the current selected customer."""
        return self._selected_customer

    @property
    def selected_contract(self) -> str:
        """Return the current selected contract."""
        return self._selected_contract

    async def _select_contract(
        self, webuser_id: str, customer_id: str, contract_id: str, force: bool = False
    ) -> None:
        """Select a customer on the Home page.

        Equivalent to click on the customer box on the Home page.
        """
        # Do nothing if self._selected_contract is already the good one
        if self._selected_contract == contract_id and not force:
            return

        self._logger.info("Selecting contract %s", contract_id)
        if force and "cl-ec-spring.hydroquebec.com" in self.cookies:
            del self.cookies["cl-ec-spring.hydroquebec.com"]

        headers = self._get_customer_http_headers(webuser_id, customer_id)
        # await self.http_request(INFOBASE_URL, "get", headers=headers)

        params = {"mode": "web"}
        await self.http_request(SESSION_URL, "get", params=params, headers=headers)

        # load overview page
        # await self.http_request(CONTRACT_URL_3, "get", headers=headers)
        # load consumption profile page
        params = {"noContrat": contract_id}
        await self.http_request(PORTRAIT_URL, "get", params=params, headers=headers)

        self._selected_contract = contract_id
        self._selected_customer = customer_id
        self._logger.info("Contract %s selected", contract_id)

    @CCached(ttl=21600)
    async def get_user_info(self) -> list[ComptesTyping]:
        """Fetch user ids and customer ids.

        .. todo::
            Handle json load error
        """
        self._logger.info("Fetching webuser info")
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.access_token,
        }
        res = await self.http_request(RELATION_URL, "get", headers=headers)
        # TODO http errors
        data: list[ComptesTyping] = await res.json()
        return data

    @CCached(ttl=21600)
    async def get_customer_info(
        self, webuser_id: str, customer_id: str
    ) -> InfoCompteTyping:
        """Fetch customer data."""
        self._logger.info("Fetching customer info: c-%s", customer_id)
        headers = self._get_customer_http_headers(webuser_id, customer_id)
        params = {"withCredentials": "true"}
        api_call_response = await self.http_request(
            CUSTOMER_INFO_URL,
            "get",
            headers=headers,
            params=params,
        )
        data: InfoCompteTyping = await api_call_response.json()
        return data

    @CCached(ttl=21600)
    async def get_periods_info(
        self, webuser_id: str, customer_id: str, contract_id: str
    ) -> list[PeriodDataTyping]:
        """Fetch all periods info."""
        await self._select_contract(webuser_id, customer_id, contract_id)
        headers = self._get_customer_http_headers(webuser_id, customer_id)
        res = await self.http_request(PERIOD_DATA_URL, "get", headers=headers)
        data = json.loads(await res.text())

        periods: list[PeriodDataTyping] = [
            p for p in data["results"] if p["numeroContrat"] == contract_id
        ]
        if not periods:
            raise HydroQcError(f"No period found for contract {contract_id}")
        return periods

    @CCached(ttl=21600)
    async def get_account_info(
        self, webuser_id: str, customer_id: str, account_id: str
    ) -> listeComptesContratsTyping:
        """Fetch account data."""
        self._logger.info("Fetching account info: c-%s - a-%s", customer_id, account_id)
        data = await self.get_customer_info(webuser_id, customer_id)
        accounts = {
            a["noCompteContrat"]: a
            for a in data["infoCockpitPourPartenaireModel"]["listeComptesContrats"]
        }
        if account_id not in accounts:
            raise HydroQcError("Account not found")
        return accounts[account_id]

    @CCached(ttl=21600)
    async def get_contract_info(
        self, webuser_id: str, customer_id: str, contract_id: str
    ) -> listeContratModelTyping:
        """Fetch contract data."""
        self._logger.info(
            "Fetching contract info: c-%s - a-%s - c-%s",
            webuser_id,
            customer_id,
            contract_id,
        )
        data = await self.get_customer_info(webuser_id, customer_id)
        contracts = {c["noContrat"]: c for c in data["listeContratModel"]}
        if contract_id not in contracts:
            raise HydroQcError("Contract not found")
        return contracts[contract_id]

    @CCached(ttl=3600)
    async def get_winter_credit(
        self, webuser_id: str, customer_id: str, contract_id: str
    ) -> WinterCreditDataTyping:
        """Return information about the winter credit.

        :return: raw JSON from hydro QC API
        """
        self._logger.info(
            "Fetching winter credits: c-%s c-%s", customer_id, contract_id
        )
        headers = self._get_customer_http_headers(webuser_id, customer_id)
        params = {"noContrat": contract_id}
        api_call_response = await self.http_request(
            GET_WINTER_CREDIT_API_URL,
            "get",
            headers=headers,
            params=params,
        )
        data: WinterCreditDataTyping = await api_call_response.json()
        return data

    async def get_today_hourly_consumption(
        self, webuser_id: str, customer_id: str, contract_id: str
    ) -> ConsoHourlyTyping:
        """Return latest consumption info (about 2h delay it seems).

        :return: raw JSON from hydro QC API for current day (not officially supported, data delayed)
        """
        today = datetime.today().astimezone(EST_TIMEZONE)
        today_str = today.strftime("%Y-%m-%d")
        yesterday_str = (today - timedelta(days=1)).strftime("%Y-%m-%d")
        # We need to call a valid date first as theoretically today is invalid
        # and the api will not respond if called directly
        await self.get_hourly_consumption(
            webuser_id, customer_id, contract_id, yesterday_str
        )
        res: ConsoHourlyTyping = await self.get_hourly_consumption(
            webuser_id, customer_id, contract_id, today_str
        )
        return res

    @CCached(ttl=3600)
    async def get_hourly_consumption(
        self, webuser_id: str, customer_id: str, contract_id: str, date_wanted: str
    ) -> ConsoHourlyTyping:
        """Return hourly consumption for a specific day.

        .. todo::
            Use decorator for self._select_contract

        :param: date: YYYY-MM-DD string to pass to API

        :return: raw JSON from hydro QC API
        """
        self._logger.info(
            "Fetching hourly consumption: c-%s c-%s", customer_id, contract_id
        )
        # TODO use decorator
        await self._select_contract(webuser_id, customer_id, contract_id)
        params = {"date": date_wanted}
        api_call_response = await self.http_request(
            HOURLY_CONSUMPTION_API_URL, "get", params=params
        )
        # We can not use res.json() because the response header are not application/json
        data: ConsoHourlyTyping = self._load_json(await api_call_response.text())
        return data

    @CCached(ttl=43200)
    async def get_daily_consumption(
        self,
        webuser_id: str,
        customer_id: str,
        contract_id: str,
        start_date: str,
        end_date: str,
    ) -> ConsoDailyTyping:
        """Return daily consumption for a specific day.

        .. todo::
            Use decorator for self._select_contract

        :param: start_date: YYYY-MM-DD string to pass to API
        :param: end_date: YYYY-MM-DD string to pass to API

        :return: raw JSON from hydro QC API
        """
        self._logger.info(
            "Fetching daily consumption: c-%s c-%s", customer_id, contract_id
        )
        # TODO use decorator
        await self._select_contract(webuser_id, customer_id, contract_id)
        params = {"dateDebut": start_date, "dateFin": end_date}
        api_call_response = await self.http_request(
            DAILY_CONSUMPTION_API_URL,
            "get",
            params=params,
        )
        # We can not use res.json() because the response header are not application/json
        data: ConsoDailyTyping = self._load_json(await api_call_response.text())
        return data

    @CCached(ttl=21600)
    async def get_monthly_consumption(
        self, webuser_id: str, customer_id: str, contract_id: str
    ) -> ConsoMonthlyTyping:
        """Fetch data of the current year.

        .. todo::
            Use decorator for self._select_contract

        API URL: https://cl-ec-spring.hydroquebec.com/portail/fr/group/clientele/
        portrait-de-consommation/resourceObtenirDonneesConsommationMensuelles
        """
        self._logger.info(
            "Fetching monthly consumption: c-%s c-%s", customer_id, contract_id
        )
        # TODO use decorator
        await self._select_contract(webuser_id, customer_id, contract_id)
        headers = {"Content-Type": "application/json"}
        api_call_response = await self.http_request(
            MONTHLY_DATA_URL, "get", headers=headers
        )
        # We can not use res.json() because the response header are not application/json
        data: ConsoMonthlyTyping = self._load_json(await api_call_response.text())
        return data

    @CCached(ttl=21600)
    async def get_annual_consumption(
        self, webuser_id: str, customer_id: str, contract_id: str
    ) -> ConsoAnnualTyping:
        """Fetch data of the current year.

        API URL: https://cl-ec-spring.hydroquebec.com/portail/fr/group/clientele/
        portrait-de-consommation/resourceObtenirDonneesConsommationAnnuelles
        """
        self._logger.info(
            "Fetching annual consumption: c-%s c-%s", customer_id, contract_id
        )
        await self._select_contract(webuser_id, customer_id, contract_id)
        headers = {"Content-Type": "application/json"}
        api_call_response = await self.http_request(
            ANNUAL_DATA_URL, "get", headers=headers
        )
        # We can not use res.json() because the response header are not application/json
        data: ConsoAnnualTyping = self._load_json(await api_call_response.text())
        return data
