class Product:
    def __init__(self, id, name, category, price, weight=1.0, taxable=True):
        self.id = id
        self.name = name
        self.category = category
        self.price = float(price)
        self.weight = float(weight)
        self.taxable = taxable.lower() == "true"
    
    def get_price(self):
        return self.price

    def get_weight(self):
        return self.weight

    def get_category(self):
        return self.category

    def get_taxable(self):
        return self.taxable
