class ShippingZone:
    def __init__(self, zone, base, per_kg=0.5):#base=5.0

        self.zone = zone
        self.base = float(base)
        self.per_kg = float(per_kg)