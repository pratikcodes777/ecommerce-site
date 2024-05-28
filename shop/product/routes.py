from flask import Flask, url_for, redirect, render_template, request, flash, session, jsonify, send_from_directory,abort, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta, timezone
import base64
from shop import app,db, admin_required
from .models import Product, Category
from shop.product.models import Likes, Cart,Order,Rating
from shop.user.models import User
from fpdf import FPDF
import os
import string
from sqlalchemy import desc, or_, func, extract
import random


@app.route('/add_products' , methods = ['GET', 'POST'])
@admin_required
def add_products():
    categories = Category.query.all()
    if request.method == 'POST':
        
        name = request.form['name']
        price = request.form['price']
        image = request.files['img']
        img_data = image.read()
        encoded_img = base64.b64encode(img_data).decode("utf-8")
        tags = request.form['tags']
        category = request.form['category']
        desc = request.form['desc']

        new_product = Product(name=name , image_file=encoded_img , price=price, tags=tags , category_id = category , desc=desc , user_id=current_user.id)
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully.')
        return redirect(url_for('add_products'))
    return render_template('product/add_product.html' , categories=categories)


@app.route('/add_category' , methods = ["GET" , "POST"])
@admin_required
def add_category():
    if request.method == 'POST':
        category = request.form['category']
        new_category = Category(name=category)
        db.session.add(new_category)
        db.session.commit()
        flash("Category added successfully.")
        return redirect(url_for('add_category'))

    return render_template('product/add_category.html')


@app.route('/update_products/<int:id>' , methods=['POST' , 'GET'])
@admin_required
def update_products(id):
    product_to_update = Product.query.get_or_404(id)
    categories = Category.query.all()
    if request.method == 'POST':
        product_to_update.name = request.form['name']
        product_to_update.price = request.form['price']
        new_image = request.files['img']
        img_data = new_image.read()
        encoded_image = base64.b64encode(img_data).decode('utf-8')
        product_to_update.image_file = encoded_image
        product_to_update.tags = request.form['tags']
        product_to_update.category_id = request.form['category']
        product_to_update.desc = request.form['desc']

        db.session.commit()
        flash("Products Updated successfully.")
        return redirect(url_for('admin_home'))


    return render_template('product/update_products.html' , product_to_update=product_to_update , categories=categories)


@app.route('/delete_products/<int:id>')
@admin_required
def delete_products(id):
    product_to_delete = Product.query.get_or_404(id)


    db.session.delete(product_to_delete)
    db.session.commit()
    flash("Product deleted successfully.")
    return redirect(url_for('admin_home'))


@app.route('/update_category/<int:id>' , methods=['POST' , 'GET'])
@admin_required
def update_category(id):
    category_to_update = Category.query.get_or_404(id)
    if request.method == 'POST':
        category_to_update.name = request.form['category']
        db.session.commit()
        flash("Category updated successfully.")
        return redirect(url_for('categories'))
    
    return render_template('product/update_category.html' , category_to_update=category_to_update)


@app.route('/delete_category/<int:id>')
@admin_required
def delete_category(id):
    category_to_delete = Category.query.get_or_404(id)
    if category_to_delete:
        products = Product.query.filter_by(category_id=id).all()
        for product in products:
            product.category_id = None  
            db.session.commit()
    db.session.delete(category_to_delete)
    db.session.commit()
    flash("Category deleted successfully.")
    return redirect(url_for('categories'))




@app.route('/get_category/<int:id>')
def get_category(id):
    all_category = Category.query.all()
    category = Category.query.get_or_404(id)
    categories = Product.query.filter_by(category_id=id)
    return render_template('home.html' , categories=categories, all_category=all_category, category=category)


@app.route('/expand_product/<int:product_id>')
def expand_product(product_id):
    product_to_expand = Product.query.get_or_404(product_id)
    return render_template('product/expand_product.html' , product_to_expand=product_to_expand)




@app.route('/like/<int:product_id>', methods=['POST'])
def like(product_id):
    product = Product.query.get(product_id)
    existing_like = Likes.query.filter_by(product_id=product_id, user_id=current_user.id).first()
    if existing_like:
        db.session.delete(existing_like)
        liked = False
   
    else:
        new_like = Likes(product_id=product_id, user_id=current_user.id)
        db.session.add(new_like)
        liked = True

    db.session.commit()
    like_count = product.count_likes()
    
    return jsonify({'liked': liked, 'like_count': like_count})


