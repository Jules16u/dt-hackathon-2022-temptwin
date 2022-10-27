#!/usr/bin/env python
import asyncio
from contextlib import nullcontext
import socket
import threading
import websockets
from hydroqc.webuser import WebUser
from datetime import datetime

USERNAME = "david.menard0@gmail.com"
PASSWORD = "tx07sx94!DHydro"

class HydroServer:

    customer = None
    account = None
    #contract = None

    webuser = None

    def __init__(self):
        print("Init HydroServer")

    async def Init(self):
        self.webuser = WebUser(USERNAME, PASSWORD, verify_ssl=False, log_level="ERROR", http_log_level="ERROR")
        await self.webuser.login()
        await self.webuser.get_info()
        self.customer = self.webuser.customers[0]
        print("User ID: " + self.customer.customer_id)
        data = await self.customer.get_info()
        print(data)

        self.account = self.customer.accounts[0]
        print("Account: " + str(self.account))
        print("Account ID: " + self.account.account_id)
        print("Account Balance: " + str(self.account.balance))

        self.contract = self.account.contracts[0]

    # Every time the client pings, we send the hydro info back
    # This is where you would parse the message from the Unity Client, and return the right info
    async def SocketEcho(self, websocket):
        async for message in websocket:

            match message:
                case "AccountID":
                    await websocket.send(str(self.account.account_id))
                case "Daily_Consumption":
                    await self.contract.winter_credit.refresh_data()
                    data = await self.contract.get_today_hourly_consumption()
                    conso_horaire = data['results']['listeDonneesConsoEnergieHoraire']
                    for i in range(23,0,-1): # 24hour in a day. we get the latest non-0 value
                        if conso_horaire[i]["consoReg"] > 0.01:
                            print(conso_horaire[i]["consoReg"])
                            await websocket.send(str(conso_horaire[i]["consoReg"])) 
                            break
                case _:
                    #self.contract = self.webuser.customers[0].accounts[0].contracts[0]
                    await self.contract.winter_credit.refresh_data()
                    data = await self.contract.get_daily_consumption("2022-01-10", "2022-01-20")
                    await websocket.send(str(data))

    async def RunSocket(self):
        async with websockets.serve(self.SocketEcho, "localhost", 8080):
            await asyncio.Future()  # run forever

loop = asyncio.get_event_loop()
try:
    print(datetime.today().strftime('%Y-%m-%d'))
    hs = HydroServer()
    loop.run_until_complete(hs.Init())
    loop.run_until_complete(hs.RunSocket())
    #loop.run_until_complete(asyncio.sleep(1))

except BaseException as exp:
    print(exp)
finally:
    close_fut = asyncio.wait([hs.webuser.close_session()])
    loop.run_until_complete(close_fut)
    loop.stop()
    loop.close()
