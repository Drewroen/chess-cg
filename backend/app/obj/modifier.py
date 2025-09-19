class Modifier:
    def __init__(self, modifier_type: str):
        self.type = modifier_type

    def to_dict(self) -> dict:
        return {"type": self.type}
