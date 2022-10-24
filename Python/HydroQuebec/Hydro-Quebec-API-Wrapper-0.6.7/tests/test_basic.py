"""Basics tests for hydroqc."""
import asyncio
import datetime
import os
import time
import typing

import pytest
from hydroqc.account import Account
from hydroqc.contract import Contract
from hydroqc.customer import Customer
from hydroqc.error import HydroQcError
from hydroqc.webuser import WebUser
from hydroqc.winter_credit.consts import EST_TIMEZONE
from hydroqc.winter_credit.handler import WinterCreditHandler

HYDROQC_USERNAME = os.environ["HYDROQC_USERNAME"]
HYDROQC_PASSWORD = os.environ["HYDROQC_PASSWORD"]
HYDROQC_RATE = os.environ["HYDROQC_RATE"]
HYDROQC_EPP_ENABLED = os.environ["HYDROQC_EPP_ENABLED"].lower() == "true"
HYDROQC_WC_ENABLED = os.environ["HYDROQC_WC_ENABLED"].lower() == "true"
HYDROQC_ACCOUNT_ID = int(os.environ.get("HYDROQC_ACCOUNT_ID", 0))

today = datetime.datetime.today().astimezone(EST_TIMEZONE).date()
today_str = today.strftime("%Y-%m-%d")
yesterday = today - datetime.timedelta(days=1)
yesterday_str = yesterday.strftime("%Y-%m-%d")
lastweekday = today - datetime.timedelta(days=7)
lastweekday_str = lastweekday.strftime("%Y-%m-%d")


async def is_young_contract(contract: Contract) -> bool:
    """Determine if the contract is young than 1 year."""
    contract_info = await contract.get_info()
    # Get contract start date
    contract_start_date = datetime.date.fromisoformat(contract_info["dateDebutContrat"])
    # Get one years ago plus few days
    one_year_ago = today - datetime.timedelta(days=367)
    # Get the youngest date between contract start date VS 1 years ago
    if contract_start_date > one_year_ago:
        return True
    return False


