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
map_key=os.environ['MAP_KEY']

@app.route('/')
def index():
    """Homepage."""

    breeds = requests.get('http://api.petfinder.com/breed.list?key=9ef528dbe181850f45ad491b29f0344a&animal=dog')
    breeds_dict = xmltodict.parse(breeds.text)
    #Can pull from database/copy drop down into a file

    # db.session.add(breeds_list)
    # db.session.commit()
    return render_template("homepage.html", breeds_dict=breeds_dict)

@app.route('/map')
def show_map():
    """Show map."""

    return render_template("sample_map.html")

@app.route('/results')
def search_results():
    """Search for the get request pet.find."""

    location = request.args.get("location")
    age = request.args.get("age")
    sex = request.args.get("sex")


    animal = "dog"
    count = 1
    payload = {'key': pf_key, 'animal': animal, 'count': count, 'location': location, 'sex': sex}

    animal_response = requests.get('http://api.petfinder.com/pet.find?', params=payload)

    animal_dict = xmltodict.parse(animal_response.text)

    shelter = animal_dict['petfinder']['pets']['pet']['shelterId']

    shelter_payload = {'key': pf_key, 'id': shelter}

    shelter_location = requests.get('http://api.petfinder.com/shelter.get?', params=shelter_payload)

    shelter_dict = xmltodict.parse(shelter_location.text)

    latitude = shelter_dict['petfinder']['shelter']['latitude']
    longitude = shelter_dict['petfinder']['shelter']['longitude']

    print "This is the latitude", latitude
    print "This is the longitude", longitude

    return render_template("/results.html", animal_dict=animal_dict)

@app.route('/randomresult')
def show_random():
    """Search for a random dog."""

    location = request.args.get("location")
    age = request.args.get("age")
    sex = request.args.get("sex")

    output = "full"
    animal = "dog"
    count = 1
    payload = {'key': pf_key, 'output': output, 'animal': animal, 'count': count, 'location': location, 'sex': sex}

    animal_response = requests.get('http://api.petfinder.com/pet.getRandom?', params=payload)

    animal_dict = xmltodict.parse(animal_response.text)


    return render_template('random_result.html', animal_dict=animal_dict)

@app.route('/register')
def register_user():
    """Register user."""


    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_process():
    """Process registration."""

    # Get form variables
    email = request.form["email"]
    password = request.form["password"]
    firstname = request.form["firstname"]
    lastname = request.form["lastname"]
    zipcode = request.form["zipcode"]
    phonenumber = request.form["phonenumber"]

    new_user = User(email=email, password=password, firstname=firstname,
                    lastname=lastname, zipcode=zipcode, phonenumber=phonenumber)

    # db.session.add(new_user)
    # db.session.commit()

    flash("User %s added." % email)
    return redirect("/")

@app.route('/login', methods=['POST'])
def login_process():
    """Process login."""

    # Get form variables
    email = request.form["email"]
    password = request.form["password"]

    if not user:
        flash("No such user")
        return redirect("/login")

    if user.password != password:
        flash("Incorrect password")
        return redirect("/login")

    session["user_id"] = user.user_id

    flash("Logged in")
    return redirect("/users/%s" % user.user_id)

@app.route('/logout')
def logout():
    """Log out."""

    del session["user_id"]
    flash("Logged Out.")

    return redirect("/")



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")