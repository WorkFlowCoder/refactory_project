from datetime import datetime
from typing import Any

TAX = 0.2
SHIPPING_LIMIT = 50
SHIP = 5.0
LOYALTY_RATIO = 0.01
HANDLING_FREE = 2.5
MAX_DISCOUNT = 200

# Fidelity points

def calcul_fidelity_points(transactions: dict) -> list:
    loyalty_points = {}
    for transaction in transactions:
        customer_id = transaction.get_customer_id()
        if customer_id not in loyalty_points:
            loyalty_points[customer_id] = 0
        loyalty_points[customer_id] += transaction.get_qty() * transaction.get_unit_price() * LOYALTY_RATIO
    return loyalty_points

# Calculate promotions

def calcul_with_promo(transaction: Any,product: Any,promotions: dict) -> list:
    discount_rate = 0
    fixed_discount = 0
    promo_code = transaction.get_promo_code()
    base_price = product.get_price()
    if promo_code and promo_code in promotions:
            promo = promotions[promo_code]
            if promo.get_active():
                if promo.get_type() == "PERCENTAGE":
                    discount_rate = float(promo.get_value()) / 100
                elif promo.get_type() == "FIXED":
                    fixed_discount = float(promo.get_value())
    line_total = (
        transaction.get_qty() * base_price * (1 - discount_rate) - fixed_discount * transaction.get_qty()
    )
    return line_total

# Remise

def get_remise(subtotal: int, level: str, totals_by_customer: dict, customer_id: int) -> float:
    disc = 0.0
    if subtotal > 50:
        disc = subtotal * 0.05
    if subtotal > 100:
        disc = subtotal * 0.10  # écrase la précédente (bug intentionnel)
    if subtotal > 500:
        disc = subtotal * 0.15
    if subtotal > 1000 and level == "PREMIUM":
        disc = subtotal * 0.20
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
    # weekday: 0=Monday, 5=Saturday, 6=Sunday
    if day_of_week == 5 or day_of_week == 6:
        disc = disc * 1.05  # 5% bonus sur remise
    return disc

# Discount

def calcul_total_discount(loyalty_points: list, customer_id: int, disc: float) -> Any:
    loyalty_discount = 0.0
    pts = loyalty_points.get(customer_id, 0)
    if pts > 100:
        loyalty_discount = min(pts * 0.1, 50.0)
    if pts > 500:
        loyalty_discount = min(pts * 0.15, 100.0)  # écrase précédent
    total_discount = disc + loyalty_discount
    if total_discount > MAX_DISCOUNT:
        total_discount = MAX_DISCOUNT
        # Ajustement proportionnel (logique complexe)
        ratio = (
            MAX_DISCOUNT / (disc + loyalty_discount)
            if (disc + loyalty_discount) > 0
            else 1
        )
        disc = disc * ratio
        loyalty_discount = loyalty_discount * ratio
    return pts,disc,loyalty_discount, total_discount

# Tax

def verify_tax(products: dict,customer_id: int,totals_by_customer: dict,taxable:float) -> float:
    tax = 0.0
    # Vérifier si tous produits taxables
    all_taxable = True
    for item in totals_by_customer[customer_id]["items"]:
        prod = products.get(item.get_product_id())
        if prod and not prod.get_taxable():
            all_taxable = False
            break

    if all_taxable:
        tax = round(taxable * TAX, 2)  # Arrondi 2 décimales
    else:
        # Calcul taxe par ligne (plus complexe)
        for item in totals_by_customer[customer_id]["items"]:
            prod = products.get(item.get_product_id())
            if prod and prod.get_taxable():
                item_total = item.get_qty() * prod.get_price()
                tax += item_total * TAX
        tax = round(tax, 2)
    return tax

# Shipping cost

def shipping_cost_calculation(weight: float,subtotal: float,shipping_zones: dict,zone: str) -> float:
    # Frais de port complexes (duplication)
    ship = 0.0
    if subtotal < SHIPPING_LIMIT:
        ship_zone = shipping_zones.get(zone, {"base": 5.0, "per_kg": 0.5})
        base_ship = ship_zone["base"]
        if weight > 10:
            ship = base_ship + (weight - 10) * ship_zone["per_kg"]
        elif weight > 5:
            # Palier intermédiaire (règle cachée)
            ship = base_ship + (weight - 5) * 0.3
        else:
            ship = base_ship

        # Majoration zones éloignées
        if zone == "ZONE3" or zone == "ZONE4":
            ship = ship * 1.2
    else:
        # Livraison gratuite mais frais manutention poids élevé
        if weight > 20:
            ship = (weight - 20) * 0.25
    return ship

# Handling free

def handling_fee_calculation(item_count: int) -> float:
    # Frais de gestion (magic number + condition cachée)
    handling = 0.0
    if item_count > 10:
        handling = HANDLING_FREE
    if item_count > 20:
        handling = HANDLING_FREE * 2  # double pour grosses commandes
    return handling

# Customers actions

def group_by_customers(transactions: dict,products: dict,promotions: dict) -> dict:
    totals_by_customer = {}
    for transaction in transactions:
        customer_id = transaction.get_customer_id()

        # Récupération produit avec fallback
        prod = products.get(transaction.get_product_id(), {})

        # Application promo (logique complexe et bugguée)
        line_total = calcul_with_promo(transaction,prod,promotions)

        morning_bonus = 0
        # Bonus matin (règle cachée basée sur heure)
        hour = int(transaction.get_time().split(":")[0])
        if hour < 10:
            morning_bonus = line_total * 0.03  # 3% réduction supplémentaire
        line_total = line_total - morning_bonus
        if customer_id not in totals_by_customer:
            totals_by_customer[customer_id] = {
                "subtotal": 0.0,
                "items": [],
                "weight": 0.0,
                "promo_discount": 0.0,
                "morning_bonus": 0.0,
            }
        totals_by_customer[customer_id]["subtotal"] += line_total
        totals_by_customer[customer_id]["weight"] += prod.get_weight() * transaction.get_qty()
        totals_by_customer[customer_id]["items"].append(transaction)
        totals_by_customer[customer_id]["morning_bonus"] += morning_bonus
    return totals_by_customer

# Currency

def currency_rate_value(currency: str) -> float: 
    # Conversion devise (règle cachée pour non-EUR)
        currency_rate = 1.0
        if currency == "USD":
            return 1.1
        elif currency == "GBP":
            return 0.85
        return currency_rate