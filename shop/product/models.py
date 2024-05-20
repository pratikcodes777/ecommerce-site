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
    orders = db.relationship('Order', backref=db.backref('ordered_product', lazy=True))


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


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(100), nullable=False, default="Pending")
    invoice = db.Column(db.String(1000), nullable=True)  

    user_link = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    user = db.relationship('User', backref='user_orders')
    product = db.relationship('Product', backref='ordered_in_orders')

    def generate_invoice(self):
        user = User.query.get(self.user_link)
        product = Product.query.get(self.product_link)
        self.invoice = f"""
        Order ID: {self.id}
        User: {user.username}
        Product: {product.name}
        Quantity: {self.quantity}
        Price per item: {self.price / self.quantity:.2f}
        Total Price: {self.price:.2f}
        Status: {self.status}
        """