from shop import db,app
from datetime import datetime
from shop.user.models import User


class Product(db.Model):
    id = db.Column(db.Integer , primary_key = True)
    name = db.Column(db.String(50) , nullable =False)
    date_created = db.Column(db.Date , default= datetime.now().date)
    image_file = db.Column(db.String(20), nullable=False, default = 'default.jpg')
    price = db.Column(db.Numeric(10,2) , nullable=False)
    tags = db.Column(db.String(200))
    desc = db.Column(db.String(1000))

    category_id = db.Column(db.Integer , db.ForeignKey('category.id') , nullable=False)
    category = db.relationship('Category' , backref=db.backref('posts' , lazy=True))
    user_id = db.Column(db.Integer , db.ForeignKey('user.id') , nullable = False)
    likes = db.relationship('Likes', backref='product', lazy=True)

    carts = db.relationship('Cart', backref=db.backref('product', lazy=True))


    def count_likes(self):
        return len(self.likes)



class Category(db.Model):
    id = db.Column(db.Integer , primary_key = True)
    name = db.Column(db.String(20) , nullable = False , unique = True)



class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    user_link = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)