@app.route('/liked_users/<int:id>')
def liked_users(id):
    product = Product.query.get_or_404(id)
    liked_users = []
    for like in product.likes:
        user = User.query.get(like.user_id)
        liked_users.append(user.email)
    return render_template('user/liked_users.html' ,product=product , liked_users=liked_users )


@app.route('/liked_products')
@login_required
def liked_products():
    liked_products = Product.query.join(Likes).filter(Likes.user_id == current_user.id).all()

    return render_template('product/liked_products.html', liked_products=liked_products)



@app.route('/add-to-cart/<int:item_id>', methods=['POST' , 'GET'])
@login_required
def add_to_cart(item_id):
    item_to_add = Product.query.get_or_404(item_id)  
    item_exists = Cart.query.filter_by(product_link=item_id, user_link=current_user.id).first()
    
    if item_exists:
        try:
            item_exists.quantity += 1
            db.session.commit()
            flash(f'Quantity of {item_exists.product.name} has been updated', 'success')
        except Exception as e:
            db.session.rollback() 
            print('Quantity not updated:', e)
            flash(f'Quantity of {item_exists.product.name} could not be updated', 'error')
    else:
        new_cart_item = Cart()
        new_cart_item.quantity = 1
        new_cart_item.product_link = item_to_add.id
        new_cart_item.user_link = current_user.id

        try:
            db.session.add(new_cart_item)
            db.session.commit()
            flash(f'{new_cart_item.product.name} added to cart', 'success')
        except Exception as e:
            db.session.rollback()
            print('Item not added to cart:', e)
            flash(f'{new_cart_item.product.name} could not be added to cart', 'error')

    return redirect(request.referrer)


@app.route('/cart')
@login_required
def show_cart():
    cart = Cart.query.filter_by(user_link=current_user.id).all()
    amount = 0
    for item in cart:
        amount += item.product.price * item.quantity

    return render_template('cart.html', cart=cart, amount=amount, total=amount+100)




@app.route('/pluscart')
@login_required
def plus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        cart_item.quantity = cart_item.quantity + 1
        db.session.commit()

        cart = Cart.query.filter_by(user_link=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)



@app.route('/minuscart')
@login_required
def minus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        cart_item.quantity = cart_item.quantity - 1
        db.session.commit()

        cart = Cart.query.filter_by(user_link=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)


@app.route('/remove-cart/<int:id>')
def remove_cart(id):
    cart_to_delete = Cart.query.get_or_404(id)
    db.session.delete(cart_to_delete)
    db.session.commit()
    flash('Cart deleted successfully')
    return redirect(url_for('show_cart'))


# @app.route('/place-order')
# @login_required
# def place_order():
#     cart_items = Cart.query.filter_by(user_link=current_user.id).all()
#     for item in cart_items:
#         new_order = Order(
#             quantity=item.quantity,
#             price=item.product.price * item.quantity,
#             user_link=current_user.id,
#             product_link=item.product.id
#         )
#         new_order.generate_invoice()  # Generate invoice for the order
#         db.session.add(new_order)
#         db.session.delete(item)  # Remove item from cart after placing order
#     db.session.commit()
#     flash('Order placed successfully. Status is Pending.')
#     return redirect(url_for('show_cart'))



@app.route('/place-order')
@login_required
def place_order():
    cart_items = Cart.query.filter_by(user_link=current_user.id).all()
    orders = []
    for item in cart_items:
        new_order = Order(
            quantity=item.quantity,
            price=float(item.product.price) * item.quantity,
            user_link=current_user.id,
            product_link=item.product.id
        )
        new_order.generate_invoice()
        db.session.add(new_order)
        orders.append(new_order)
        db.session.delete(item)  
    db.session.commit()

    pdf_filename = generate_invoice_pdf(orders)
    flash('Order placed successfully. Status is Pending.')
    return redirect(url_for('show_invoice', pdf_filename=pdf_filename))



def generate_invoice_number(length=8):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))




