import numpy as np
from flask import Flask, redirect, url_for, request, render_template
from flask_sqlalchemy import SQLAlchemy


# creating instance of the class
app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers.db'
db = SQLAlchemy(app)


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

with app.app_context():
    db.create_all()
