import sqlite3

import sqlalchemy.exc
from flask import Flask, render_template, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, NumberRange, EqualTo
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


# telling flask app what it is gonna be running
app = Flask(__name__)
app.config['SECRET_KEY'] = 'no one can crack this'
# database initialization
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customer.sqlite3'
app.config['SQLALCHEMY_BINDS'] = {'two': 'sqlite:///product.sqlite3'}
db = SQLAlchemy(app)


# creating customer database
class customer(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Text(), nullable= False)
    pwd =  db.Column(db.Text(), nullable = False)
    mobile = db.Column(db.Integer(), nullable = False)
    address = db.Column(db.Text(), nullable = False)

    def __repr__(self):  # I don't know why this exists but it does
        return '<Name %r>' % self.name


class product(db.Model):
    __bind_key__ = 'two'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Text(), nullable=False)
    qty = db.Column(db.Integer(), nullable=False)
    price = db.Column(db.Integer(), nullable=False)

    def __repr__(self):  # I don't know why this exists but it does
        return '<Name %r>' % self.name

@app.route('/ap', methods=['GET', 'POST'])
@app.route('/addproduct')
def addProduct():
    name= None
    id = None
    qty = None
    price = None
    form = addProd()
    products= []
    error = False
    if form.validate_on_submit():
        name = form.name.data
        id = form.id.data
        qty = form.qty.data
        price = form.price.data
        form.name.data = ''
        form.id.data = 0
        form.qty.data = 0
        form.price.data = 0
        try:  # id repeated error management
            newprod= product(id=id, name= name, qty = qty, price = price)
            db.session.add(newprod)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            error = True
            db.session.rollback()
        products = product.query.order_by(product.id)

    return render_template('addproduct.html', name=name, id = id, qty = qty, price=price, form=form, products=products, error=error)


# Product add form
class addProd(FlaskForm):

    id = IntegerField('Id', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    qty = StringField('Quantity', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __repr__(self):  # I don't know why this exists but it does
        return '<Name %r>' % self.name



# login details entry form
class registrationForm(FlaskForm):

    name = StringField('Name', validators=[DataRequired()] )
    pwd= PasswordField('Password', validators=[DataRequired(), EqualTo('confirmpwd', message='Passwords do not match')])
    confirmpwd = PasswordField('Repeat Password', validators=[DataRequired()])
    mobile = StringField('Mobile Number', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[DataRequired()])
    submit= SubmitField('Submit')

# home page
@app.route("/")
@app.route('/home')
def hello_world():
    return render_template('home.html')


@app.route("/customerlist")  #list of customers
def l():
    customers = customer.query.order_by(customer.id)
    return render_template('customer list.html', customers=customers)

@app.route("/productlist")
@app.route("/pl")
def pl():
    products = product.query.order_by(product.id)
    return render_template('product list.html', products = products)

# register page
@app.route("/register", methods=['GET', 'POST'])
def register():
    name= None
    pwd=None
    confirmpwd= None
    mobile=None
    address= None
    form= registrationForm()
    if form.validate_on_submit():
        check=form.mobile.data
        if check.isdigit():  # checking if mobile number string is digits
            mobile=form.mobile.data
        elif (form.name.data == '') or ( form.pwd.data == '') or ( form.mobile.data == '') or (form.address.data == ''):

            return render_template('register.html', name=name, form=form, pwd=pwd, mobile=mobile, address=address)

        else:
            form.name.data = ''
            form.pwd.data = ''
            form.mobile.data = ''
            form.address.data = ''
            flash("Invalid mobile number entered")
            return render_template('register.html', name=name, form=form, pwd=pwd, mobile=mobile, address=address)

        name = form.name.data  # retrieving form information
        pwd = form.pwd.data
        address = form.address.data
        form.name.data = ''
        form.pwd.data = ''
        form.mobile.data = ''
        form.address.data = ''

        newcustomer = customer(name=name ,pwd= pwd, mobile =mobile, address = address)
        db.session.add(newcustomer)
        db.session.commit()

        return render_template('register.html', name=name,form=form, pwd=pwd,confirmpwd=confirmpwd, mobile= mobile, address=address)

    else:
        return render_template('register.html', name=name,form=form, pwd=pwd, mobile= mobile, address=address)

# error handler page if wrong url is entered
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')



db.create_all()
app.run(debug=True)