class Product:
    def __init__(self, product):
        self.id = product[0]
        self.name = product[1]
        self.category = product[2]
        self.price = float(product[3])
        self.weight = float(product[4]) if product[4] else 1.0
        self.taxable = product[5].lower() == "true" if product[5] else True

    def get_price(self):
        return self.price

    def get_weight(self):
        return self.weight

    def get_category(self):
        return self.category

    def get_taxable(self):
        return self.taxable
