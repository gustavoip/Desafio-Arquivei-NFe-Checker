from nfe_checker.shared import db


class Nfe(db.Model):
    __tablename__ = "nfes"

    id = db.Column(db.Integer, primary_key=True)
    access_key = db.Column(db.String())
    value = db.Column(db.Float())

    def __init__(self, access_key: str, value: float):
        self.access_key = access_key
        self.value = value

    def __repr__(self):
        return f"<id {self.id};value {self.value};access_key {self.access_key}>"


class CursorPosition(db.Model):
    __tablename__ = "cursors"
    id = db.Column(db.Integer, primary_key=True)
    cursor_position = db.Column(db.Integer())

    def __init__(self, cursor_position: int):
        self.cursor_position = cursor_position
