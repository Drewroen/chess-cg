class Modifier:
    def __init__(self, modifier_type: str, data: dict = None):
        self.modifier_type = modifier_type
        self.data = data or {}

    def to_dict(self) -> dict:
        return {"modifier_type": self.modifier_type, "data": self.data}