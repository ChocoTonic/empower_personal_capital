import getpass
import logging
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv

from personalcapital import (
    PersonalCapital,
    RequireTwoFactorException,
    TwoFactorVerificationModeEnum,
)

load_dotenv()


def get_email():
    email = os.getenv("PEW_EMAIL")
    if not email:
        print(
            "Set PEW_EMAIL and PEW_PASSWORD environment variables "
            "to skip these prompts in future runs."
        )
        return input("Enter email:")
    return email


def get_password():
    password = os.getenv("PEW_PASSWORD")
    if not password:
        return getpass.getpass("Enter password:")
    return password


def main():
    email, password = get_email(), get_password()
    pc = PersonalCapital()
    try:
        pc.load_session("session.json")
    except FileNotFoundError:
        logging.info("No saved session found")
    except ValueError as error:
        logging.warning("Ignoring invalid saved session: %s", error)

    try:
        pc.login(email, password)
    except RequireTwoFactorException:
        pc.two_factor_challenge(TwoFactorVerificationModeEnum.SMS)
        pc.two_factor_authenticate(TwoFactorVerificationModeEnum.SMS, input("code: "))
        pc.authenticate_password(password)

    accounts_response = pc.fetch("/newaccount/getAccounts")

    now = datetime.now()
    date_format = "%Y-%m-%d"
    days = 90
    start_date = (now - (timedelta(days=days + 1))).strftime(date_format)
    end_date = (now - (timedelta(days=1))).strftime(date_format)
    transactions_response = pc.fetch(
        "/transaction/getUserTransactions",
        {
            "sort_cols": "transactionTime",
            "sort_rev": "true",
            "page": "0",
            "rows_per_page": "100",
            "startDate": start_date,
            "endDate": end_date,
            "component": "DATAGRID",
        },
    )
    pc.save_session("session.json")

    accounts = accounts_response.json()["spData"]
    print("Networth: {0}".format(accounts["networth"]))

    transactions = transactions_response.json()["spData"]
    print(
        "Number of transactions between {0} and {1}: {2}".format(
            transactions["startDate"],
            transactions["endDate"],
            len(transactions["transactions"]),
        )
    )


if __name__ == "__main__":
    main()
