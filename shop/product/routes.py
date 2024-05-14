from flask import Flask, url_for, redirect, render_template, request, flash, session
from datetime import datetime, timedelta, timezone
import base64
from shop import app,db, admin_required
from .models import Product, Category


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

        new_product = Product(name=name , image_file=encoded_img , price=price, tags=tags , category_id = category , desc=desc)
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