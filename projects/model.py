from flask_sqlalchemy import SQLAlchemy
db=SQLAlchemy()
class diary_login(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(200),unique=True,nullable=False)
    password=db.Column(db.String(200))
    email=db.Column(db.String(200),unique=True,nullable=False)
    entries = db.relationship('Diary', backref='user', lazy=True)
class Diary(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    date_entry=db.Column(db.String(100))
    text_area=db.Column(db.String(1000))
    mood=db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('diary_login.id'), nullable=False)