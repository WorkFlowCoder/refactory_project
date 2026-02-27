class Promotion:
    def __init__(self, promo):
        self.code = promo[0]
        self.type = promo[1]
        self.value = float(promo[2])
        self.active = bool(promo[3]) if promo[3] else True

    def get_active(self):
        return self.active

    def get_type(self):
        return self.type

    def get_value(self):
        return self.value
