from flask import Flask, url_for, redirect, render_template, request, flash, session
from datetime import datetime, timedelta, timezone
import base64
from shop import app,db
from .models import Product


@app.route('/add_products' , methods = ['GET', 'POST'])
def add_products():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        image = request.files['img']
        img_data = image.read()
        encoded_img = base64.b64encode(img_data).decode("utf-8")
        tags = request.form['tags']

        new_product = Product(name=name , image_file=encoded_img , price=price, tags=tags)
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully.')
        return redirect(url_for('add_products'))
    return render_template('product/add_product.html')


