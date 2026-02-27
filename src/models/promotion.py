class Promotion:
    def __init__(self, code, type, value, active=True):
        self.code = code
        self.type = type
        self.value = float(value)
        self.active = bool(active)
    
    def get_active(self):
        return self.active
    
    def get_type(self):
        return self.type
    
    def get_value(self):
        return self.value