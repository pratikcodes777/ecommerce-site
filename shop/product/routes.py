from flask import Flask, url_for, redirect, render_template, request, flash, session, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta, timezone
import base64
from shop import app,db, admin_required
from .models import Product, Category
from shop.product.models import Likes, Cart
from shop.user.models import User


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



@app.route('/add-to-cart/<int:item_id>')
@login_required
def add_to_cart(item_id):
    item_to_add = Product.query.get(item_id)
    item_exists = Cart.query.filter_by(product_link=item_id, user_link=current_user.id).first()
    if item_exists:
        try:
            item_exists.quantity = item_exists.quantity + 1
            db.session.commit()
            flash(f' Quantity of { item_exists.product.name } has been updated')
            return redirect(request.referrer)
        except Exception as e:
            print('Quantity not Updated', e)
            flash(f'Quantity of { item_exists.product.name } not updated')
            return redirect(request.referrer)

    new_cart_item = Cart()
    new_cart_item.quantity = 1
    new_cart_item.product_link = item_to_add.id
    new_cart_item.user_link = current_user.id

    try:
        db.session.add(new_cart_item)
        db.session.commit()
        flash(f'{new_cart_item.product.name} added to cart')
    except Exception as e:
        print('Item not added to cart', e)
        flash(f'{new_cart_item.product.name} has not been added to cart')

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