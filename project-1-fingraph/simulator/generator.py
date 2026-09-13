"""
FinGraph - Synthetic Financial Transaction Generator

Generates realistic transaction data for testing the FinGraph
real-time fraud detection pipeline.
"""

import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

NUM_ACCOUNTS = 1000
NUM_TRANSACTIONS = 10000

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "generated"
OUTPUT_FILE = OUTPUT_DIR / "transactions.csv"

fake = Faker("en_IN")
random.seed(42)


# ---------------------------------------------------------
# Account Generation
# ---------------------------------------------------------

def generate_accounts(num_accounts: int) -> list[dict]:
    """Generate synthetic bank accounts."""

    accounts = []

    for i in range(num_accounts):
        account = {
            "account_id": f"ACC_{i + 1:05d}",
            "customer_name": fake.name(),
            "country": random.choice(["IN", "IN", "IN", "US", "GB", "SG"]),
            "ip_address": fake.ipv4(),
        }

        accounts.append(account)

    return accounts


# ---------------------------------------------------------
# Normal Transaction Generation
# ---------------------------------------------------------

def generate_normal_transaction(
    accounts: list[dict],
    timestamp: datetime,
) -> dict:
    """Generate one normal financial transaction."""

    sender = random.choice(accounts)
    receiver = random.choice(accounts)

    # Make sure an account does not send money to itself.
    while receiver["account_id"] == sender["account_id"]:
        receiver = random.choice(accounts)

    amount = round(random.uniform(100, 50000), 2)

    return {
        "transaction_id": f"TXN_{uuid.uuid4().hex[:12].upper()}",
        "timestamp": timestamp.isoformat(),
        "sender_account": sender["account_id"],
        "receiver_account": receiver["account_id"],
        "amount": amount,
        "sender_ip": sender["ip_address"],
        "receiver_ip": receiver["ip_address"],
        "transaction_type": "TRANSFER",
        "country": sender["country"],
        "is_fraud": False,
        "fraud_pattern": "",
    }


# ---------------------------------------------------------
# Fraud Ring Generation
# ---------------------------------------------------------

def generate_fraud_ring(
    accounts: list[dict],
    start_time: datetime,
    ring_size: int = 5,
) -> list[dict]:
    """
    Generate a circular money-laundering network.

    Example:

        A -> B -> C -> D -> E -> A
    """

    ring_accounts = random.sample(accounts, ring_size)

    transactions = []

    amount = random.choice(
        [
            8900,
            9200,
            9500,
            9900,
        ]
    )

    for i in range(ring_size):
        sender = ring_accounts[i]
        receiver = ring_accounts[(i + 1) % ring_size]

        transaction = {
            "transaction_id": f"FRAUD_{uuid.uuid4().hex[:12].upper()}",
            "timestamp": (
                start_time + timedelta(seconds=i * random.randint(10, 60))
            ).isoformat(),
            "sender_account": sender["account_id"],
            "receiver_account": receiver["account_id"],
            "amount": amount,
            "sender_ip": sender["ip_address"],
            "receiver_ip": receiver["ip_address"],
            "transaction_type": "TRANSFER",
            "country": sender["country"],
            "is_fraud": True,
            "fraud_pattern": "CIRCULAR_RING",
        }

        transactions.append(transaction)

    return transactions


# ---------------------------------------------------------
# Starburst Syndicate Generation
# ---------------------------------------------------------

def generate_starburst(
    accounts: list[dict],
    start_time: datetime,
    member_count: int = 10,
) -> list[dict]:
    """
    Generate a starburst fraud pattern.

    Many accounts transfer money into one central account.

        A ─┐
        B ─┤
        C ─┼──> CENTRAL
        D ─┤
        E ─┘
    """

    selected_accounts = random.sample(accounts, member_count + 1)

    central_account = selected_accounts[0]
    sending_accounts = selected_accounts[1:]

    transactions = []

    for i, sender in enumerate(sending_accounts):

        amount = random.choice(
            [
                8900,
                9200,
                9500,
                9900,
            ]
        )

        transaction = {
            "transaction_id": f"FRAUD_{uuid.uuid4().hex[:12].upper()}",
            "timestamp": (
                start_time + timedelta(seconds=i * random.randint(5, 45))
            ).isoformat(),
            "sender_account": sender["account_id"],
            "receiver_account": central_account["account_id"],
            "amount": amount,
            "sender_ip": sender["ip_address"],
            "receiver_ip": central_account["ip_address"],
            "transaction_type": "TRANSFER",
            "country": sender["country"],
            "is_fraud": True,
            "fraud_pattern": "STARBURST",
        }

        transactions.append(transaction)

    return transactions


# ---------------------------------------------------------
# Dataset Generation
# ---------------------------------------------------------

def generate_dataset() -> None:
    """Generate the complete FinGraph transaction dataset."""

    print("\nFinGraph Transaction Simulator")
    print("-" * 40)

    accounts = generate_accounts(NUM_ACCOUNTS)

    print(f"Accounts generated: {len(accounts)}")

    start_time = datetime.now() - timedelta(days=30)

    transactions = []

    # Generate normal transactions
    for _ in range(NUM_TRANSACTIONS):
        random_time = start_time + timedelta(
            seconds=random.randint(0, 30 * 24 * 60 * 60)
        )

        transaction = generate_normal_transaction(
            accounts,
            random_time,
        )

        transactions.append(transaction)

    print(f"Normal transactions generated: {len(transactions)}")

    # Inject circular fraud rings
    fraud_ring_count = 5

    for _ in range(fraud_ring_count):

        ring_start = start_time + timedelta(
            seconds=random.randint(0, 30 * 24 * 60 * 60)
        )

        ring = generate_fraud_ring(
            accounts,
            ring_start,
            ring_size=random.randint(4, 7),
        )

        transactions.extend(ring)

    # Inject starburst fraud networks
    starburst_count = 3

    for _ in range(starburst_count):

        starburst_start = start_time + timedelta(
            seconds=random.randint(0, 30 * 24 * 60 * 60)
        )

        starburst = generate_starburst(
            accounts,
            starburst_start,
            member_count=random.randint(8, 15),
        )

        transactions.extend(starburst)

    # Sort transactions chronologically
    transactions.sort(key=lambda x: x["timestamp"])

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Write CSV
    fieldnames = [
        "transaction_id",
        "timestamp",
        "sender_account",
        "receiver_account",
        "amount",
        "sender_ip",
        "receiver_ip",
        "transaction_type",
        "country",
        "is_fraud",
        "fraud_pattern",
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(transactions)

    fraud_transactions = sum(
        1 for transaction in transactions
        if transaction["is_fraud"]
    )

    print(f"Total transactions: {len(transactions)}")
    print(f"Fraud transactions injected: {fraud_transactions}")
    print(f"Fraud rings: {fraud_ring_count}")
    print(f"Starburst syndicates: {starburst_count}")

    print("\nDataset saved successfully:")
    print(OUTPUT_FILE)


# ---------------------------------------------------------
# Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":
    generate_dataset()