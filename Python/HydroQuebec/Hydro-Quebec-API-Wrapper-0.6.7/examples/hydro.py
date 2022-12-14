#!/usr/bin/env python
import asyncio

from hydroqc.webuser import WebUser


webuser = WebUser("USERNAME", "PASSWORD", verify_ssl=False, log_level="ERROR", http_log_level="ERROR")
async def async_func():
    await webuser.login()
    await webuser.get_info()

    customer = webuser.customers[0]
    print(customer.customer_id)
    data = await customer.get_info()
    print(data)

    account = customer.accounts[0]
    print(account)
    print(account.account_id)
    print(account.balance)

    contract = webuser.customers[0].accounts[0].contracts[0]
    print(contract.contract_id)
    data = await contract.get_periods_info()
    print(data)

    # Can still access events but probably unnecessary
    await contract.winter_credit.refresh_data()
    data = contract.winter_credit.next_anchor
    print(data)
    data = contract.winter_credit.next_peak
    print(data)
    data = contract.winter_credit.next_peak.is_critical
    print(data)
    data = contract.winter_credit.cumulated_credit
    print(data)

    # Need to call refresh_data before accessing attributes
    await contract.winter_credit.refresh_data()
    wc = contract.winter_credit.__dict__
    for k in wc.keys():
        if not k.startswith('value_'):
            continue
        else:
            print(k + ' : ' + str(wc[k]))
    # Still accessible through the data property
    data = contract.winter_credit.raw_data
    print(data)
    data = await contract.get_hourly_consumption("2022-01-20")
    print(data)
    data = await contract.get_today_hourly_consumption()
    print(data)
    data = await contract.get_today_daily_consumption()
    print(data)
    data = await contract.get_monthly_consumption()
    print(data)
    data = await contract.get_annual_consumption()
    print(data)
    data = await contract.get_daily_consumption("2022-01-10", "2022-01-20")
    print(data)


loop = asyncio.get_event_loop()


# Fetch data
try:
    results = loop.run_until_complete(async_func())
except BaseException as exp:
    print(exp)
finally:
    close_fut = asyncio.wait([webuser.close_session()])
    loop.run_until_complete(close_fut)
    loop.close()
