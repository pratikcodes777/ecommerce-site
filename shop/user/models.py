from shop import db ,login_manager,app
from flask_login import UserMixin
from datetime import datetime



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(120) , unique = True , nullable = False)
    password = db.Column(db.String(60) , nullable=False)
    role = db.Column(db.String(20) , nullable=False , default='customer')

    cart_items = db.relationship('Cart', backref=db.backref('user', lazy=True))




