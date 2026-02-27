from datetime import datetime

TAX = 0.2
SHIPPING_LIMIT = 50
SHIP = 5.0
LOYALTY_RATIO = 0.01
HANDLING_FREE = 2.5
MAX_DISCOUNT = 200

# Fidelity points

def calcul_fidelity_points(transactions):
    loyalty_points = {}
    for transaction in transactions:
        cid = transaction.get_customer_id()
        if cid not in loyalty_points:
            loyalty_points[cid] = 0
        loyalty_points[cid] += transaction.get_qty() * transaction.get_unit_price() * LOYALTY_RATIO
    return loyalty_points

# Calculate promotions

def calcul_with_promo(transaction,prod,promotions):
    discount_rate = 0
    fixed_discount = 0
    promo_code = transaction.get_promo_code()
    base_price = prod.get_price()
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
        totals_by_customer[cid]["items"][0].get_date()
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

# Discount

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

# Tax

def verify_tax(products,cid,totals_by_customer,taxable):
    tax = 0.0
    # Vérifier si tous produits taxables
    all_taxable = True
    for item in totals_by_customer[cid]["items"]:
        prod = products.get(item.get_product_id())
        if prod and not prod.get_taxable():
            all_taxable = False
            break

    if all_taxable:
        tax = round(taxable * TAX, 2)  # Arrondi 2 décimales
    else:
        # Calcul taxe par ligne (plus complexe)
        for item in totals_by_customer[cid]["items"]:
            prod = products.get(item.get_product_id())
            if prod and prod.get_taxable():
                item_total = item.get_qty() * prod.get_price()
                tax += item_total * TAX
        tax = round(tax, 2)
    return tax

# Shipping cost

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

# Handling free

def handling_fee_calculation(item_count):
    # Frais de gestion (magic number + condition cachée)
    handling = 0.0
    if item_count > 10:
        handling = HANDLING_FREE
    if item_count > 20:
        handling = HANDLING_FREE * 2  # double pour grosses commandes
    return handling

# Customers actions

def group_by_customers(transactions,products,promotions):
    totals_by_customer = {}
    for transaction in transactions:
        cid = transaction.get_customer_id()

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
        if cid not in totals_by_customer:
            totals_by_customer[cid] = {
                "subtotal": 0.0,
                "items": [],
                "weight": 0.0,
                "promo_discount": 0.0,
                "morning_bonus": 0.0,
            }
        totals_by_customer[cid]["subtotal"] += line_total
        totals_by_customer[cid]["weight"] += prod.get_weight() * transaction.get_qty()
        totals_by_customer[cid]["items"].append(transaction)
        totals_by_customer[cid]["morning_bonus"] += morning_bonus
    return totals_by_customer

# Currency

def currency_rate_value(currency): 
    # Conversion devise (règle cachée pour non-EUR)
        currency_rate = 1.0
        if currency == "USD":
            return 1.1
        elif currency == "GBP":
            return 0.85
        return currency_rate