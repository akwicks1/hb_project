from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Favorite, Dog

import json
import requests
import xmltodict
import os

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined



pf_key=os.environ['PF_KEY'],
pf_secret=os.environ['PF_SECRET']

@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route('/results')
def show_results():
    """Search for the get request pet.find."""

    location = request.args.get("location")
    # age = request.args.get("age")
    # sex = request.args.get("sex")
    print location

    # animal = "dog"
    payload = {'key': pf_key, 'location': location}

    dog2 = requests.get('http://api.petfinder.com/pet.find?', params=payload)
    print dog2
    parse_dog2 = xmltodict.parse(dog2.text)
    
    json_dog2 = json.dumps(parse_dog2)

    print json_dog2





    return render_template("/results.html", json_dog2=json_dog2)


@app.route('/register')
def register_user():
    """Register user."""




    return render_template("/register.html")

@app.route('/register', methods=['POST'])
def register_process():
    """Process registration."""

    # Get form variables
    email = request.form["email"]
    password = request.form["password"]
    firstname = request.form["firstname"]
    lastname = request.form["lastname"]
    zipcode = request.form["zipcode"]

    # new_user = User(email=email, password=password, age=age, zipcode=zipcode)

    # db.session.add(new_user)
    # db.session.commit()

    # flash("User %s added." % email)
    # return redirect("/")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")