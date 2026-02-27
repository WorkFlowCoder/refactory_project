import math
from services.calculations import *

def report_generator(customers,products,shipping_zones,loyalty_points,totals_by_customer,output_lines): 
    json_data = []
    grand_total = 0.0
    total_tax_collected = 0.0
    # Tri par ID client (comportement à préserver)
    sorted_customer_ids = sorted(totals_by_customer.keys())

    for cid in sorted_customer_ids:
        cust = customers.get(cid, {})
        name = cust.get_name()
        level = cust.get_level()
        zone = cust.get_shipping_zone()
        currency = cust.get_currency()

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