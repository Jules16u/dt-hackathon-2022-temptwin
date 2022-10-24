# HydroQC - Hydro Quebec API wrapper


[![coverage report](https://gitlab.com/hydroqc/hydroqc/badges/main/coverage.svg)](https://gitlab.com/hydroqc/hydroqc/-/commits/main)
[![pipeline status](https://gitlab.com/hydroqc/hydroqc/badges/main/pipeline.svg)](https://gitlab.com/hydroqc/hydroqc/-/commits/main)
[![Latest Release](https://gitlab.com/hydroqc/hydroqc/-/badges/release.svg)](https://gitlab.com/hydroqc/hydroqc/-/releases)


**This is a library to use if you want to build your own solution. If you want a user-friendly implementation for your home automation system please use [hydroqc2mqtt](https://gitlab.com/hydroqc/hydroqc2mqtt) which provide a MQTT publisher, docker image and HASS addon.**

This is a package to access some functionalities of Hydro Quebec API that are not documented.

We started a discord server for the project where you can come to discuss and find help with the project on our [#development](https://discord.gg/NWnfdfRZ7T) channel

## Account Scenarios

Each account and contracts are different and we do our best to integrate all available options. Currently the account combinations listed below are supported and tested automaticaly by our CI/CD pipeline. If your account scenario is not currently tested and listed as **Needed** feel free to reach out to us on our discord [#development](https://discord.gg/NWnfdfRZ7T) channel if you want to volunter for testing. We provide a way to setup CI/CD tests in your own account in a way that keep your account info private to you (more details [here](https://gitlab.com/hydroqc/hydroqc-test-template)). Keep in mind that this process is a bit involved technicaly so it is best if you have some working knowledge with Gitlab.

### Rate D (most residential accounts should fall under this rate)

| Winter Credit | EPP* | Tester | Test result | Last run | Multi Contract | Multi Customer | Comment |
| - | - | - | - | - | - | - | - |
| No | No | @weimdall | ![Test Result](https://gitlab.com/api/v4/projects/hydroqc%2Fhydroqc/jobs/artifacts/main/raw/39038345-badge.svg?job=private_tests_done) | ![Timestamp](https://gitlab.com/api/v4/projects/hydroqc%2Fhydroqc/jobs/artifacts/main/raw/39038345-job-end-date.svg?job=private_tests_done) | Yes | | |
| No | Yes | @devzwf | ![Test Result](https://gitlab.com/api/v4/projects/hydroqc%2Fhydroqc/jobs/artifacts/main/raw/39310934-badge.svg?job=private_tests_done) | ![Timestamp](https://gitlab.com/api/v4/projects/hydroqc%2Fhydroqc/jobs/artifacts/main/raw/39310934-job-end-date.svg?job=private_tests_done) | | | |
| Yes | Yes | @zepiaf |  ![Test Result](https://gitlab.com/api/v4/projects/hydroqc%2Fhydroqc/jobs/artifacts/main/raw/35331048-badge.svg?job=private_tests_done) | ![Timestamp](https://gitlab.com/api/v4/projects/hydroqc%2Fhydroqc/jobs/artifacts/main/raw/35331048-job-end-date.svg?job=private_tests_done) | | | |
| Yes | No | @titilambert |![Test Result](https://gitlab.com/api/v4/projects/hydroqc%2Fhydroqc/jobs/artifacts/main/raw/35085986-badge.svg?job=private_tests_done)  | ![Timestamp](https://gitlab.com/api/v4/projects/hydroqc%2Fhydroqc/jobs/artifacts/main/raw/35085986-job-end-date.svg?job=private_tests_done) | | Yes | |
| Yes | No | @mdallaire1 | ![Test Result](https://gitlab.com/api/v4/projects/hydroqc%2Fhydroqc/jobs/artifacts/main/raw/39503160-badge.svg?job=private_tests_done) | ![Timestamp](https://gitlab.com/api/v4/projects/hydroqc%2Fhydroqc/jobs/artifacts/main/raw/39503160-job-end-date.svg?job=private_tests_done) | No | No | |

*EPP = Equal Payment Plan
#### Flex D
We don't have anyone to test with. Please reach out to us if you have this plan and want to help!

### Other plans (commercial, etc)
We don't have anyone to test with. Please reach out to us if you have this plan and want to help!

## Documentation

### Code documentation

[https://hydroqc.readthedocs.io/](https://hydroqc.readthedocs.io/)

### Architecture / concepts

If you need more information about the usage and current integrations of the library please see our website [https://hydroqc.ca](https://hydroqc.ca)

## Goal

Make it easy to fetch and manipulate data from Hydro-Quebec, especially the winter credit periods

## Example folder

An example script that extracts the data available from Hydro-Quebec is available in the examples folder.

### Basic setup

This uses python 3 (tested with 3.8)

1. Clone the repo

   ```bash
   git clone https://gitlab.com/hydroqc/hydroqc.git
   ```

2. Create a virtual-env

   ```bash
   python -m venv env
   . env/bin/activate
   pip install --editable .
   ```

3. Enter your hydro account credentials in the examples/hydro.py file (line 6)

4. Run

   ```bash
   examples/hydro.py
   ```

## Available features

- Services.getWinterCredit() to get raw winter credit data
- Services.getTodayHourlyConsumption() to get raw hourly consumption for current day
- Services.getHourlyConsumption(date = 'YYYY-MM-DD') to get hourly consumption for specific day
- Services.getDailyConsumption(start_date = 'YYYY-MM-DD',end_date = 'YYYY-MM-DD') to get a range of daily consumption
- WinterCredit.getFutureEvents() to get a list of JSON object with future peak events

## NOTES

As per issue [https://github.com/zepiaf/hydroqc/issues/11](https://github.com/zepiaf/hydroqc/issues/11) the full certificate chain for "session.hydroquebec.com" is not provided completely by Hydro-Quebec, resulting in a failed SSL verification. We are providing it in the "hydro-chain.pem" file and the code is using this file to validate the certificate in queries to "session.hydroquebec.com".

We would very much like for this to be either fixed by Hydro-Quebec or for this chain to be dynamicaly built at run time. Any help to make this happen would be greatly appreciated.

## TODO

[https://gitlab.com/groups/hydroqc/-/issues](https://gitlab.com/groups/hydroqc/-/issues)

## Targeted architecture (might change in the future)

```mermaid
classDiagram
    WebUser <-- Customer
    WebUser <-- HydroClient

    Customer <-- Account

    Account <-- Contract

    Contract <-- HydroClient
    Contract <-- Period
    Contract <-- Event
    Contract <-- WinterCreditHelper

    WinterCreditHelper <-- HydroClient


    HydroClient <-- Authenticator

    class HydroClient{

    }
    class WinterCreditHelper{
    }

    class WebUser{
        -HydroClient _hydro_client
        +List~Customer~ customers
        +get_contracts()
    }

    class Customer{
        -HydroClient _hydro_client
        +List~Account~ accounts
    }

    class Account{
        -HydroClient _hydro_client
        +List~Contract~ contracts
    }

    class Config{
        -string config_file_path
    }

    class Contract{
        -HydroClient _hydro_client
        -int customer_id
        -int webuser_id
        +string subscription_type
        +float balance
        +list~Period~ periods
        +list~Event~ events
        +get_winter_credit()
        +fetch_periods()
        +fetch_summary()
    }

    class Period{
    }

    class Event{
    }
```
