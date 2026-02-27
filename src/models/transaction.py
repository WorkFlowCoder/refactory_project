class Transaction:
    def __init__(self, transaction):
        self.id = transaction[0]
        self.customer_id = transaction[1]
        self.product_id = transaction[2]
        self.qty = int(transaction[3])
        self.unit_price = float(transaction[4])
        self.date = transaction[5] if transaction[5] else ""
        self.promo_code = transaction[6]
        self.time = transaction[7] if transaction[7] else "12:00"

    def get_id(self):
        return self.id

    def get_qty(self):
        return self.qty

    def get_customer_id(self):
        return self.customer_id

    def get_unit_price(self):
        return self.unit_price

    def get_product_id(self):
        return self.product_id

    def get_promo_code(self):
        return self.promo_code

    def get_time(self):
        return self.time

    def get_date(self):
        return self.date
