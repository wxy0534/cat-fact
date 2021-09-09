from flask import Flask, render_template, redirect, request, flash, session, jsonify, g
from flask_debugtoolbar import DebugToolbarExtension
from forms import UserForm, FactForm
from models import connect_db, db, User, Fact
from sqlalchemy.exc import IntegrityError
import requests 
import json
import os


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL','postgresql:///number_db')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY','pingann39')
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
toolbar = DebugToolbarExtension(app)


connect_db(app)
CURR_USER_KEY='user_id'

@app.before_request
def add_user_to_g():
        """If we're logged in, add curr user to Flask global."""
        if CURR_USER_KEY in session:
                g.user = User.query.get(session[CURR_USER_KEY])
        else:
                g.user = None
def do_login(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]



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
                        flash("success")
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
                

                #db.session.add(new_user)
                try:
                        new_user = User.register(username, password)
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
        res = requests.get('https://catfact.ninja/facts')
        json = res.json()
               
        user_facts = None
        if g.user:
                user = User.query.get_or_404(g.user.id)
                user_facts = (Fact.query.filter(Fact.user_id == g.user.id).limit(15).all())
        
        return render_template("facts.html", form=form, user_facts=user_facts, ext_facts=json['data'])


@app.route('/facts/new', methods=["GET", "POST"])
def facts_add():
        if not g.user:
                flash("Access Denied!", "danger")
                return redirect("/login")

        form = FactForm()
        
        if form.validate_on_submit():
                
                msg = Fact(text=form.text.data)                
                g.user.facts.append(msg)
                db.session.commit()

                return redirect("/facts")
        
        return render_template('facts.html', form=form)


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
