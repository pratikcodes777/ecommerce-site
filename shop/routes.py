from flask import Flask, url_for, redirect, render_template, request, flash, session
import random
from datetime import datetime, timedelta, timezone
from shop import app, bcrypt, db, mail
from flask_login import login_user, current_user, logout_user
from flask_mail import Message
from shop.models import User



@app.route('/' , methods=['POST' , 'GET'])
def home():
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

    return render_template("home.html")


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
    return render_template("log_in.html")


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
            msg = Message(subject='OTP for your login is: ' , recipients=[email])
            msg.body = str(otp)
            mail.send(msg)
            return redirect(url_for('forgotten_password'))
    return render_template('forgotten_password.html')
