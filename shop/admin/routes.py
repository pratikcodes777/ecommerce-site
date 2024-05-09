from flask import Flask, url_for, redirect, render_template, request, flash, session
from flask_login import login_required

from shop.user.models import User
from shop.product.models import Product, Category

from shop import db,app


@app.route('/admin_home')
@login_required
def admin_home():
    products = Product.query.all()
    return render_template('admin/admin_home.html' , products=products)


@app.route('/categories')
def categories():
    all_categories = Category.query.all()
    return render_template('admin/category.html' , all_categories=all_categories)


@app.route('/view_users')
def view_users():
    all_users = User.query.all()
    return render_template('admin/view_users.html' , all_users=all_users)
