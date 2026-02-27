class ShippingZone:
    def __init__(self, zone, base, per_kg=0.5):
        self.zone = zone
        self.base = float(base)
        self.per_kg = float(per_kg)
