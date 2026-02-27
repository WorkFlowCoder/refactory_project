from datetime import datetime
from typing import Any

# Constantes globales pour le calcul des remises, taxes et frais

TAX = 0.2  # taux de TVA par défaut
SHIPPING_LIMIT = 50  # seuil de livraison gratuite
SHIP = 5.0  # frais de port de base
LOYALTY_RATIO = 0.01  # ratio de conversion pour points de fidélité
HANDLING_FREE = 2.5  # frais de gestion pour grosses commandes
MAX_DISCOUNT = 200  # remise maximale totale possible


# Calcul des points de fidélité
def calcul_fidelity_points(transactions: dict) -> list:
    loyalty_points = {}
    for transaction in transactions:
        customer_id = transaction.get_customer_id()
        if customer_id not in loyalty_points:
            loyalty_points[customer_id] = 0
        # Points basés sur montant total de la transaction * ratio
        tmp = transaction.get_qty() * transaction.get_unit_price()
        loyalty_points[customer_id] += tmp * LOYALTY_RATIO
    return loyalty_points


# Calcul du total d'une ligne avec promotion
def calcul_with_promo(transaction: Any, product: Any, promos: dict) -> list:
    discount_rate = 0
    fixed_discount = 0
    promo_code = transaction.get_promo_code()
    base_price = product.get_price()

    # Vérifie si promo existante et active
    if promo_code and promo_code in promos:
        promo = promos[promo_code]
        if promo.get_active():
            if promo.get_type() == "PERCENTAGE":
                discount_rate = float(promo.get_value()) / 100
            elif promo.get_type() == "FIXED":
                fixed_discount = float(promo.get_value())

    # Calcul du total de la ligne après application des remises
    line_total = (
        transaction.get_qty() * base_price * (1 - discount_rate)
        - fixed_discount * transaction.get_qty()
    )
    return line_total


# Remise globale en fonction du montant et du type de client
def get_remise(
    subtotal: int, level: str, totals_by_customer: dict, customer_id: int
) -> float:
    disc = 0.0
    # Remise progressive selon le montant (duplication volontaire)
    if subtotal > 50:
        disc = subtotal * 0.05
    if subtotal > 100:
        disc = subtotal * 0.10  # écrase la précédente
    if subtotal > 500:
        disc = subtotal * 0.15
    if subtotal > 1000 and level == "PREMIUM":
        disc = subtotal * 0.20

    # Bonus weekend si première commande
    first_order_date = (
        totals_by_customer[customer_id]["items"][0].get_date()
        if totals_by_customer[customer_id]["items"]
        else ""
    )
    day_of_week = 0
    if first_order_date:
        try:
            dt = datetime.strptime(first_order_date, "%Y-%m-%d")
            day_of_week = dt.weekday()
        except (IndexError, ValueError):
            pass

    # Week-end : 5% bonus sur la remise
    if day_of_week == 5 or day_of_week == 6:
        disc = disc * 1.05
    return disc


# Calcul des remises totales (volume + fidélité)
def calcul_discount(loyalty_pts: list, customer_id: int, disc: float) -> Any:
    loyalty_discount = 0.0
    pts = loyalty_pts.get(customer_id, 0)

    # Remise fidélité progressive
    if pts > 100:
        loyalty_discount = min(pts * 0.1, 50.0)
    if pts > 500:
        loyalty_discount = min(pts * 0.15, 100.0)  # écrase précédent

    total_discount = disc + loyalty_discount

    # Limite maximale de remise
    if total_discount > MAX_DISCOUNT:
        total_discount = MAX_DISCOUNT
        # Ajustement proportionnel
        ratio = (
            MAX_DISCOUNT / (disc + loyalty_discount)
            if (disc + loyalty_discount) > 0
            else 1
        )
        disc = disc * ratio
        loyalty_discount = loyalty_discount * ratio

    return pts, disc, loyalty_discount, total_discount


# Vérification et calcul de la taxe
def verify_tax(
    products: dict, customer_id: int, totals_by_customer: dict, taxable: float
) -> float:
    tax = 0.0
    all_taxable = True

    for item in totals_by_customer[customer_id]["items"]:
        prod = products.get(item.get_product_id())
        if prod and not prod.get_taxable():
            all_taxable = False
            break

    if all_taxable:
        tax = round(taxable * TAX, 2)
    else:
        # Calcul taxe produit par produit
        for item in totals_by_customer[customer_id]["items"]:
            prod = products.get(item.get_product_id())
            if prod and prod.get_taxable():
                item_total = item.get_qty() * prod.get_price()
                tax += item_total * TAX
        tax = round(tax, 2)
    return tax


# Calcul des frais de port
def shipping_cost_calculation(
    weight: float, subtotal: float, shipping_zones: dict, zone: str
) -> float:
    ship = 0.0

    if subtotal < SHIPPING_LIMIT:
        ship_zone = shipping_zones.get(zone, {"base": 5.0, "per_kg": 0.5})
        base_ship = ship_zone["base"]

        # Palier selon poids
        if weight > 10:
            ship = base_ship + (weight - 10) * ship_zone["per_kg"]
        elif weight > 5:
            ship = base_ship + (weight - 5) * 0.3
        else:
            ship = base_ship

        # Majoration pour zones éloignées
        if zone == "ZONE3" or zone == "ZONE4":
            ship = ship * 1.2
    else:
        if weight > 20:
            ship = (weight - 20) * 0.25
    return ship


# Calcul des frais de traitement
def handling_fee_calculation(item_count: int) -> float:
    handling = 0.0
    if item_count > 10:
        handling = HANDLING_FREE
    if item_count > 20:
        handling = HANDLING_FREE * 2
    return handling


# Regroupement des clients et calcul des totaux
def group_customers(transactions: dict, products: dict, promos: dict) -> dict:
    totals_by_customer = {}
    for transaction in transactions:
        customer_id = transaction.get_customer_id()
        prod = products.get(transaction.get_product_id(), {})

        line_total = calcul_with_promo(transaction, prod, promos)

        # Bonus matin si commande avant 10h
        morning_bonus = 0
        hour = int(transaction.get_time().split(":")[0])
        if hour < 10:
            morning_bonus = line_total * 0.03
        line_total = line_total - morning_bonus

        # Initialisation client si premier achat
        if customer_id not in totals_by_customer:
            totals_by_customer[customer_id] = {
                "subtotal": 0.0,
                "items": [],
                "weight": 0.0,
                "promo_discount": 0.0,
                "morning_bonus": 0.0,
            }

        totals_by_customer[customer_id]["subtotal"] += line_total
        totals_by_customer[customer_id]["weight"] += (
            prod.get_weight() * transaction.get_qty()
        )
        totals_by_customer[customer_id]["items"].append(transaction)
        totals_by_customer[customer_id]["morning_bonus"] += morning_bonus

    return totals_by_customer


# Conversion des devises
def currency_rate_value(currency: str) -> float:
    """
    Retourne le taux de conversion de la devise par rapport à l'EUR.
    Par défaut 1.0 pour EUR, sinon USD=1.1, GBP=0.85
    """
    currency_rate = 1.0
    if currency == "USD":
        return 1.1
    elif currency == "GBP":
        return 0.85
    return currency_rate
