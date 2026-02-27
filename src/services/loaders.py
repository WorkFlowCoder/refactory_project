import csv
import os

from models.customer import Customer
from models.product import Product
from models.transaction import Transaction
from models.promotion import Promotion
from models.shippingZone import ShippingZone


# Lecture générique d'un fichier CSV
def read_file(base: str, path: str, file: str) -> list:
    file_path = os.path.join(base, path, file)
    try:
        with open(file_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            return list(reader)
    except (IndexError, ValueError):
        pass
    return []


# Chargement des clients
def load_customers(base: str, path: str, file: str) -> dict:
    lines = read_file(base, path, file)
    customers = {}
    for row in lines:
        # Création d'un objet Customer pour chaque ligne
        customers[row[0]] = Customer(row[0], row[1], row[2], row[3], row[4])
    return customers


# Chargement des produits
def load_products(base: str, path: str, file: str) -> dict:
    lines = read_file(base, path, file)
    products = {}
    for i in range(1, len(lines)):  # skip header
        try:
            product = lines[i]
            products[product[0]] = Product(product)
        except (IndexError, ValueError):
            pass
    return products


# Chargement des promotions
def load_promotions(base: str, path: str, file: str) -> dict:
    lines = read_file(base, path, file)
    promotions = {}
    for i in range(1, len(lines)):  # skip header
        promo = lines[i]
        promotions[promo[0]] = Promotion(promo)
    return promotions


# Chargement des zones de livraison
def load_shipping_zones(base: str, path: str, file: str) -> dict:
    lines = read_file(base, path, file)
    shipping_zones = {}
    for i in range(1, len(lines)):  # skip header
        shipping_zone = lines[i]
        shipping_zones[shipping_zone[0]] = ShippingZone(
            shipping_zone[0], shipping_zone[1], shipping_zone[2]
        )
    return shipping_zones


# Chargement des transactions
def load_transactions(base: str, path: str, file: str) -> dict:
    lines = read_file(base, path, file)
    transactions = []
    for i in range(1, len(lines)):  # skip header
        transaction = lines[i]
        try:
            transactions.append(Transaction(transaction))
        except (IndexError, ValueError):
            continue
    return transactions
