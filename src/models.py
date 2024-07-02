from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    checked_in = db.Column(db.Boolean, default=False)
    check_ins_outs = db.relationship('CheckInOut', backref='child', lazy=True)

class CheckInOut(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(3))  # 'in' or 'out'
    timestamp = db.Column(db.DateTime)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'))
