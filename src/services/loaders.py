import csv
import os

from models.customer import Customer
from models.product import Product
from models.transaction import Transaction
from models.promotion import Promotion
from models.shippingZone import ShippingZone


def read_file(base: str, path: str, file: str) -> list:
    file_path = os.path.join(base, path, file)
    try:
        with open(file_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            return list(reader)
    except (IndexError, ValueError):
        pass
    return []


# CUSTOMERS


def load_customers(base: str, path: str, file: str) -> dict:
    lines = read_file(base, path, file)
    customers = {}
    for row in lines:
        customers[row[0]] = Customer(row[0], row[1], row[2], row[3], row[4])
    return customers


# PRODUCTS


def load_products(base: str, path: str, file: str) -> dict:
    lines = read_file(base, path, file)
    products = {}
    for i in range(1, len(lines)):  # skip header
        try:
            product = lines[i]
            products[product[0]] = Product(product)
        except (IndexError, ValueError):
            # Skip silencieux
            pass
    return products


# PROMOTIONS


def load_promotions(base: str, path: str, file: str) -> dict:
    lines = read_file(base, path, file)
    promotions = {}
    for i in range(1, len(lines)):
        promo = lines[i]
        promotions[promo[0]] = Promotion(promo)
    return promotions


# SHIPPING ZONES


def load_shipping_zones(base: str, path: str, file: str) -> dict:
    lines = read_file(base, path, file)
    shipping_zones = {}
    for i in range(1, len(lines)):
        shipping_zone = lines[i]
        shipping_zones[shipping_zone[0]] = ShippingZone(
            shipping_zone[0], shipping_zone[1], shipping_zone[2]
        )
    return shipping_zones


# TRANSACTIONS


def load_transactions(base: str, path: str, file: str) -> dict:
    lines = read_file(base, path, file)
    transactions = []
    for i in range(1, len(lines)):
        transaction = lines[i]
        try:
            transactions.append(Transaction(transaction))
        except (IndexError, ValueError):
            continue
    return transactions
