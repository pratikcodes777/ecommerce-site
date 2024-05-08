from flask import Flask, url_for, redirect, render_template, request, flash, session
import random
from datetime import datetime, timedelta, timezone
from shop import app, bcrypt, db, mail
from flask_login import login_user, current_user, logout_user
from flask_mail import Message
from .models import User
from shop.product.models import Product
from sqlalchemy import or_



@app.route('/' , methods=['POST' , 'GET'])
def home():
    all_products = Product.query.all()
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        repassword = request.form['repassword']
        hashed_password = bcrypt.generate_password_hash(password)
        existing_email = User.query.filter_by(email=email).first()
        if not existing_email:
            if password == repassword:
                new_user = User(email=email , password=hashed_password)
                db.session.add(new_user)
                db.session.commit()
                flash("User created! Login to Continue.")
                return redirect(url_for('log_in'))
            else:
                flash("Please choose same password.")
        else:
            flash("Email already exists.")

    return render_template("home.html" , all_products=all_products)


@app.route('/log_in' , methods= ['POST' , 'GET'])
def log_in():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            if bcrypt.check_password_hash(existing_user.password, password):
                login_user(existing_user)
                return redirect(url_for('home'))
            else:
                flash('Incorrect Username or Password')
        else:
            flash('Please register to continue.')
            return redirect(url_for('home'))
    return render_template("user/log_in.html")


@app.route('/log_out')
def log_out():
    logout_user()
    flash("You have been logged out! Please login to continue.")
    return redirect(url_for('home'))



@app.route('/forgotten_password' , methods= ['POST' , 'GET'])
def forgotten_password():
    if request.method == 'POST':
        email = request.form['email']
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            session['email'] = email
            otp = random.randint(1000, 9999)
            current_time = datetime.now(timezone.utc) 
            session['otp'] = {
                'value': otp,
                'created_at': current_time
            }
            msg = Message(subject='OTP for your login is: ' , recipients=[email])
            msg.body = str(otp)
            mail.send(msg)
            return redirect(url_for('otp'))
    return render_template('user/forgotten_password.html')


@app.route('/otp' , methods=["POST" , "GET"])
def otp():
    if request.method == 'POST':
        if 'otp' in session:
            user_otp = request.form["user_otp"]
            otp_data = session.get('otp')
            if otp_data:
                if user_otp == str(otp_data['value']):
                    current_time = datetime.now(timezone.utc)
                    if current_time - otp_data['created_at'] <= timedelta(minutes=1):
                        return redirect(url_for('update_password'))
                    else:
                        flash("OTP has expired. Please generate a new one.")
                        return redirect(url_for('forgotten_password'))
                else:
                    flash("OTP didn't match")
            else:
                flash("Please send new OTP again!")
                return redirect(url_for('forgotten_password'))

    return render_template('user/otp.html')


@app.route('/update_password' , methods=['POST', 'GET'])
def update_password():
    if request.method == 'POST':
        new_password = request.form['new_password']
        re_password = request.form['re_password']
        if new_password == re_password:
            email = session.get('email')
            user = User.query.filter_by(email=email).first()
            if user:
                hashed_password = bcrypt.generate_password_hash(new_password)
                user.password = hashed_password

                db.session.commit()
                session.pop('email')
                session.pop('otp')
                return redirect(url_for('log_in'))
            else:
                flash("User doesn't found")
        else:
            flash("Password didn't match! Please enter same password.")
    return render_template('user/update_password.html')


@app.route("/search", methods=['POST'])
def search():
    if request.method == 'POST':
        search_query = request.form['search']
        search_results = Product.query.filter(or_(Product.name.like(f"%{search_query}%"), Product.tags.like(f"%{search_query}%"))).all()

        return render_template('user/search_results.html', search_results=search_results , search_query=search_query)