def generate_invoice_pdf(orders):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    user = User.query.get(orders[0].user_link)
    invoice_number = generate_invoice_number()

    # User details and invoice number
    pdf.cell(200, 10, txt=f"Invoice Number: #{invoice_number}", ln=True)
    pdf.cell(200, 10, txt=f"Customer Name: {user.username}", ln=True)
    pdf.cell(200, 10, txt=f"Customer Email: {user.email}", ln=True)
    pdf.cell(200, 10, txt=" ", ln=True)

    # Table headers
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(40, 10, txt="S.N.", border=1, align="C")
    pdf.cell(60, 10, txt="Product", border=1, align="C")
    pdf.cell(20, 10, txt="Quantity", border=1, align="C")
    pdf.cell(40, 10, txt="Price per item", border=1, align="C")
    pdf.cell(40, 10, txt="Total Price", border=1, align="C")
    pdf.ln()

    pdf.set_font("Arial", size=12)
    grand_total = 0
    counter = 1

    for order in orders:
        product = Product.query.get(order.product_link)
        total_price = order.price
        grand_total += total_price

        pdf.cell(40, 10, txt=f"{counter}", border=1, align="C")
        pdf.cell(60, 10, txt=f"{product.name}", border=1, align="C")
        pdf.cell(20, 10, txt=f"{order.quantity}", border=1, align="C")
        pdf.cell(40, 10, txt=f"{order.price / order.quantity:.2f}", border=1, align="C")
        pdf.cell(40, 10, txt=f"{total_price:.2f}", border=1, align="C")
        pdf.ln()

        counter += 1

    # Grand total
    pdf.cell(160, 10, txt="Grand Total", border=1, align="C")
    pdf.cell(40, 10, txt=f"{grand_total:.2f}", border=1, align="C")
    pdf.ln()

    invoice_dir = os.path.join(current_app.root_path, 'static', 'invoices')
    if not os.path.exists(invoice_dir):
        os.makedirs(invoice_dir)

    pdf_filename = f'invoice_{current_user.id}_{invoice_number}.pdf'
    pdf_path = os.path.join(invoice_dir, pdf_filename)
    pdf.output(pdf_path)

    return pdf_filename



@app.route('/orders')
@login_required
def order():
    orders = Order.query.filter_by(user_link=current_user.id).order_by(desc(Order.id)).all()
    return render_template('product/orders.html', orders=orders)


@app.route('/cancel_order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)

    if order.user_link == current_user.id and order.status == 'Pending':
        order.status = 'Canceled'
        db.session.commit()
        flash('Order successfully cancelled.', 'success')  
    else:
        flash('Failed to cancel order. Either the order does not exist or it is not pending.')  
    
    return redirect(url_for('order'))



@app.route('/show-invoice')
@login_required
def show_invoice():
    pdf_filename = request.args.get('pdf_filename')
    if not pdf_filename:
        flash('Invoice not found.', 'danger')
        return redirect(url_for('show_cart'))
    return render_template('product/show_invoice.html', pdf_filename=pdf_filename)



@app.route('/invoices/<filename>')
@login_required
def serve_invoice(filename):
    try:
        return send_from_directory(os.path.join(current_app.root_path, 'static', 'invoices'), filename)
    except FileNotFoundError:
        abort(404)



@app.route('/purchase-history')
@login_required
def purchase_history():
    accepted_orders = Order.query.filter_by(user_link=current_user.id, status='Delivered').all()
    return render_template('user/purchase_history.html', orders=accepted_orders)



@app.route('/purchased-products')
@login_required
def purchased_products():
    # Fetch all delivered orders for the current user
    all_orders = Order.query.filter_by(user_link=current_user.id, status='Delivered').all()
    
    # Use a dictionary to store unique products
    unique_products = {}
    for order in all_orders:
        if order.product_link not in unique_products:
            unique_products[order.product_link] = order
    
    # Convert the dictionary values to a list
    unique_orders = list(unique_products.values())

    return render_template('user/purchased_products.html', orders=unique_orders)



@app.route('/rate_product/<int:product_id>/<int:rating_value>', methods=['POST'])
@login_required
def rate_product(product_id, rating_value):
    product = Product.query.get_or_404(product_id)
    purchase = Order.query.filter_by(user_link=current_user.id, product_link=product_id, status='Delivered').first()

    if not purchase:
        return jsonify({'success': False, 'message': 'You can only rate products that have been delivered.'}), 403

    if rating_value < 1 or rating_value > 5:
        return jsonify({'success': False, 'message': 'Invalid rating value.'}), 400

    rating = Rating.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if rating:
        rating.value = rating_value
    else:
        rating = Rating(value=rating_value, user_id=current_user.id, product_id=product_id)
        db.session.add(rating)

    new_rating =product.average_rating()
    db.session.commit()

    return jsonify({'success': True, 'new_rating': new_rating}), 200
