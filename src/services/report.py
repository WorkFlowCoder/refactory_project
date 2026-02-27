import math
from typing import Any
from services.calculations import get_remise
from services.calculations import calcul_discount
from services.calculations import verify_tax
from services.calculations import shipping_cost_calculation
from services.calculations import handling_fee_calculation
from services.calculations import currency_rate_value


def report_generator(
    customers: dict,
    products: dict,
    shipping_zones: dict,
    loyalty_points: list,
    totals_by_customer: dict,
    output_lines: Any,
) -> Any:
    json_data = []
    grand_total = 0.0
    total_tax_collected = 0.0

    def calculate_discounts(customer_id: str, subtotal: float):
        customer = customers.get(customer_id, {})
        # Remise
        disc = get_remise(
            subtotal, customer.get_level(), totals_by_customer, customer_id
        )
        # Remise fidélité
        pts, disc, loyalty_discount, total_discount = calcul_discount(
            loyalty_points, customer_id, disc
        )
        return customer, pts, disc, loyalty_discount, total_discount

    def calculate_totals(customer_id: str, subtotal: float, discount: float):
        customer = customers.get(customer_id, {})
        taxable = subtotal - discount
        # Tax
        tax = verify_tax(products, customer_id, totals_by_customer, taxable)
        weight = totals_by_customer[customer_id]["weight"]
        # Shipping
        ship = shipping_cost_calculation(
            weight, subtotal, shipping_zones, customer.get_shipping_zone()
        )
        item_count = len(totals_by_customer[customer_id]["items"])
        # Handling free
        handling = handling_fee_calculation(item_count)
        currency_rate = currency_rate_value(customer.get_currency())
        total = round((taxable + tax + ship + handling) * currency_rate, 2)
        return tax, ship, handling, currency_rate, total, weight, item_count

    def append_output(
        customer_id: str,
        customer,
        subtotal,
        disc,
        loyalty_discount,
        total_discount,
        tax,
        ship,
        handling,
        total,
        pts,
        weight,
        item_count,
    ):
        output_lines.append(f"Customer: {customer.get_name()} ({customer_id})")
        output_lines.append(
            f"Level: {customer.get_level()} | Zone: "
            f"{customer.get_shipping_zone()} | Currency: "
            f"{customer.get_currency()}"
        )
        output_lines.append(f"Subtotal: {subtotal:.2f}")
        output_lines.append(f"Discount: {total_discount:.2f}")
        output_lines.append(f"  - Volume discount: {disc:.2f}")
        output_lines.append(f"  - Loyalty discount: {loyalty_discount:.2f}")
        if totals_by_customer[customer_id]["morning_bonus"] > 0:
            output_lines.append(
                f"  - Morning bonus: "
                f"{totals_by_customer[customer_id]['morning_bonus']:.2f}"
            )
        output_lines.append(f"Tax: {tax * currency_rate:.2f}")
        tmp = customer.get_shipping_zone()
        shipping_info = f"Shipping ({tmp}, {weight:.1f}kg): {ship:.2f}"
        output_lines.append(shipping_info)
        if handling > 0:
            tmp = item_count
            item_info = f"Handling ({tmp} items): {handling:.2f}"
            output_lines.append(item_info)
        output_lines.append(f"Total: {total:.2f} {customer.get_currency()}")
        output_lines.append(f"Loyalty Points: {math.floor(pts)}")
        output_lines.append("")

    sorted_customer_ids = sorted(totals_by_customer.keys())

    for customer_id in sorted_customer_ids:
        subtotal = totals_by_customer[customer_id]["subtotal"]
        customer, pts, disc, loyalty, discount = calculate_discounts(
            customer_id, subtotal
        )
        tax, ship, handling, currency_rate, total, weight, item_count = (
            calculate_totals(customer_id, subtotal, discount)
        )

        grand_total += total
        total_tax_collected += tax * currency_rate

        append_output(
            customer_id,
            customer,
            subtotal,
            disc,
            loyalty,
            discount,
            tax,
            ship,
            handling,
            total,
            pts,
            weight,
            item_count,
        )
    return json_data, grand_total, total_tax_collected
