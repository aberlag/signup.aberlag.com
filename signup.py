# coding: utf-8
"""
Simple flask app that shows a form asking for user details and then adds those details to a database.
"""

from flask import Flask, flash, render_template, request, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import Form, TextField, BooleanField, ValidationError

from sqlalchemy.exc import IntegrityError
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms.validators import Required, Email

# Application and config
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///signup.db'
app.config['SECRET_KEY'] = "Hello world"

# Database
db = SQLAlchemy(app)

class Member (db.Model):
	id	  = db.Column(db.Integer, primary_key=True)
	name  = db.Column(db.String(80), unique=True) #: The members name
	email = db.Column(db.String(120), unique=True) #: The members email address
	bos   = db.Column(db.String(10), unique=True) #: The members BOS number
	paid  = db.Column(db.Boolean) #: Has the member paid the membership fee?
	
	def __init__ (self, name, email, bos, paid):
		self.__dict__.update(locals())
		if self.bos == "":
			self.bos = None
		
	def __repr__ (self):
		return "<%s '%s'>" % (self.__class__.__name__, self.name)
	
class SignupForm (Form):	
	name = TextField("Name", [Required()])
	
	def validate_name (form, field):
		if Member.query.filter(Member.name == field.data).first():
			raise ValidationError("A member with this name already exists")
	
	email = TextField("Email", [Required(), Email()], default="@aber.ac.uk")
	
	def validate_email (form, field):
		if Member.query.filter(Member.email == field.data).first():
			raise ValidationError("A member with this email already exists")
		
	bos = TextField("BOS Number")
	
	def validate_bos (form, field):
		if Member.query.filter(Member.bos == field.data).first():
			raise ValidationError("A member with this BOS number already exists")
	
	paid = BooleanField("Paid", description="The membership fee is &pound;3 - pay now?")

@app.route("/", methods=['GET', 'POST'])
def signup ():
	form = SignupForm(request.form)
	if form.validate_on_submit():
		member = Member(**form.data)
		db.session.add(member)
		try:
			db.session.commit()
			flash("'%s' has been signed up. Welcome to AberLAG." % member.name)
			form = SignupForm()
		except IntegrityError:
			flash("This name, email or bos number has already been used to sign up.")
	return render_template("signup.html", form=form)

@app.route("/list")
def list ():
	members = Member.query.all()
	count = len(members)
	return render_template("list.html", **locals())

@app.route("/edit/<id>", methods=['GET', 'POST'])
def edit (id):
	member = Member.query.filter_by(id=id).first()
	form = SignupForm(request.form, obj=member)
	if form.validate_on_submit():
		form.populate_obj(member)
		db.session.add(member)
		db.session.commit()
		flash("Member '%s' has been updated." % member.name)
		return redirect(url_for("list"))
	return render_template("signup.html", form=form)

if __name__ == "__main__":
	db.create_all()
	app.run(debug=True, host='0.0.0.0')
