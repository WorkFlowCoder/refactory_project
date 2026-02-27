class Customer:
    def __init__(self, id, name="Unknown", level="BASIC", shipping_zone="ZONE1", currency="EUR"):
        self.id = id
        self.name = name
        self.level = level
        self.shipping_zone = shipping_zone
        self.currency = currency
    
    def get_name(self):
        return self.name
    
    def get_level(self):
        return self.level
    
    def get_shipping_zone(self):
        return self.shipping_zone
    
    def get_currency(self):
        return self.currency
