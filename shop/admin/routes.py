from flask import Flask, url_for, redirect, render_template, request, flash, session
from flask_login import login_required, login_user, current_user
from sqlalchemy import desc
from shop.user.models import User
from shop.product.models import Product, Category,Order

from shop import db,app, bcrypt,admin_required


@app.route('/admin_home')
@login_required
@admin_required
def admin_home():
    products = Product.query.all()
    return render_template('admin/admin_home.html' , products=products)


@app.route('/admin_login' , methods= ['POST' , 'GET'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            if bcrypt.check_password_hash(existing_user.password, password):
                login_user(existing_user)
                return redirect(url_for('admin_home'))
            else:
                flash('Incorrect Username or Password')
    return render_template("admin/admin_login.html")



@app.route('/categories')
@admin_required
def categories():
    all_categories = Category.query.all()
    return render_template('admin/category.html' , all_categories=all_categories)


@app.route('/view_users')
@admin_required
def view_users():
    all_users = User.query.all()
    return render_template('admin/view_users.html' , all_users=all_users)



@app.route('/delete_user/<int:id>')
def delete_user(id):
    user_to_delete = User.query.get_or_404(id)
    db.session.delete(user_to_delete)
    db.session.commit()
    flash('User deleted successfully')
    return redirect(url_for('view_users'))


@app.route('/view-orders')
@admin_required
def view_orders():
    orders = Order.query.order_by(desc(Order.id))
    return render_template('admin/orders.html', orders=orders)


@app.route('/update-order/<int:order_id>', methods=['GET', 'POST'])
@admin_required
def update_order(order_id):
    order = Order.query.get_or_404(order_id)

    if request.method == 'POST':
        status = request.form.get('order_status')

        if status:  
            order.status = status

            try:
                db.session.commit()
                flash(f'Order {order_id} updated successfully.', 'success')
                return redirect('/view-orders')
            except Exception as e:
                print(e)
                flash(f'Error updating order {order_id}.', 'danger')
                return redirect('/view-orders')
        else:
            flash('Invalid form data.', 'danger')
            return redirect('/update-order/{order_id}')

    return render_template('admin/update_order.html',  order=order )