import os
from services.loaders import load_transactions
from services.loaders import load_customers
from services.loaders import load_products
from services.loaders import load_promotions
from services.loaders import load_shipping_zones
from services.report import report_generator
from services.calculations import calcul_fidelity_points, group_customers
from services.report_writer import ReportWriter


def run() -> None:
    base = os.path.dirname(__file__)

    # Lecture des données
    customers = load_customers(base, "data", "customers.csv")
    products = load_products(base, "data", "products.csv")
    shipping_zones = load_shipping_zones(base, "data", "shipping_zones.csv")
    promotions = load_promotions(base, "data", "promotions.csv")
    orders = load_transactions(base, "data", "orders.csv")

    # Calcul points de fidélité (première duplication)
    loyalty_points = calcul_fidelity_points(orders)

    # Groupement par client (logique métier mélangée avec aggregation)
    totals_by_customer = group_customers(orders, products, promotions)

    # Génération rapport (mélange calculs + formatage + I/O)
    output_lines = []

    report = report_generator(
        customers,
        products,
        shipping_zones,
        loyalty_points,
        totals_by_customer,
        output_lines,
    )

    output_lines.append(f"Grand Total: {report[1]:.2f} EUR")
    output_lines.append(f"Total Tax Collected: {report[2]:.2f} EUR")

    output = ReportWriter(base)
    result = "\n".join(output_lines)
    output.print_and_save(result, "output.json", report[0])

    return result


if __name__ == "__main__":
    run()
