from shop import db,app
from datetime import datetime


class Product(db.Model):
    id = db.Column(db.Integer , primary_key = True)
    name = db.Column(db.String(50) , nullable =False)
    date_created = db.Column(db.Date , default= datetime.now().date)
    image_file = db.Column(db.String(20), nullable=False, default = 'default.jpg')
    price = db.Column(db.Numeric(10,2) , nullable=False)
    tags = db.Column(db.String(200))