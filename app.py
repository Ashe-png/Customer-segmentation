import numpy as np
import flask
import pickle
from flask import Flask, redirect, url_for, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from sqlalchemy.exc import IntegrityError


# creating instance of the class
app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers.db'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'youremail@gmail.com'
app.config['MAIL_PASSWORD'] = 'yourpassword'
app.config['MAIL_DEFAULT_SENDER'] = 'youremail@gmail.com'

db = SQLAlchemy(app)
mail = Mail(app)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    annual_income = db.Column(db.Integer)
    spending_score = db.Column(db.Integer)
    email = db.Column(db.String(120), unique=True, nullable=False)
    cluster = db.Column(db.Integer)
    # Add more columns as needed

def send_email(to, subject, body):
    msg = Message(subject, recipients=[to])
    msg.body = body
    mail.send(msg)


# to tell flask what url should trigger the function index()


@app.route('/')
@app.route('/index')
def index():
    return flask.render_template('index.html')


# prediction function
# Memprediksi input dari form user
def ValuePredictor(to_predict_list):
    to_predict = np.array(to_predict_list).reshape(1, 3)
    loaded_model = pickle.load(
        open("./model/model.pkl", "rb"))  # load the model
    # predict the values using loded model
    result = loaded_model.predict(to_predict)
    return result

@app.route('/customers')
def view_customers():
    with app.app_context():
        customers = Customer.query.all()
        return flask.render_template('customers.html', customers=customers)

@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        gender = request.form['gender']
        age = request.form['age']
        annual_income = request.form['annual_income']
        spending_score = request.form['spending_score']

        to_predict_list = list(map(int, [age, annual_income, spending_score]))
        result = ValuePredictor(to_predict_list)

        if int(result) == 0:
            prediction = 'Low annual income low score'
        elif int(result) == 1:
            prediction = 'High annual income high score'
        elif int(result) == 2:
            prediction = 'High annual income low score'
        elif int(result) == 3:
            prediction = 'Medium annual income and score'
        elif int(result) == 4:
            prediction = 'Low annual income and high score'

        with app.app_context():
            customer1 = Customer(name=name, email=email, gender=gender, age=age, annual_income=annual_income, spending_score=spending_score, cluster=int(result))
            try:
                db.session.add(customer1)
                db.session.commit()
                message = 'Added to Database'
                if customer1.cluster == 1:
                    subject = "NAYA BARSA KO DHAMAKA"
                    body = "Dear customer, On the occasion of New Year 2080 you can use PROMO CODE: NAYABARSA2080 and get 20 percent off on every item  your purchase"
                    send_email(customer1.email, subject, body)
            except IntegrityError:
                db.session.rollback()
                message = f'Customer with email {email} already exists in database'

        return render_template("result.html", prediction=prediction, name=name, message=message)
    
@app.route('/email_cluster/<int:cluster_id>')
def email_cluster(cluster_id):
    with app.app_context():
        customers = Customer.query.filter_by(cluster=cluster_id).all()
        email_addresses = [customer.email for customer in customers]
        return render_template('email_cluster.html', email_addresses=email_addresses, cluster_id=cluster_id)
        
@app.route('/send_email_cluster/<int:cluster_id>', methods=['POST'])
def send_email_cluster(cluster_id):
    with app.app_context():
        customers = Customer.query.filter_by(cluster=cluster_id).all()
        email_addresses = [customer.email for customer in customers]
        subject = "Important Information for Cluster {}".format(cluster_id)
        body = "Dear customer,\n\nWe wanted to inform you of some important information regarding your account. Please log in to your account to see the details.\n\nThank you,\nYour Bank"
        for email in email_addresses:
            send_email(email, subject, body)
        return redirect(url_for('view_customers'))

@app.route('/delete_all')
def delete_all():
    with app.app_context():
        customers = Customer.query.all()
        for customer in customers:
            db.session.delete(customer)
        db.session.commit()
        print('All data deleted')
        return redirect(url_for('view_customers'))

if __name__ == "__main__":
    app.run()  # use debug = False for jupyter notebook

import sqlite3