class TestBase:
    """Base test class."""

    @typing.no_type_check
    @pytest.fixture(scope="module")
    def event_loop(self):
        """Override asyncio event_loop to keep the loop running through the whole module."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
        yield loop
        loop.close()

    @pytest.mark.asyncio
    async def test_bad_credentials(self) -> None:
        """Test bad credentials management."""
        # Webuser
        webuser = WebUser("bad_username", "bad_password", verify_ssl=True)
        connected = await webuser.login()
        assert connected is False, "Login should not work"

    @pytest.fixture(scope="module")
    def webuser(self) -> WebUser:
        """Fixture to keep the webuser instance through all tests."""
        return WebUser(
            HYDROQC_USERNAME,
            HYDROQC_PASSWORD,
            verify_ssl=True,
            log_level="ERROR",
            http_log_level="ERROR",
        )

    @pytest.mark.asyncio
    async def teardown_ends(self, webuser: WebUser) -> None:
        """Run all needed steps to ends tests."""
        print("teardown")
        # Close session
        await webuser.close_session()

    @pytest.mark.asyncio
    async def test_good_credentials(self, webuser: WebUser) -> None:
        """Test credentials main."""
        assert webuser.session_expired is True, "The session should be expired"

        connected = await webuser.login()
        assert connected is True, "Login should work. Please check your credentials"
        await webuser.get_info()

    @pytest.mark.asyncio
    async def test_session(self, webuser: WebUser) -> None:
        """Test session attributes."""
        assert webuser.first_name != "", "No webuser's firstname found"
        assert webuser.last_name != "", "No webuser's lastname found"
        assert webuser.session_expired is False, "Session expired"
        assert repr(webuser).startswith("<Webuser - ")

        # Test caching
        start_time = time.time()
        await webuser.refresh_session()
        end_time = time.time()
        first_refresh = end_time - start_time

        start_time = time.time()
        await webuser.refresh_session()
        end_time = time.time()
        second_refresh = end_time - start_time
        # Check if second refresh is way quicker than first refresh
        assert first_refresh > second_refresh * 100

    @pytest.fixture(scope="module")
    def customer(self, webuser: WebUser) -> Customer | None:
        """Fixture to keep the customer instance through all tests."""
        if len(webuser.customers) <= HYDROQC_ACCOUNT_ID:
            return None
        return webuser.customers[HYDROQC_ACCOUNT_ID]

    @typing.no_type_check
    @pytest.mark.asyncio
    async def test_customer(self, webuser: WebUser, customer: Customer) -> None:
        """Test customer attributes."""
        assert len(webuser.customers) > 0, "No customer found"
        assert (
            webuser.get_customer(customer.customer_id) == customer
        ), "Can not retrieve the same customer with webuser.get_customer method"
        with pytest.raises(HydroQcError):
            webuser.get_customer("bad customer id")
        assert customer.names != "", "Bad customer name"
        assert repr(customer).startswith("<Customer - ")
        assert customer.customer_id is not None, "No customer id found"

    @pytest.fixture(scope="module")
    def account(self, customer: Customer) -> Account | None:
        """Fixture to keep the account instance through all tests."""
        if len(customer.accounts) <= 0:
            return None
        return customer.accounts[0]

    @pytest.mark.asyncio
    async def test_account(self, customer: Customer, account: Account) -> None:
        """Test account attributes."""
        assert len(customer.accounts) > 0, "No account found"
        assert account.account_id is not None, "No account id found"
        assert (
            customer.get_account(account.account_id) == account
        ), "Can not retrieve the same account with customer.get_account method"
        with pytest.raises(HydroQcError):
            customer.get_account("bad account id")
        assert isinstance(account.balance, float)
        assert repr(account).startswith("<Account - ")

    @pytest.fixture(scope="module")
    def contract(self, account: Account) -> Contract | None:
        """Fixture to keep the contract instance through all tests."""
        if len(account.contracts) <= 0:
            return None
        return account.contracts[0]

    @pytest.mark.asyncio
    async def test_contract(self, account: Account, contract: Contract) -> None:
        """Test contract attributes."""
        assert len(account.contracts) > 0, "No contract found"
        assert contract.contract_id is not None, "No contract id found"
        assert (
            account.get_contract(contract.contract_id) == contract
        ), "Can not retrieve the same contract with account.get_contract method"
        with pytest.raises(HydroQcError):
            account.get_contract("bad contract id")
        assert contract.account_id == account.account_id, "Bad account id in contract"
        assert repr(contract).startswith("<Contract - ")

    @pytest.mark.asyncio
    async def test_hourly_consumption(self, contract: Contract) -> None:
        """Test hourly consumption stats."""
        today_hourly_consumption = await contract.get_today_hourly_consumption()
        assert today_hourly_consumption.get("success") is True
        assert today_hourly_consumption.get("results", {}).get("dateJour") in (
            today_str,
            yesterday_str,
        )

    @pytest.mark.asyncio
    async def test_total_hourly_consumption(self, contract: Contract) -> None:
        """Test total hourly consumption stats."""
        hourly_consumption = await contract.get_hourly_consumption(yesterday_str)
        assert hourly_consumption.get("success") is True
        assert hourly_consumption.get("results", {}).get("dateJour") == yesterday_str

    @pytest.mark.asyncio
    async def test_daily_consumption(self, contract: Contract) -> None:
        """Test daily consumption stats."""
        daily_consumption = await contract.get_daily_consumption(
            lastweekday_str, yesterday_str
        )
        assert daily_consumption.get("success") is True
        assert len(daily_consumption.get("results", [])) == 7
        assert (
            daily_consumption["results"][-1]["courant"]["dateJourConso"]
            == lastweekday_str
        )

    @pytest.mark.asyncio
    async def test_total_daily_consumption(self, contract: Contract) -> None:
        """Test total hourly consumption stats."""
        today_daily_consumption = await contract.get_today_daily_consumption()
        assert today_daily_consumption.get("success") is True

        assert len(today_daily_consumption.get("results", [])) == 1
        assert (
            today_daily_consumption["results"][-1]["courant"]["dateJourConso"]
            == yesterday_str
        )

    @pytest.mark.skipif(
        "config.getoption('--new-contract')",
        reason="No history available on new contracts",
    )
    @pytest.mark.asyncio
    async def test_monthly_consumption(self, contract: Contract) -> None:
        """Test monthly consumption stats."""
        monthly_consumption = await contract.get_monthly_consumption()
        assert monthly_consumption.get("success") is True
        if await is_young_contract(contract):
            assert len(monthly_consumption.get("results", [])) > 0
            assert len(monthly_consumption.get("results", [])) < 12
        else:
            assert len(monthly_consumption.get("results", [])) == 12

    @pytest.mark.skipif(
        "config.getoption('--new-contract')",
        reason="No history available on new contracts",
    )
    @pytest.mark.asyncio
    async def test_annual_consumption(self, contract: Contract) -> None:
        """Test annual consumption stats."""
        annual_consumption = await contract.get_annual_consumption()
        assert annual_consumption.get("success") is True

        if await is_young_contract(contract):
            # If the contract is too young (less than 1 year) we don't have any data
            assert len(annual_consumption.get("results", [])) == 0
        else:
            assert len(annual_consumption.get("results", [])) == 1
            assert (
                annual_consumption["results"][0]
                .get("courant", {})
                .get("dateFinAnnee", "")
                .startswith(str(today.year))
            )

    @pytest.mark.asyncio
    async def test_latest_period(self, contract: Contract) -> None:
        """Test latest_period."""
        assert (
            contract.cp_current_day is None
        ), "Method get_latest_period_info is already called but it should not"
        assert (
            not contract.get_latest_period_info()
        ), "Method get_latest_period_info is already called but it should not"

    @typing.no_type_check
    @pytest.mark.asyncio
    async def test_contract_info(self, contract: Contract) -> None:
        """Test contract information validity."""
        await contract.get_periods_info()
        assert (
            contract._hydro_client.selected_customer == contract.customer_id
        ), "Bad selected customer"
        assert (
            contract._hydro_client.selected_contract == contract.contract_id
        ), "Bad selected contract"

        assert len(contract.get_latest_period_info()) > 0, "No period info found"
        assert contract.cp_current_day >= 0

        assert contract.cp_duration >= 0
        assert contract.cp_current_bill >= 0
        assert contract.cp_projected_bill >= 0
        assert contract.cp_daily_bill_mean >= 0
        assert contract.cp_daily_consumption_mean >= 0
        assert contract.cp_total_consumption >= 0
        assert contract.cp_projected_total_consumption >= 0
        assert contract.cp_lower_price_consumption >= 0
        assert contract.cp_higher_price_consumption >= 0
        assert contract.cp_average_temperature >= -30
        assert contract.cp_average_temperature <= 50
        assert contract.cp_kwh_cost_mean >= 0
        assert (
            contract.cp_rate == HYDROQC_RATE
        ), "Bad rate status, please check the value of HYDROQC_RATE"
        assert (
            contract.cp_epp_enabled == HYDROQC_EPP_ENABLED
        ), "Bad EPP status, please check the value of HYDROQC_EPP_ENABLED"

    @pytest.fixture(scope="module")
    def winter_credit(self, contract: Contract) -> WinterCreditHandler:
        """Fixture to keep the winter credit instance through all tests."""
        return contract.winter_credit

    @pytest.mark.asyncio
    async def test_winter_credit(
        self,
        webuser: WebUser,
        account: Account,
        contract: Contract,
        winter_credit: WinterCreditHandler,
    ) -> None:
        """Test winter credit information validity."""
        assert winter_credit.webuser_id == webuser.webuser_id
        assert winter_credit.customer_id == account.customer_id
        assert winter_credit.contract_id == contract.contract_id

        assert (
            len(winter_credit.raw_data) == 0
        ), "Raw data should be empty, data not fetched yet"

        await winter_credit.refresh_data()
        assert (
            winter_credit.is_enabled == HYDROQC_WC_ENABLED
        ), "Bad winter credit status, please check the value of HYDROQC_WC_ENABLED"
        assert len(winter_credit.raw_data) > 0
        if winter_credit.is_enabled:
            assert winter_credit.winter_start_date.month == 12
            assert winter_credit.winter_start_date.day == 1
            assert winter_credit.winter_end_date.month == 3
            assert winter_credit.winter_end_date.day == 31
            assert len(winter_credit.peaks) > 0
            assert len(winter_credit.sonic) > 0
            assert len(winter_credit.critical_peaks) >= 0
            assert len(winter_credit.critical_peaks) <= len(winter_credit.peaks)
            assert winter_credit.cumulated_credit >= 0
            assert winter_credit.current_peak in [None] + winter_credit.peaks
            assert winter_credit.current_peak_is_critical in {None, True, False}
            assert winter_credit.current_state in {
                "critical_anchor",
                "anchor",
                "critical_peak",
                "peak",
                "normal",
            }
            assert isinstance(winter_credit.preheat_in_progress, bool)
            assert isinstance(winter_credit.is_any_critical_peak_coming, bool)
            assert isinstance(winter_credit.next_peak_is_critical, bool)
            assert (
                winter_credit.next_critical_peak
                in [None] + winter_credit.critical_peaks
            )
            assert winter_credit.today_morning_peak in [None] + winter_credit.peaks
            assert winter_credit.today_evening_peak in [None] + winter_credit.peaks
            assert winter_credit.tomorrow_morning_peak in [None] + winter_credit.peaks
            assert winter_credit.tomorrow_evening_peak in [None] + winter_credit.peaks
            assert winter_credit.yesterday_morning_peak in [None] + winter_credit.peaks
            assert winter_credit.yesterday_evening_peak in [None] + winter_credit.peaks
            assert winter_credit.next_anchor in [None] + [
                p.anchor for p in winter_credit.peaks
            ]
        else:
            assert winter_credit.winter_start_date is None
            assert winter_credit.winter_end_date is None
            assert winter_credit.peaks is None
            assert winter_credit.sonic is None
            assert winter_credit.critical_peaks is None
            assert winter_credit.cumulated_credit is None
            assert winter_credit.current_peak is None
            assert winter_credit.current_peak_is_critical is None
            assert winter_credit.current_state is None
            assert winter_credit.preheat_in_progress is None
            assert winter_credit.is_any_critical_peak_coming is None
            assert winter_credit.next_peak_is_critical is None
            assert winter_credit.next_critical_peak is None
            assert winter_credit.today_morning_peak is None
            assert winter_credit.today_evening_peak is None
            assert winter_credit.tomorrow_morning_peak is None
            assert winter_credit.tomorrow_evening_peak is None
            assert winter_credit.yesterday_morning_peak is None
            assert winter_credit.yesterday_evening_peak is None
            assert winter_credit.next_anchor is None

        # assert winter_credit.next_anchor
        # Close session
        # await self.webuser.close_session()
