from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from forms import UserForm, FactForm
from models import connect_db, db, User, Fact
from sqlalchemy.exc import IntegrityError
import requests 
import json


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql:///number_db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config['SECRET_KEY'] = "pingann39"
# app.config['WTF_CSRF_SECRET_KEY'] = "secretkey"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
toolbar = DebugToolbarExtension(app)


connect_db(app)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login_user():
        form = UserForm()
        if form.validate_on_submit():
                name = form.username.data
                pwd = form.password.data
                user = User.authenticate(name, pwd)
                if user:
                        session['user_id'] = user.id
                        return redirect('/facts')
                else:
                        form.username.errors = ['Invalid Username/Password'] 

        return render_template("login.html", form=form)   


@app.route('/register', methods=['GET', 'POST'])
def register_user():
        form = UserForm()
        if form.validate_on_submit():
                username = form.username.data
                password = form.password.data
                new_user = User.register(username, password)

                db.session.add(new_user)
                try:
                        db.session.commit()
                except IntegrityError:
                        form.username.errors.append('Username was taken. Please pick anoter')
                        return render_template('register.html', form=form)
                session['user_id'] = new_user.id
                flash('Welcome! YOu created new account!', 'success')
                return redirect('/facts') 

        return render_template('register.html', form=form ) 


@app.route('/facts', methods=['GET', 'POST']) 
def show_facts():
        form = FactForm()
        res = requests.get('https://cat-fact.herokuapp.com/facts')
        data = res.content
        all_facts = Fact.query.all()
        if form.validate_on_submit():

                text = form.text.data
                new_fact = Fact(text=text, user_id=session['user_id'])
                db.session.add(new_fact)
                db.session.commit()
                flash('New Fact Created!', 'success')
                return redirect('/facts')

        return render_template("facts.html", form=form, data=data, facts=all_facts)
        

@app.route('/facts/<int:id>', methods=["POST"])
def delete_fact(id):
        fact = Fact.query.get_or_404(id)
        if fact.user_id == session['user_id']:
                db.session.delete(fact)
                db.session.commit()
                flash("Fact deleted!", "info")
                return redirect('/facts')
        return redirect('/facts')


@app.route('/logout')
def logout_user():
    session.pop('user_id')
    flash("Goodbye!", "info")
    return redirect('/')
