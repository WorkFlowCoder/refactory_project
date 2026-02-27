import csv
import os
import json
import math
from datetime import datetime

TAX = 0.2
SHIPPING_LIMIT = 50
SHIP = 5.0
LOYALTY_RATIO = 0.01
HANDLING_FREE = 2.5
MAX_DISCOUNT = 200

def read_file(base,path,file):
    file_path = os.path.join(base, path, file)
    try:
        with open(file_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            return list(reader)
    except (IndexError, ValueError):
            pass
    return []

def print_and_save_data(result,base,json_data):
    print(result)
    output_path = os.path.join(base, "output.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)

def load_customers(base,path,file):
    lines = read_file(base,path,file)
    customers = {}
    for row in lines:
        customers[row[0]] = {
            "id": row[0],
            "name": row[1],
            "level": row[2] if len(row) > 2 else "BASIC",
            "shipping_zone": row[3] if len(row) > 3 else "ZONE1",
            "currency": row[4] if len(row) > 4 else "EUR",
        }
    return customers

def load_products(base,path,file):
    lines = read_file(base,path,file)
    products = {}
    for i in range(1, len(lines)):  # skip header
        try:
            product = lines[i]
            products[product[0]] = {
                "id": product[0],
                "name": product[1],
                "category": product[2],
                "price": float(product[3]),
                "weight": float(product[4]) if len(product) > 4 else 1.0,
                "taxable": product[5].lower() == "true" if len(product) > 5 else True,
            }
        except (IndexError, ValueError):
            # Skip silencieux
            pass
    return products

def load_shipping_zones(base,path,file):
    lines = read_file(base,path,file)
    shipping_zones = {}
    for i in range(1, len(lines)):
        shipping_zone = lines[i]
        shipping_zones[shipping_zone[0]] = {
            "zone": shipping_zone[0],
            "base": float(shipping_zone[1]),
            "per_kg": float(shipping_zone[2]) if len(shipping_zone) > 2 else 0.5,
        }
    return shipping_zones

def load_promotions(base,path,file):
    lines = read_file(base,path,file)
    promotions = {}
    for i in range(1, len(lines)):
        promo = lines[i]
        promotions[promo[0]] = {
            "code": promo[0],
            "type": promo[1],
            "value": promo[2],
            "active": promo[3] != "false" if len(promo) > 3 else True,
        }
    return promotions

def load_transactions(base,path,file):
    lines = read_file(base,path,file)
    transactions = []
    for i in range(1, len(lines)):
        transaction = lines[i]
        try:
            transactions.append(
                {
                    "id": transaction[0],
                    "customer_id": transaction[1],
                    "product_id": transaction[2],
                    "qty": int(transaction[3]),
                    "unit_price": float(transaction[4]),
                    "date": transaction[5],
                    "promo_code": transaction[6],
                    "time": transaction[7] if transaction[7] else "12:00",
                }
            )
        except Exception as e:
            continue
    return transactions

def calcul_fidelity_points(transactions):
    loyalty_points = {}
    for transaction in transactions:
        cid = transaction["customer_id"]
        if cid not in loyalty_points:
            loyalty_points[cid] = 0
        loyalty_points[cid] += transaction["qty"] * transaction["unit_price"] * LOYALTY_RATIO
    return loyalty_points

def calcul_with_promo(transaction,prod,promotions):
    discount_rate = 0
    fixed_discount = 0
    promo_code = transaction["promo_code"]
    base_price = prod.get("price", transaction["unit_price"])
    if promo_code and promo_code in promotions:
            promo = promotions[promo_code]
            if promo["active"]:
                if promo["type"] == "PERCENTAGE":
                    discount_rate = float(promo["value"]) / 100
                elif promo["type"] == "FIXED":
                    # Bug: appliqué par ligne au lieu de global
                    fixed_discount = float(promo["value"])
    # Calcul ligne avec réduction promo
    line_total = (
        transaction["qty"] * base_price * (1 - discount_rate) - fixed_discount * transaction["qty"]
    )
    return line_total

def group_by_customers(transactions,products,promotions):
    totals_by_customer = {}
    for transaction in transactions:
        cid = transaction["customer_id"]

        # Récupération produit avec fallback
        prod = products.get(transaction["product_id"], {})

        # Application promo (logique complexe et bugguée)
        line_total = calcul_with_promo(transaction,prod,promotions)

        morning_bonus = 0
        # Bonus matin (règle cachée basée sur heure)
        hour = int(transaction["time"].split(":")[0])
        if hour < 10:
            morning_bonus = line_total * 0.03  # 3% réduction supplémentaire
        line_total = line_total - morning_bonus
        if cid not in totals_by_customer:
            totals_by_customer[cid] = {
                "subtotal": 0.0,
                "items": [],
                "weight": 0.0,
                "promo_discount": 0.0,
                "morning_bonus": 0.0,
            }
        totals_by_customer[cid]["subtotal"] += line_total
        totals_by_customer[cid]["weight"] += prod.get("weight", 1.0) * transaction["qty"]
        totals_by_customer[cid]["items"].append(transaction)
        totals_by_customer[cid]["morning_bonus"] += morning_bonus
    return totals_by_customer

def get_remise(sub,level,totals_by_customer,cid):
    disc = 0.0
    if sub > 50:
        disc = sub * 0.05
    if sub > 100:
        disc = sub * 0.10  # écrase la précédente (bug intentionnel)
    if sub > 500:
        disc = sub * 0.15
    if sub > 1000 and level == "PREMIUM":
        disc = sub * 0.20
    first_order_date = (
        totals_by_customer[cid]["items"][0].get("date", "")
        if totals_by_customer[cid]["items"]
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

def calcul_total_discount(loyalty_points,cid,disc):
    loyalty_discount = 0.0
    pts = loyalty_points.get(cid, 0)
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

def verify_tax(products,cid,totals_by_customer,taxable):
    tax = 0.0
    # Vérifier si tous produits taxables
    all_taxable = True
    for item in totals_by_customer[cid]["items"]:
        prod = products.get(item["product_id"])
        if prod and not prod.get("taxable", True):
            all_taxable = False
            break

    if all_taxable:
        tax = round(taxable * TAX, 2)  # Arrondi 2 décimales
    else:
        # Calcul taxe par ligne (plus complexe)
        for item in totals_by_customer[cid]["items"]:
            prod = products.get(item["product_id"])
            if prod and prod.get("taxable", True):
                item_total = item["qty"] * prod.get("price", item["unit_price"])
                tax += item_total * TAX
        tax = round(tax, 2)
    return tax

def shipping_cost_calculation(weight,sub,shipping_zones,zone):
    # Frais de port complexes (duplication)
    ship = 0.0
    if sub < SHIPPING_LIMIT:
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

def handling_fee_calculation(item_count):
    # Frais de gestion (magic number + condition cachée)
    handling = 0.0
    if item_count > 10:
        handling = HANDLING_FREE
    if item_count > 20:
        handling = HANDLING_FREE * 2  # double pour grosses commandes
    return handling

def currency_rate_value(currency): 
    # Conversion devise (règle cachée pour non-EUR)
        currency_rate = 1.0
        if currency == "USD":
            return 1.1
        elif currency == "GBP":
            return 0.85
        return currency_rate

def report_generator(customers,products,shipping_zones,loyalty_points,totals_by_customer,output_lines): 
    json_data = []
    grand_total = 0.0
    total_tax_collected = 0.0
    # Tri par ID client (comportement à préserver)
    sorted_customer_ids = sorted(totals_by_customer.keys())

    for cid in sorted_customer_ids:
        cust = customers.get(cid, {})
        name = cust.get("name", "Unknown")
        level = cust.get("level", "BASIC")
        zone = cust.get("shipping_zone", "ZONE1")
        currency = cust.get("currency", "EUR")

        sub = totals_by_customer[cid]["subtotal"]
        
        # Remise par paliers (duplication + magic numbers)
        disc = get_remise(sub,level,totals_by_customer,cid)

        # Calcul remise fidélité (duplication)
        pts, disc,loyalty_discount, total_discount = calcul_total_discount(loyalty_points,cid,disc)
        # Calcul taxe (gestion spéciale par produit)
        taxable = sub - total_discount
        tax = verify_tax(products,cid,totals_by_customer,taxable)

        # Frais de port complexes (duplication)
        weight = totals_by_customer[cid]["weight"]
        ship = shipping_cost_calculation(weight,sub,shipping_zones,zone)
        
        # Frais de gestion (magic number + condition cachée)
        item_count = len(totals_by_customer[cid]["items"])
        handling = handling_fee_calculation(item_count)

        # Conversion devise (règle cachée pour non-EUR)
        currency_rate = currency_rate_value(currency)

        total = round((taxable + tax + ship + handling) * currency_rate, 2)
        grand_total += total
        total_tax_collected += tax * currency_rate

        # Formatage texte (dispersé, pas de fonction dédiée)
        output_lines.append(f"Customer: {name} ({cid})")
        output_lines.append(f"Level: {level} | Zone: {zone} | Currency: {currency}")
        output_lines.append(f"Subtotal: {sub:.2f}")
        output_lines.append(f"Discount: {total_discount:.2f}")
        output_lines.append(f"  - Volume discount: {disc:.2f}")
        output_lines.append(f"  - Loyalty discount: {loyalty_discount:.2f}")
        if totals_by_customer[cid]["morning_bonus"] > 0:
            output_lines.append(
                f"  - Morning bonus: {totals_by_customer[cid]['morning_bonus']:.2f}"
            )
        output_lines.append(f"Tax: {tax * currency_rate:.2f}")
        output_lines.append(f"Shipping ({zone}, {weight:.1f}kg): {ship:.2f}")
        if handling > 0:
            output_lines.append(f"Handling ({item_count} items): {handling:.2f}")
        output_lines.append(f"Total: {total:.2f} {currency}")
        output_lines.append(f"Loyalty Points: {math.floor(pts)}")
        output_lines.append("")
    return (json_data,grand_total,total_tax_collected)

def run():
    base = os.path.dirname(__file__)

    #Lecture des données
    customers = load_customers(base, "data", "customers.csv")
    products = load_products(base, "data", "products.csv")
    shipping_zones = load_shipping_zones(base, "data", "shipping_zones.csv")
    promotions = load_promotions(base, "data", "promotions.csv")
    orders = load_transactions(base, "data", "orders.csv")

    # Calcul points de fidélité (première duplication)
    loyalty_points =  calcul_fidelity_points(orders)

    # Groupement par client (logique métier mélangée avec aggregation)
    totals_by_customer = group_by_customers(orders,products,promotions)

    # Génération rapport (mélange calculs + formatage + I/O)
    output_lines = []

    report= report_generator(customers,products,shipping_zones,loyalty_points,totals_by_customer,output_lines)

    output_lines.append(f"Grand Total: {report[1]:.2f} EUR")
    output_lines.append(f"Total Tax Collected: {report[2]:.2f} EUR")

    result = "\n".join(output_lines)
    print_and_save_data(result,base,report[0])

    return result

if __name__ == "__main__":
    run()
